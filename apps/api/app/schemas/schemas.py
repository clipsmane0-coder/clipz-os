from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime


# ============================================================
# API ENVELOPES
# ============================================================
class ApiMeta(BaseModel):
    request_id: str


class ApiResponse(BaseModel):
    success: bool = True
    data: Any
    meta: ApiMeta


class PaginatedMeta(BaseModel):
    page: int
    page_size: int
    total: int
    request_id: str


class PaginatedResponse(BaseModel):
    success: bool = True
    data: List[Any]
    meta: PaginatedMeta


class ApiError(BaseModel):
    code: str
    message: str
    details: dict = {}
    retryable: bool = False


class ApiErrorResponse(BaseModel):
    success: bool = False
    error: ApiError
    meta: ApiMeta


# ============================================================
# HEALTH
# ============================================================
class HealthResponse(BaseModel):
    api: bool = True
    database: bool = True
    version: str = "0.1.0"


# ============================================================
# PROFILES
# ============================================================
class ProfileCreate(BaseModel):
    name: str
    slug: str
    profile_type: str = "general"
    description: str = ""
    avatar_path: Optional[str] = None
    language: str = "en"
    auto_approval_enabled: bool = False
    default_processing_mode: str = "balanced"
    default_rights_status: str = "unknown"


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    profile_type: Optional[str] = None
    description: Optional[str] = None
    avatar_path: Optional[str] = None
    language: Optional[str] = None
    auto_approval_enabled: Optional[bool] = None
    default_processing_mode: Optional[str] = None
    default_rights_status: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    name: str
    slug: str
    profile_type: str
    description: str
    avatar_path: Optional[str] = None
    language: str
    status: str
    auto_approval_enabled: bool
    default_processing_mode: str
    default_rights_status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# SOURCES
# ============================================================
class SourceCreate(BaseModel):
    title: str
    profile_id: str
    source_type: str = "upload"
    source_kind: str = "video"
    source_url: Optional[str] = None
    original_filename: Optional[str] = None
    duration_ms: int = 0
    width: int = 0
    height: int = 0
    frame_rate: float = 0.0
    language: str = "en"
    rights_status: str = "unknown"


class SourceRegisterUrl(BaseModel):
    profile_id: str
    source_url: str
    title: Optional[str] = None
    platform: Optional[str] = None
    rights_status: str = "unknown"


class SourceUpdate(BaseModel):
    title: Optional[str] = None
    language: Optional[str] = None
    rights_status: Optional[str] = None
    status: Optional[str] = None


class SourceResponse(BaseModel):
    id: str
    profile_id: str
    title: str
    source_type: str
    source_kind: str = "video"
    original_filename: Optional[str] = None
    original_url: Optional[str] = None
    storage_key: Optional[str] = None
    source_url: Optional[str] = None
    mime_type: Optional[str] = None
    extension: Optional[str] = None
    file_hash: Optional[str] = None
    checksum_sha256: Optional[str] = None
    duration_ms: int
    width: int
    height: int
    frame_rate: float
    codec: Optional[str] = None
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    audio_channels: Optional[int] = None
    audio_sample_rate: Optional[int] = None
    bitrate: Optional[int] = None
    container_format: Optional[str] = None
    file_size_bytes: int
    language: str
    rights_status: str
    status: str
    inspection_status: str = "pending"
    inspection_error: Optional[str] = None
    thumbnail_storage_key: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    imported_at: datetime
    inspected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# CANDIDATES
# ============================================================
class CandidateCreate(BaseModel):
    source_id: str
    profile_id: str
    start_ms: int = 0
    end_ms: int = 0
    duration_ms: int = 0
    title: str = ""
    transcript_excerpt: str = ""
    hook_text: str = ""
    selection_reason: str = ""
    overall_score: float = 0.0


class CandidateUpdate(BaseModel):
    title: Optional[str] = None
    approval_status: Optional[str] = None
    recommended_platform: Optional[str] = None


class CandidateResponse(BaseModel):
    id: str
    source_id: str
    profile_id: str
    start_ms: int
    end_ms: int
    duration_ms: int
    title: str
    transcript_excerpt: str
    hook_text: str
    selection_reason: str
    overall_score: float
    crop_confidence: float
    audio_quality_score: float
    visual_quality_score: float
    duplicate_risk: float
    safety_status: str
    rights_status: str
    approval_status: str
    recommended_platform: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# JOBS
# ============================================================
class JobCreate(BaseModel):
    job_type: str
    entity_type: str
    entity_id: str
    profile_id: Optional[str] = None
    priority: str = "normal"
    payload_json: Optional[dict] = None


class JobResponse(BaseModel):
    id: str
    job_type: str
    entity_type: str
    entity_id: str
    profile_id: Optional[str] = None
    priority: str
    status: str
    progress_percent: int
    attempts: int
    max_attempts: int
    retryable: bool
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# NOTIFICATIONS
# ============================================================
class NotificationResponse(BaseModel):
    id: str
    profile_id: Optional[str] = None
    type: str
    title: str
    message: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# SETTINGS
# ============================================================
class SettingsUpdate(BaseModel):
    key: str
    value: str


class SettingsResponse(BaseModel):
    key: str
    value: str
    value_type: str
    description: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# PROFILE SETTINGS
# ============================================================
class ProfileSettingsResponse(BaseModel):
    id: str
    profile_id: str
    key: str
    value: str
    value_type: str
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# DASHBOARD
# ============================================================
class DashboardOverview(BaseModel):
    total_profiles: int = 0
    total_sources: int = 0
    total_candidates: int = 0
    total_jobs: int = 0
    active_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    published_clips: int = 0
    storage_used_bytes: int = 0
    storage_capacity_bytes: int = 0
    system_health: str = "healthy"


# ============================================================
# SCHEDULES
# ============================================================
class ScheduleCreate(BaseModel):
    profile_id: str
    platform: str
    scheduled_at: str
    candidate_id: Optional[str] = None
    status: str = "draft"


class ScheduleUpdate(BaseModel):
    status: Optional[str] = None
    scheduled_at: Optional[str] = None


class ScheduleResponse(BaseModel):
    id: str
    profile_id: str
    platform: str
    scheduled_at: str
    candidate_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# ANALYTICS
# ============================================================
class AnalyticsOverview(BaseModel):
    total_clips: int = 0
    total_published: int = 0
    total_views: int = 0
    total_engagement: int = 0
    avg_views_per_clip: float = 0.0
    top_platform: str = "tiktok"
    growth_rate: float = 0.0