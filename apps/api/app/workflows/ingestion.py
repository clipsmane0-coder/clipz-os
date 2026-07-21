"""Source Ingestion Workflow — Phase 4B operational.

Coordinates profile validation, upload validation, streaming storage,
checksum calculation, duplicate detection, source record creation,
FFprobe inspection, thumbnail extraction, and analysis job creation.

Compensates for partial failure at every step.
"""

import os
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import utcnow
from app.models import Source, Job
from app.repositories.repositories import (
    ProfileRepository, SourceRepository, JobRepository,
)
from app.adapters.storage import (
    LocalStorageAdapter, calculate_sha256, generate_storage_key,
    sanitize_filename, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES,
)
from app.adapters.media import FFprobeMediaInspector, ThumbnailExtractor
from app.core.state_machine import JOB_STATUS_QUEUED, JOB_STATUS_PENDING

logger = logging.getLogger("clipz")


class IngestionError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400,
                 details: dict = None, retryable: bool = False):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.retryable = retryable
        super().__init__(message)


class SourceIngestionWorkflow:
    """Operational ingestion pipeline. Every step is compensated on failure."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_repo = ProfileRepository(db)
        self.source_repo = SourceRepository(db)
        self.job_repo = JobRepository(db)
        self.storage = LocalStorageAdapter()
        self.inspector = FFprobeMediaInspector()
        self.thumbnailer = ThumbnailExtractor()
        self.stored_keys: list[str] = []
        self.created_source_id: Optional[str] = None
        self.created_job_id: Optional[str] = None

    async def run_upload(
        self,
        profile_id: str,
        file_data: bytes,
        filename: str,
        title: Optional[str] = None,
        rights_status: str = "unknown",
    ) -> dict:
        """Execute the full upload ingestion pipeline."""
        try:
            return await self._run(profile_id, file_data, filename, title, rights_status)
        except IngestionError:
            raise
        except Exception as e:
            logger.error(f"Ingestion unexpected error: {e}", exc_info=True)
            raise IngestionError("INTERNAL_ERROR", "An unexpected error occurred during ingestion.",
                                  status_code=500, retryable=True)

    async def _run(self, profile_id: str, file_data: bytes, filename: str,
                   title: Optional[str], rights_status: str) -> dict:
        # Step 1: Validate profile
        profile = await self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise IngestionError("PROFILE_NOT_FOUND", "The requested profile does not exist.",
                                  status_code=404)

        # Step 2: Validate file
        clean_name = sanitize_filename(filename)
        ext = os.path.splitext(clean_name)[1].lower()
        if not ext or ext not in ALLOWED_EXTENSIONS:
            raise IngestionError("UNSUPPORTED_FILE_TYPE",
                                  f"Extension '{ext}' is not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

        if len(file_data) == 0:
            raise IngestionError("EMPTY_FILE", "Uploaded file is empty.")

        if len(file_data) > MAX_UPLOAD_SIZE_BYTES:
            raise IngestionError("FILE_TOO_LARGE",
                                  f"File exceeds maximum size of {MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB.")

        # Step 3: Calculate checksum
        checksum = calculate_sha256(file_data)

        # Step 4: Duplicate check
        existing = await self._find_duplicate_by_checksum(checksum)
        if existing:
            raise IngestionError("DUPLICATE_SOURCE",
                                  "A source with identical content already exists.",
                                  status_code=409,
                                  details={"existing_source_id": existing.id})

        # Step 5: Write to storage
        storage_key = generate_storage_key("sources", ext)
        try:
            storage_path = await self.storage.save(storage_key, file_data)
            self.stored_keys.append(storage_key)
        except Exception as e:
            raise IngestionError("STORAGE_WRITE_FAILED", f"Failed to write file to storage: {e}",
                                  status_code=500, retryable=True)

        # Step 6: Create source record
        source_title = title or clean_name or "Untitled upload"
        source_data = {
            "profile_id": profile_id,
            "title": source_title,
            "source_type": "upload",
            "source_kind": "video",
            "original_filename": clean_name,
            "storage_key": storage_key,
            "mime_type": self._guess_mime(ext),
            "extension": ext,
            "checksum_sha256": checksum,
            "file_hash": checksum,
            "file_size_bytes": len(file_data),
            "rights_status": rights_status,
            "status": "validating",
            "inspection_status": "pending",
        }
        try:
            source = await self.source_repo.create(source_data)
            self.created_source_id = source.id
        except Exception as e:
            # Compensation: remove stored file
            await self._cleanup_storage()
            raise IngestionError("DATABASE_ERROR", f"Failed to create source record: {e}",
                                  status_code=500, retryable=True)

        # Step 7: FFprobe inspection
        inspection_result = None
        try:
            inspection_result = await self.inspector.inspect(storage_path)
            # Update source with inspection data
            await self.source_repo.update(source.id, {
                "duration_ms": inspection_result["duration_ms"],
                "width": inspection_result["width"],
                "height": inspection_result["height"],
                "frame_rate": inspection_result["frame_rate"],
                "video_codec": inspection_result["video_codec"],
                "audio_codec": inspection_result["audio_codec"],
                "audio_channels": inspection_result["audio_channels"],
                "audio_sample_rate": inspection_result["audio_sample_rate"],
                "bitrate": inspection_result.get("bitrate", 0),
                "container_format": inspection_result.get("container_format", ""),
                "inspection_status": "completed",
                "inspected_at": utcnow(),
                "status": "completed",
            })
        except Exception as e:
            # Compensation: mark inspection failed, preserve source
            error_msg = str(e)[:500]
            await self.source_repo.update(source.id, {
                "inspection_status": "failed",
                "inspection_error": error_msg,
                "status": "failed",
            })
            # Don't raise — preserve the source record for retry
            return {
                "source_id": source.id,
                "storage_key": storage_key,
                "checksum_sha256": checksum,
                "file_size_bytes": len(file_data),
                "inspection_status": "failed",
                "inspection_error": error_msg,
                "job_id": None,
                "status": "inspection_failed",
            }

        # Step 8: Thumbnail extraction
        thumbnail_key = None
        try:
            thumb_ext = ".jpg"
            thumbnail_key = generate_storage_key("thumbnails", thumb_ext)
            thumb_path = self.storage.resolve_path(thumbnail_key)
            success = await self.thumbnailer.extract(storage_path, thumb_path)
            if success:
                await self.source_repo.update(source.id, {
                    "thumbnail_storage_key": thumbnail_key,
                })
                self.stored_keys.append(thumbnail_key)
        except Exception as e:
            logger.warning(f"Thumbnail extraction failed (non-fatal): {e}")

        # Step 9: Create analysis job
        job_id = None
        try:
            job_data = {
                "job_type": "analyze_source",
                "entity_type": "source",
                "entity_id": source.id,
                "profile_id": profile_id,
                "priority": "normal",
                "status": JOB_STATUS_PENDING,
                "payload_json": {"source_id": source.id, "checksum": checksum},
            }
            job = await self.job_repo.create(job_data)
            self.created_job_id = job.id
            # Queue the job
            await self.job_repo.update(job.id, {"status": JOB_STATUS_QUEUED})
            job_id = job.id
        except Exception as e:
            logger.warning(f"Analysis job creation failed (non-fatal): {e}")

        return {
            "source_id": source.id,
            "storage_key": storage_key,
            "checksum_sha256": checksum,
            "file_size_bytes": len(file_data),
            "inspection_status": "completed",
            "thumbnail_key": thumbnail_key,
            "job_id": job_id,
            "job_status": "queued" if job_id else None,
            "status": "completed",
        }

    async def _find_duplicate_by_checksum(self, checksum: str) -> Optional[Source]:
        """Check for existing source with the same checksum across all profiles."""
        from sqlalchemy import select
        from app.models import Source
        result = await self.db.execute(
            select(Source).where(Source.checksum_sha256 == checksum).limit(1)
        )
        return result.scalar_one_or_none()

    async def _cleanup_storage(self):
        """Remove all stored files on failure."""
        for key in self.stored_keys:
            try:
                await self.storage.delete(key)
            except Exception:
                pass

    def _guess_mime(self, ext: str) -> str:
        mime_map = {
            ".mp4": "video/mp4", ".mov": "video/quicktime",
            ".avi": "video/x-msvideo", ".mkv": "video/x-matroska",
            ".webm": "video/webm", ".flv": "video/x-flv",
            ".wmv": "video/x-ms-wmv", ".m4v": "video/mp4",
            ".mpg": "video/mpeg", ".mpeg": "video/mpeg",
        }
        return mime_map.get(ext, "application/octet-stream")


class SourceValidationWorkflow:
    """Validates source metadata before processing."""

    async def validate_upload(self, filename: str, file_size: int, file_data: bytes) -> dict:
        clean_name = sanitize_filename(filename)
        ext = os.path.splitext(clean_name)[1].lower()
        errors = []
        if not ext:
            errors.append("File has no extension")
        if ext not in ALLOWED_EXTENSIONS:
            errors.append(f"Extension '{ext}' not allowed")
        if file_size == 0:
            errors.append("File is empty")
        if file_size > MAX_UPLOAD_SIZE_BYTES:
            errors.append("File exceeds maximum size")
        return {"valid": len(errors) == 0, "errors": errors, "clean_name": clean_name, "ext": ext}


class SourceInspectionWorkflow:
    """Inspects source media metadata."""

    def __init__(self):
        self.inspector = FFprobeMediaInspector()

    async def inspect(self, file_path: str) -> dict:
        return await self.inspector.inspect(file_path)


class AnalysisJobCreationWorkflow:
    """Creates a durable analysis job for a source."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)

    async def create(self, source_id: str, profile_id: str, checksum: str) -> Optional[Job]:
        """Create and queue an analysis job. Prevents duplicates."""
        from sqlalchemy import select, and_
        from app.models import Job
        # Check for existing active analysis job for this source
        existing = await self.db.execute(
            select(Job).where(
                and_(
                    Job.entity_type == "source",
                    Job.entity_id == source_id,
                    Job.job_type == "analyze_source",
                    Job.status.in_(["pending", "queued", "running"]),
                )
            )
        )
        if existing.scalar_one_or_none():
            return None  # Job already exists
        job_data = {
            "job_type": "analyze_source",
            "entity_type": "source",
            "entity_id": source_id,
            "profile_id": profile_id,
            "priority": "normal",
            "status": JOB_STATUS_PENDING,
            "payload_json": {"source_id": source_id, "checksum": checksum},
        }
        job = await self.job_repo.create(job_data)
        await self.job_repo.update(job.id, {"status": JOB_STATUS_QUEUED})
        return job