import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.services import (
    HealthService, ProfileService, SourceService,
    CandidateService, JobService, NotificationService, SettingsService,
)
from app.repositories.repositories import (
    ProfileRepository, SourceRepository, CandidateRepository,
    JobRepository, NotificationRepository, SettingsRepository,
)
from app.schemas.schemas import (
    ApiMeta, ApiResponse, PaginatedMeta, PaginatedResponse,
    ApiError, ApiErrorResponse, ProfileCreate, ProfileUpdate,
    ProfileResponse, SourceCreate, SourceUpdate, SourceResponse,
    CandidateCreate, CandidateUpdate, CandidateResponse,
    JobCreate, JobResponse, NotificationResponse,
    SettingsResponse, SettingsUpdate,
)

router = APIRouter(prefix="/api/v1")


def get_meta(request: Request) -> ApiMeta:
    return ApiMeta(request_id=getattr(request.state, "request_id", str(uuid.uuid4())))


def paginated_meta(request: Request, page: int, page_size: int, total: int) -> PaginatedMeta:
    return PaginatedMeta(page=page, page_size=page_size, total=total,
                          request_id=getattr(request.state, "request_id", str(uuid.uuid4())))


def error(code: str, message: str, details: dict = None,
          retryable: bool = False, status_code: int = 400):
    raise HTTPException(
        status_code=status_code,
        detail=ApiErrorResponse(
            error=ApiError(code=code, message=message, details=details or {}, retryable=retryable),
            meta=ApiMeta(request_id=""),
        ).model_dump(),
    )


def validate_uuid(id_str: str, name: str = "id"):
    try:
        uuid.UUID(id_str)
    except ValueError:
        error(f"INVALID_{name.upper()}", f"Invalid {name} format: {id_str}",
              status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY)


# ============================================================
# HEALTH
# ============================================================
@router.get("/health")
async def health_check(request: Request):
    service = HealthService()
    result = await service.check()
    return ApiResponse(data=result, meta=get_meta(request))


