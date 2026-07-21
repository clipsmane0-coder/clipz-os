from typing import Optional, List, Tuple

from app.repositories.repositories import (
    ProfileRepository, SourceRepository, CandidateRepository,
    JobRepository, NotificationRepository, SettingsRepository,
)
from app.models import Profile, Source, Candidate, Job, Notification


class HealthService:
    async def check(self) -> dict:
        return {
            "api": True,
            "database": True,
            "version": "0.1.0",
        }


class ProfileService:
    def __init__(self, repo: ProfileRepository):
        self.repo = repo

    async def list(self, page: int = 1, page_size: int = 25,
                   status: Optional[str] = None,
                   profile_type: Optional[str] = None) -> Tuple[List[Profile], int]:
        return await self.repo.list(page, page_size, status, profile_type)

    async def get(self, profile_id: str) -> Optional[Profile]:
        return await self.repo.get_by_id(profile_id)

    async def create(self, data: dict) -> Profile:
        if not data.get("slug"):
            data["slug"] = data["name"].lower().replace(" ", "-")
        return await self.repo.create(data)

    async def update(self, profile_id: str, data: dict) -> Optional[Profile]:
        return await self.repo.update(profile_id, data)

    async def delete(self, profile_id: str) -> bool:
        return await self.repo.delete(profile_id)

    async def update_status(self, profile_id: str, status: str) -> Optional[Profile]:
        valid = {"active", "paused", "archived"}
        if status not in valid:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid}")
        return await self.repo.update(profile_id, {"status": status})


class SourceService:
    def __init__(self, repo: SourceRepository):
        self.repo = repo

    async def list(self, page: int = 1, page_size: int = 25,
                   status: Optional[str] = None,
                   profile_id: Optional[str] = None) -> Tuple[List[Source], int]:
        return await self.repo.list(page, page_size, status, profile_id)

    async def get(self, source_id: str) -> Optional[Source]:
        return await self.repo.get_by_id(source_id)

    async def create(self, data: dict) -> Source:
        if "status" not in data:
            data["status"] = "new"
        return await self.repo.create(data)

    async def update(self, source_id: str, data: dict) -> Optional[Source]:
        return await self.repo.update(source_id, data)

    async def archive(self, source_id: str) -> Optional[Source]:
        return await self.repo.update(source_id, {"status": "archived"})


class CandidateService:
    def __init__(self, repo: CandidateRepository):
        self.repo = repo

    async def list(self, page: int = 1, page_size: int = 25,
                   approval_status: Optional[str] = None,
                   profile_id: Optional[str] = None,
                   source_id: Optional[str] = None,
                   min_score: Optional[float] = None) -> Tuple[List[Candidate], int]:
        return await self.repo.list(page, page_size, approval_status, profile_id, source_id, min_score)

    async def get(self, candidate_id: str) -> Optional[Candidate]:
        return await self.repo.get_by_id(candidate_id)

    async def create(self, data: dict) -> Candidate:
        return await self.repo.create(data)

    async def update(self, candidate_id: str, data: dict) -> Optional[Candidate]:
        return await self.repo.update(candidate_id, data)

    async def update_approval(self, candidate_id: str, status: str) -> Optional[Candidate]:
        valid = {"pending", "approved", "rejected", "needs_changes", "archived"}
        if status not in valid:
            raise ValueError(f"Invalid approval status: {status}")
        current = await self.repo.get_by_id(candidate_id)
        if not current:
            return None
        # Validate transitions
        if current.approval_status == "archived":
            raise ValueError("Cannot change status of an archived candidate")
        if current.approval_status == "approved" and status not in ("archived",):
            raise ValueError("Approved candidates can only transition to archived")
        return await self.repo.update(candidate_id, {"approval_status": status})


class JobService:
    def __init__(self, repo: JobRepository):
        self.repo = repo

    async def list(self, page: int = 1, page_size: int = 25,
                   status: Optional[str] = None,
                   job_type: Optional[str] = None,
                   profile_id: Optional[str] = None) -> Tuple[List[Job], int]:
        return await self.repo.list(page, page_size, status, job_type, profile_id)

    async def get(self, job_id: str) -> Optional[Job]:
        return await self.repo.get_by_id(job_id)

    async def create(self, data: dict) -> Job:
        if "status" not in data:
            data["status"] = "pending"
        return await self.repo.create(data)

    async def update_status(self, job_id: str, new_status: str) -> Optional[Job]:
        valid = {"pending", "queued", "running", "paused", "retrying", "completed", "failed", "cancelled"}
        if new_status not in valid:
            raise ValueError(f"Invalid job status: {new_status}")
        return await self.repo.update(job_id, {"status": new_status})

    async def retry(self, job_id: str) -> Optional[Job]:
        job = await self.repo.get_by_id(job_id)
        if not job:
            return None
        if not job.retryable:
            raise ValueError("This job is not retryable")
        if job.attempts >= job.max_attempts:
            raise ValueError(f"Max attempts ({job.max_attempts}) reached")
        return await self.repo.update(job_id, {
            "status": "queued",
            "attempts": job.attempts + 1,
            "error_code": None,
            "error_message": None,
        })


class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def list(self, page: int = 1, page_size: int = 25,
                   unread_only: bool = False) -> Tuple[List[Notification], int]:
        return await self.repo.list(page, page_size, unread_only)

    async def mark_read(self, notification_id: str) -> bool:
        return await self.repo.mark_read(notification_id)


class SettingsService:
    def __init__(self, repo: SettingsRepository):
        self.repo = repo

    async def get_all(self) -> list:
        settings = await self.repo.get_all()
        return [
            {"key": s.key, "value": s.value, "value_type": s.value_type,
             "description": s.description, "updated_at": s.updated_at.isoformat()}
            for s in settings
        ]

    async def update(self, key: str, value: str) -> dict:
        setting = await self.repo.set(key, value)
        return {"key": setting.key, "value": setting.value, "value_type": setting.value_type,
                "description": setting.description, "updated_at": setting.updated_at.isoformat()}

    async def get_profile_settings(self, profile_id: str) -> list:
        settings = await self.repo.get_profile_settings(profile_id)
        return [
            {"id": s.id, "profile_id": s.profile_id, "key": s.key, "value": s.value,
             "value_type": s.value_type, "updated_at": s.updated_at.isoformat()}
            for s in settings
        ]

    async def set_profile_setting(self, profile_id: str, key: str, value: str) -> dict:
        setting = await self.repo.set_profile_setting(profile_id, key, value)
        return {"id": setting.id, "profile_id": setting.profile_id, "key": setting.key,
                "value": setting.value, "value_type": setting.value_type,
                "updated_at": setting.updated_at.isoformat()}