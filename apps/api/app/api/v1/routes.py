import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status as http_status, UploadFile, File
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
    ProfileResponse, SourceCreate, SourceUpdate, SourceRegisterUrl, SourceResponse,
    CandidateCreate, CandidateUpdate, CandidateResponse,
    JobCreate, JobResponse, NotificationResponse,
    SettingsUpdate, DashboardOverview, ScheduleCreate, ScheduleUpdate,
    ScheduleResponse, AnalyticsOverview,
)
from app.workflows.ingestion import SourceIngestionWorkflow, IngestionError
from app.auth.dependencies import get_current_user
from app.models.models import User

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
# HEALTH (public)
# ============================================================
@router.get("/health")
async def health_check(request: Request):
    service = HealthService()
    result = await service.check()
    return ApiResponse(data=result, meta=get_meta(request))


# ============================================================
# DASHBOARD (authenticated)
# ============================================================
@router.get("/dashboard/overview")
async def dashboard_overview(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import select, func
    from app.models.models import Profile, Source, Candidate, Job

    # Count profiles
    profile_count = await db.scalar(select(func.count(Profile.id)).where(Profile.user_id == current_user.id))
    profile_count = profile_count or 0

    # Get profile IDs for this user
    profile_rows = await db.execute(select(Profile.id).where(Profile.user_id == current_user.id))
    profile_ids = [row[0] for row in profile_rows]

    source_count = 0
    candidate_count = 0
    job_count = 0
    active_jobs = 0
    completed_jobs = 0
    failed_jobs = 0

    if profile_ids:
        source_count = await db.scalar(select(func.count(Source.id)).where(Source.profile_id.in_(profile_ids)))
        source_count = source_count or 0

        candidate_count = await db.scalar(select(func.count(Candidate.id)).where(Candidate.profile_id.in_(profile_ids)))
        candidate_count = candidate_count or 0

        job_count = await db.scalar(select(func.count(Job.id)).where(Job.profile_id.in_(profile_ids)))
        job_count = job_count or 0

        active_jobs = await db.scalar(select(func.count(Job.id)).where(Job.profile_id.in_(profile_ids), Job.status.in_(["pending", "running", "queued"])))
        active_jobs = active_jobs or 0

        completed_jobs = await db.scalar(select(func.count(Job.id)).where(Job.profile_id.in_(profile_ids), Job.status == "completed"))
        completed_jobs = completed_jobs or 0

        failed_jobs = await db.scalar(select(func.count(Job.id)).where(Job.profile_id.in_(profile_ids), Job.status == "failed"))
        failed_jobs = failed_jobs or 0

    return ApiResponse(
        data=DashboardOverview(
            total_profiles=profile_count,
            total_sources=source_count,
            total_candidates=candidate_count,
            total_jobs=job_count,
            active_jobs=active_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            published_clips=0,
            storage_used_bytes=0,
            storage_capacity_bytes=1073741824,
            system_health="healthy",
        ),
        meta=get_meta(request),
    )


# ============================================================
# PROFILES (authenticated)
# ============================================================
@router.get("/profiles")
async def list_profiles(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    profile_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(ProfileRepository(db))
    data, total = await service.list(current_user.id, page, page_size, status, profile_type)
    return PaginatedResponse(data=[ProfileResponse.model_validate(p) for p in data],
                              meta=paginated_meta(request, page, page_size, total))


@router.post("/profiles", status_code=http_status.HTTP_201_CREATED)
async def create_profile(
    request: Request, body: ProfileCreate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProfileService(ProfileRepository(db))
    data = await service.create(current_user.id, body.model_dump(exclude_unset=True))
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


@router.get("/profiles/{profile_id}")
async def get_profile(
    request: Request, profile_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    data = await service.get(profile_id, current_user.id)
    if not data:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


@router.patch("/profiles/{profile_id}")
async def update_profile(
    request: Request, profile_id: str, body: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    data = await service.update(profile_id, current_user.id, body.model_dump(exclude_unset=True))
    if not data:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


@router.delete("/profiles/{profile_id}")
async def delete_profile(
    request: Request, profile_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    deleted = await service.delete(profile_id, current_user.id)
    if not deleted:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data={"deleted": True}, meta=get_meta(request))


@router.post("/profiles/{profile_id}/pause")
async def pause_profile(
    request: Request, profile_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    try:
        data = await service.update_status(profile_id, current_user.id, "paused")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


@router.post("/profiles/{profile_id}/resume")
async def resume_profile(
    request: Request, profile_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    try:
        data = await service.update_status(profile_id, current_user.id, "active")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


@router.post("/profiles/{profile_id}/archive")
async def archive_profile(
    request: Request, profile_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(profile_id, "profile_id")
    service = ProfileService(ProfileRepository(db))
    try:
        data = await service.update_status(profile_id, current_user.id, "archived")
    except ValueError as e:
        error("INVALID_TRANSITION", str(e), status_code=http_status.HTTP_409_CONFLICT)
    if not data:
        error("PROFILE_NOT_FOUND", "The requested profile does not exist.", status_code=404)
    return ApiResponse(data=ProfileResponse.model_validate(data), meta=get_meta(request))


# ============================================================
# SOURCES (authenticated)
# ============================================================
@router.get("/sources")
async def list_sources(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    profile_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SourceService(SourceRepository(db))
    data, total = await service.list(current_user.id, page, page_size, status, profile_id)
    return PaginatedResponse(data=[SourceResponse.model_validate(s) for s in data],
                              meta=paginated_meta(request, page, page_size, total))


@router.post("/sources", status_code=http_status.HTTP_201_CREATED)
async def create_source(
    request: Request, body: SourceCreate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify profile belongs to user
    profile_repo = ProfileRepository(db)
    profile = await profile_repo.get_by_id(body.profile_id, current_user.id)
    if not profile:
        error("PROFILE_NOT_FOUND", "Profile not found or does not belong to you.", status_code=404)
    service = SourceService(SourceRepository(db))
    data = await service.create(body.model_dump(exclude_unset=True))
    return ApiResponse(data=SourceResponse.model_validate(data), meta=get_meta(request))


@router.get("/sources/{source_id}")
async def get_source(
    request: Request, source_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(source_id, "source_id")
    service = SourceService(SourceRepository(db))
    data = await service.get(source_id, current_user.id)
    if not data:
        error("SOURCE_NOT_FOUND", "The requested source does not exist.", status_code=404)
    return ApiResponse(data=SourceResponse.model_validate(data), meta=get_meta(request))


@router.patch("/sources/{source_id}")
async def update_source(
    request: Request, source_id: str, body: SourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(source_id, "source_id")
    service = SourceService(SourceRepository(db))
    data = await service.update(source_id, current_user.id, body.model_dump(exclude_unset=True))
    if not data:
        error("SOURCE_NOT_FOUND", "The requested source does not exist.", status_code=404)
    return ApiResponse(data=SourceResponse.model_validate(data), meta=get_meta(request))


@router.post("/sources/upload", status_code=http_status.HTTP_201_CREATED)
async def upload_source(
    request: Request,
    profile_id: str = Query(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify profile belongs to user
    profile_repo = ProfileRepository(db)
    profile = await profile_repo.get_by_id(profile_id, current_user.id)
    if not profile:
        error("PROFILE_NOT_FOUND", "Profile not found or does not belong to you.", status_code=404)
    # ... rest of upload logic (unchanged)
    from app.workflows.ingestion import SourceIngestionWorkflow
    workflow = SourceIngestionWorkflow(db)
    result = await workflow.run_upload(profile_id, file)
    return ApiResponse(data=result, meta=get_meta(request))


@router.post("/sources/register-url", status_code=http_status.HTTP_201_CREATED)
async def register_source_url(
    request: Request, body: SourceRegisterUrl, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify profile belongs to user
    profile_repo = ProfileRepository(db)
    profile = await profile_repo.get_by_id(body.profile_id, current_user.id)
    if not profile:
        error("PROFILE_NOT_FOUND", "Profile not found or does not belong to you.", status_code=404)
    from app.workflows.ingestion import SourceIngestionWorkflow
    workflow = SourceIngestionWorkflow(db)
    result = await workflow.run_url_registration(body.profile_id, body.source_url, body.title)
    return ApiResponse(data=result, meta=get_meta(request))


# ============================================================
# CANDIDATES (authenticated)
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
    current_user: User = Depends(get_current_user),
):
    service = CandidateService(CandidateRepository(db))
    data, total = await service.list(
        current_user.id, page, page_size, approval_status, profile_id, source_id, min_score
    )
    return PaginatedResponse(data=[CandidateResponse.model_validate(c) for c in data],
                              meta=paginated_meta(request, page, page_size, total))


@router.get("/candidates/{candidate_id}")
async def get_candidate(
    request: Request, candidate_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(candidate_id, "candidate_id")
    service = CandidateService(CandidateRepository(db))
    data = await service.get(candidate_id, current_user.id)
    if not data:
        error("CANDIDATE_NOT_FOUND", "The requested candidate does not exist.", status_code=404)
    return ApiResponse(data=CandidateResponse.model_validate(data), meta=get_meta(request))


@router.patch("/candidates/{candidate_id}")
async def update_candidate(
    request: Request, candidate_id: str, body: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(candidate_id, "candidate_id")
    service = CandidateService(CandidateRepository(db))
    data = await service.update(candidate_id, current_user.id, body.model_dump(exclude_unset=True))
    if not data:
        error("CANDIDATE_NOT_FOUND", "The requested candidate does not exist.", status_code=404)
    return ApiResponse(data=CandidateResponse.model_validate(data), meta=get_meta(request))


# ============================================================
# JOBS (authenticated)
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
    current_user: User = Depends(get_current_user),
):
    service = JobService(JobRepository(db))
    data, total = await service.list(current_user.id, page, page_size, status, job_type, profile_id)
    return PaginatedResponse(data=[JobResponse.model_validate(j) for j in data],
                              meta=paginated_meta(request, page, page_size, total))


@router.get("/jobs/{job_id}")
async def get_job(
    request: Request, job_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(job_id, "job_id")
    service = JobService(JobRepository(db))
    data = await service.get(job_id, current_user.id)
    if not data:
        error("JOB_NOT_FOUND", "The requested job does not exist.", status_code=404)
    return ApiResponse(data=JobResponse.model_validate(data), meta=get_meta(request))


# ============================================================
# NOTIFICATIONS (authenticated)
# ============================================================
@router.get("/notifications")
async def list_notifications(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(NotificationRepository(db))
    data, total = await service.list(current_user.id, page, page_size, unread_only)
    return PaginatedResponse(data=[NotificationResponse.model_validate(n) for n in data],
                              meta=paginated_meta(request, page, page_size, total))


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    request: Request, notification_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(NotificationRepository(db))
    result = await service.mark_read(notification_id, current_user.id)
    return ApiResponse(data={"read": result}, meta=get_meta(request))


# ============================================================
# SETTINGS (system — authenticated)
# ============================================================
@router.get("/settings")
async def list_settings(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SettingsService(SettingsRepository(db))
    data = await service.get_all()
    return ApiResponse(data=data, meta=get_meta(request))


@router.patch("/settings")
async def update_settings(
    request: Request, body: SettingsUpdate, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SettingsService(SettingsRepository(db))
    data = await service.update(body.key, body.value)
    return ApiResponse(data=data, meta=get_meta(request))


@router.get("/settings/profile/{profile_id}")
async def get_profile_settings(
    request: Request, profile_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SettingsService(SettingsRepository(db))
    data = await service.get_profile_settings(profile_id, current_user.id)
    return ApiResponse(data=data, meta=get_meta(request))


@router.put("/settings/profile/{profile_id}/{key}")
async def set_profile_setting(
    request: Request, profile_id: str, key: str, body: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SettingsService(SettingsRepository(db))
    data = await service.set_profile_setting(profile_id, current_user.id, key, body.value)
    if not data:
        error("PROFILE_NOT_FOUND", "Profile not found or does not belong to you.", status_code=404)
    return ApiResponse(data=data, meta=get_meta(request))


# ============================================================
# INSPECTION (authenticated)
# ============================================================
@router.post("/sources/{source_id}/inspect")
async def inspect_source(
    request: Request, source_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(source_id, "source_id")
    service = SourceService(SourceRepository(db))
    source = await service.get(source_id, current_user.id)
    if not source:
        error("SOURCE_NOT_FOUND", "Source not found.", status_code=404)
    from app.workflows.ingestion import SourceIngestionWorkflow
    workflow = SourceIngestionWorkflow(db)
    result = await workflow.run_inspection(source_id)
    return ApiResponse(data=result, meta=get_meta(request))


@router.post("/sources/{source_id}/reinspect")
async def reinspect_source(
    request: Request, source_id: str, db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_uuid(source_id, "source_id")
    service = SourceService(SourceRepository(db))
    source = await service.get(source_id, current_user.id)
    if not source:
        error("SOURCE_NOT_FOUND", "Source not found.", status_code=404)
    from app.workflows.ingestion import SourceIngestionWorkflow
    workflow = SourceIngestionWorkflow(db)
    result = await workflow.run_reinspection(source_id)
    return ApiResponse(data=result, meta=get_meta(request))


# ============================================================
# ANALYTICS (authenticated)
# ============================================================
@router.get("/analytics/overview")
async def analytics_overview(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import select, func
    from app.models.models import Profile, Candidate

    profile_count = await db.scalar(select(func.count(Profile.id)).where(Profile.user_id == current_user.id))
    profile_count = profile_count or 0

    profile_rows = await db.execute(select(Profile.id).where(Profile.user_id == current_user.id))
    profile_ids = [row[0] for row in profile_rows]

    candidate_count = 0
    if profile_ids:
        candidate_count = await db.scalar(select(func.count(Candidate.id)).where(Candidate.profile_id.in_(profile_ids)))
        candidate_count = candidate_count or 0

    return ApiResponse(
        data=AnalyticsOverview(
            total_clips=candidate_count,
            total_published=0,
            total_views=0,
            total_engagement=0,
            avg_views_per_clip=0.0,
            top_platform="tiktok",
            growth_rate=0.0,
        ),
        meta=get_meta(request),
    )


# ============================================================
# SCHEDULES (authenticated)
# ============================================================
@router.get("/schedules")
async def list_schedules(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status: Optional[str] = None,
    profile_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conditions = []
    if status:
        conditions.append("status = :status")
    if profile_id:
        validate_uuid(profile_id, "profile_id")
        conditions.append("profile_id = :profile_id")
    where = " AND ".join(conditions) if conditions else "1=1"
    params = {"status": status, "profile_id": profile_id}

    # Schedules don't have a dedicated table yet — return empty
    return ApiResponse(
        data=[],
        meta=PaginatedMeta(page=page, page_size=page_size, total=0,
                           request_id=getattr(request.state, "request_id", str(uuid.uuid4()))),
    )


@router.post("/schedules")
async def create_schedule(
    request: Request,
    body: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    error("NOT_IMPLEMENTED", "Schedule creation is not yet implemented.", status_code=501)