# ============================================================
# PROFILES
# ============================================================
@router.get("/profiles")
async def list_profiles(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    profile_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    service = ProfileService(ProfileRepository(db))
    data, total = await service.list(page, page_size, status, profile_type)
    return PaginatedResponse(data=[ProfileResponse.model_validate(p) for p in data],
                              meta=paginated_meta(request, page, page_size, total))


@router.post("/profiles", status_code=http_status.HTTP_201_CREATED)
async def create_profile(request: Request, body: ProfileCreate, db: AsyncSession = Depends(get_db)):
    service = ProfileService(ProfileRepository(db))
    data = await service.create(body.model_dump(exclude_unset=True))
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


@router.get("/profiles/{profile_id}")
async def get_profile(request: Request, profile_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    data = await service.get(profile_id)
    if not data:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


@router.patch("/profiles/{profile_id}")
async def update_profile(request: Request, profile_id: str, body: ProfileUpdate,
                          db: AsyncSession = Depends(get_db)):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    data = await service.update(profile_id, body.model_dump(exclude_unset=True))
    if not data:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


@router.delete("/profiles/{profile_id}")
async def delete_profile(request: Request, profile_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    deleted = await service.delete(profile_id)
    if not deleted:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data={"deleted": True}, meta=get_meta(request))


@router.post("/profiles/{profile_id}/pause")
async def pause_profile(request: Request, profile_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    try:
        data = await service.update_status(profile_id, "paused")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


@router.post("/profiles/{profile_id}/resume")
async def resume_profile(request: Request, profile_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    try:
        data = await service.update_status(profile_id, "active")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


@router.post("/profiles/{profile_id}/archive")
async def archive_profile(request: Request, profile_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    try:
        data = await service.update_status(profile_id, "archived")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


# ============================================================
# SOURCES
# ============================================================
@router.get("/sources")
async def list_sources(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    profile_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    service = SourceService(SourceRepository(db))
    data, total = await service.list(page, page_size, status, profile_id)
    return PaginatedResponse(data=[SourceResponse.model_validate(s) for s in data],
                              meta=paginated_meta(request, page, page_size, total))


@router.post("/sources", status_code=http_status.HTTP_201_CREATED)
async def create_source(request: Request, body: SourceCreate, db: AsyncSession = Depends(get_db)):
    service = SourceService(SourceRepository(db))
    data = await service.create(body.model_dump(exclude_unset=True))
    return ApiResponse(data=SourceResponse.model_validate(data), meta=get_meta(request))


@router.get("/sources/{source_id}")
async def get_source(request: Request, source_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(source_id, "source_id")
    service = SourceService(SourceRepository(db))
    data = await service.get(source_id)
    if not data:
        error("SOURCE_NOT_FOUND", "The requested source does not exist.", status_code=404)
    return ApiResponse(data=SourceResponse.model_validate(data), meta=get_meta(request))


@router.patch("/sources/{source_id}")
async def update_source(request: Request, source_id: str, body: SourceUpdate,
                         db: AsyncSession = Depends(get_db)):
    validate_uuid(source_id, "source_id")
    service = SourceService(SourceRepository(db))
    data = await service.update(source_id, body.model_dump(exclude_unset=True))
    if not data:
        error("SOURCE_NOT_FOUND", "The requested source does not exist.", status_code=404)
    return ApiResponse(data=SourceResponse.model_validate(data), meta=get_meta(request))


@router.delete("/sources/{source_id}")
async def delete_source(request: Request, source_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(source_id, "source_id")
    service = SourceService(SourceRepository(db))
    data = await service.get(source_id)
    if not data:
        error("SOURCE_NOT_FOUND", "The requested source does not exist.", status_code=404)
    await service.archive(source_id)
    return ApiResponse(data={"deleted": True}, meta=get_meta(request))


@router.post("/sources/{source_id}/archive")
async def archive_source(request: Request, source_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(source_id, "source_id")
    service = SourceService(SourceRepository(db))
    data = await service.archive(source_id)
    if not data:
        error("SOURCE_NOT_FOUND", "The requested source does not exist.", status_code=404)
    return ApiResponse(data=SourceResponse.model_validate(data), meta=get_meta(request))


# ============================================================
# CANDIDATES
# ============================================================
@router.get("/candidates")
async def list_candidates(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    approval_status: Optional[str] = None,
    profile_id: Optional[str] = None,
    source_id: Optional[str] = None,
    min_score: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
):
    service = CandidateService(CandidateRepository(db))
    data, total = await service.list(page, page_size, approval_status, profile_id, source_id, min_score)
    return PaginatedResponse(data=[CandidateResponse.model_validate(c) for c in data],
                              meta=paginated_meta(request, page, page_size, total))


@router.post("/candidates", status_code=http_status.HTTP_201_CREATED)
async def create_candidate(request: Request, body: CandidateCreate,
                            db: AsyncSession = Depends(get_db)):
    service = CandidateService(CandidateRepository(db))
    data = await service.create(body.model_dump(exclude_unset=True))
    return ApiResponse(data=CandidateResponse.model_validate(data), meta=get_meta(request))


@router.get("/candidates/{candidate_id}")
async def get_candidate(request: Request, candidate_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(candidate_id, "candidate_id")
    service = CandidateService(CandidateRepository(db))
    data = await service.get(candidate_id)
    if not data:
        error("CANDIDATE_NOT_FOUND", "The requested candidate does not exist.", status_code=404)
    return ApiResponse(data=CandidateResponse.model_validate(data), meta=get_meta(request))


@router.patch("/candidates/{candidate_id}")
async def update_candidate(request: Request, candidate_id: str, body: CandidateUpdate,
                            db: AsyncSession = Depends(get_db)):
    validate_uuid(candidate_id, "candidate_id")
    service = CandidateService(CandidateRepository(db))
    data = await service.update(candidate_id, body.model_dump(exclude_unset=True))
    if not data:
        error("CANDIDATE_NOT_FOUND", "The requested candidate does not exist.", status_code=404)
    return ApiResponse(data=CandidateResponse.model_validate(data), meta=get_meta(request))


@router.post("/candidates/{candidate_id}/approve")
async def approve_candidate(request: Request, candidate_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(candidate_id, "candidate_id")
    service = CandidateService(CandidateRepository(db))
    try:
        data = await service.update_approval(candidate_id, "approved")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("CANDIDATE_NOT_FOUND", "The requested candidate does not exist.", status_code=404)
    return ApiResponse(data=CandidateResponse.model_validate(data), meta=get_meta(request))


@router.post("/candidates/{candidate_id}/reject")
async def reject_candidate(request: Request, candidate_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(candidate_id, "candidate_id")
    service = CandidateService(CandidateRepository(db))
    try:
        data = await service.update_approval(candidate_id, "rejected")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("CANDIDATE_NOT_FOUND", "The requested candidate does not exist.", status_code=404)
    return ApiResponse(data=CandidateResponse.model_validate(data), meta=get_meta(request))


@router.post("/candidates/{candidate_id}/archive")
async def archive_candidate(request: Request, candidate_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(candidate_id, "candidate_id")
    service = CandidateService(CandidateRepository(db))
    try:
        data = await service.update_approval(candidate_id, "archived")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("CANDIDATE_NOT_FOUND", "The requested candidate does not exist.", status_code=404)
    return ApiResponse(data=CandidateResponse.model_validate(data), meta=get_meta(request))


# ============================================================
# JOBS
# ============================================================
@router.get("/jobs")
async def list_jobs(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    profile_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    service = JobService(JobRepository(db))
    data, total = await service.list(page, page_size, status, job_type, profile_id)
    return PaginatedResponse(data=[JobResponse.model_validate(j) for j in data],
                              meta=paginated_meta(request, page, page_size, total))


@router.post("/jobs", status_code=http_status.HTTP_201_CREATED)
async def create_job(request: Request, body: JobCreate, db: AsyncSession = Depends(get_db)):
    service = JobService(JobRepository(db))
    data = await service.create(body.model_dump(exclude_unset=True))
    return ApiResponse(data=JobResponse.model_validate(data), meta=get_meta(request))


@router.get("/jobs/{job_id}")
async def get_job(request: Request, job_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(job_id, "job_id")
    service = JobService(JobRepository(db))
    data = await service.get(job_id)
    if not data:
        error("JOB_NOT_FOUND", "The requested job does not exist.", status_code=404)
    return ApiResponse(data=JobResponse.model_validate(data), meta=get_meta(request))


@router.post("/jobs/{job_id}/retry")
async def retry_job(request: Request, job_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(job_id, "job_id")
    service = JobService(JobRepository(db))
    try:
        data = await service.retry(job_id)
    except ValueError as e:
        error("JOB_RETRY_FAILED", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("JOB_NOT_FOUND", "The requested job does not exist.", status_code=404)
    return ApiResponse(data=JobResponse.model_validate(data), meta=get_meta(request))


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(request: Request, job_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(job_id, "job_id")
    service = JobService(JobRepository(db))
    try:
        data = await service.update_status(job_id, "cancelled")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("JOB_NOT_FOUND", "The requested job does not exist.", status_code=404)
    return ApiResponse(data=JobResponse.model_validate(data), meta=get_meta(request))


@router.post("/jobs/{job_id}/pause")
async def pause_job(request: Request, job_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(job_id, "job_id")
    service = JobService(JobRepository(db))
    try:
        data = await service.update_status(job_id, "paused")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("JOB_NOT_FOUND", "The requested job does not exist.", status_code=404)
    return ApiResponse(data=JobResponse.model_validate(data), meta=get_meta(request))


@router.post("/jobs/{job_id}/resume")
async def resume_job(request: Request, job_id: str, db: AsyncSession = Depends(get_db)):
    validate_uuid(job_id, "job_id")
    service = JobService(JobRepository(db))
    try:
        data = await service.update_status(job_id, "queued")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("JOB_NOT_FOUND", "The requested job does not exist.", status_code=404)
    return ApiResponse(data=JobResponse.model_validate(data), meta=get_meta(request))


# ============================================================
# SETTINGS
# ============================================================
@router.get("/settings")
async def get_settings(request: Request, db: AsyncSession = Depends(get_db)):
    service = SettingsService(SettingsRepository(db))
    data = await service.get_all()
    return ApiResponse(data=data, meta=get_meta(request))


@router.patch("/settings")
async def update_setting(request: Request, body: SettingsUpdate,
                          db: AsyncSession = Depends(get_db)):
    service = SettingsService(SettingsRepository(db))
    data = await service.update(body.key, body.value)
    return ApiResponse(data=data, meta=get_meta(request))


@router.get("/profiles/{profile_id}/settings")
async def get_profile_settings(request: Request, profile_id: str,
                                db: AsyncSession = Depends(get_db)):
    validate_uuid(profile_id, "profile_id")
    service = SettingsService(SettingsRepository(db))
    data = await service.get_profile_settings(profile_id)
    return ApiResponse(data=data, meta=get_meta(request))


@router.patch("/profiles/{profile_id}/settings")
async def update_profile_setting(request: Request, profile_id: str,
                                  body: SettingsUpdate,
                                  db: AsyncSession = Depends(get_db)):
    validate_uuid(profile_id, "profile_id")
    service = SettingsService(SettingsRepository(db))
    data = await service.set_profile_setting(profile_id, body.key, body.value)
    return ApiResponse(data=data, meta=get_meta(request))


# ============================================================
# NOTIFICATIONS
# ============================================================
@router.get("/notifications")
async def list_notifications(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    service = NotificationService(NotificationRepository(db))
    data, total = await service.list(page, page_size, unread_only)
    return PaginatedResponse(data=[NotificationResponse.model_validate(n) for n in data],
                              meta=paginated_meta(request, page, page_size, total))


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(request: Request, notification_id: str,
                                  db: AsyncSession = Depends(get_db)):
    validate_uuid(notification_id, "notification_id")
    service = NotificationService(NotificationRepository(db))
    result = await service.mark_read(notification_id)
    if not result:
        error("NOTIFICATION_NOT_FOUND", "The requested notification does not exist.", status_code=404)
    return ApiResponse(data={"read": True}, meta=get_meta(request))


# ============================================================
# EXCEPTION HANDLER
# ============================================================
@router.get("/profiles/{profile_id}/pause", include_in_schema=False)
@router.get("/profiles/{profile_id}/resume", include_in_schema=False)
@router.get("/profiles/{profile_id}/archive", include_in_schema=False)
@router.get("/sources/{source_id}/archive", include_in_schema=False)
@router.get("/candidates/{candidate_id}/approve", include_in_schema=False)
@router.get("/candidates/{candidate_id}/reject", include_in_schema=False)
@router.get("/candidates/{candidate_id}/archive", include_in_schema=False)
@router.get("/jobs/{job_id}/retry", include_in_schema=False)
@router.get("/jobs/{job_id}/cancel", include_in_schema=False)
@router.get("/jobs/{job_id}/pause", include_in_schema=False)
@router.get("/jobs/{job_id}/resume", include_in_schema=False)
async def method_not_allowed():
    raise HTTPException(status_code=http_status.HTTP_405_METHOD_NOT_ALLOWED,
                         detail="Use POST for this action")