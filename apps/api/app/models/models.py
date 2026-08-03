import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


# ============================================================
# USERS
# ============================================================
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="owner")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


# ============================================================
# SESSIONS
# ============================================================
class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="sessions")


# ============================================================
# PROFILES
# ============================================================
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    profile_type = Column(String, nullable=False, default="general")
    description = Column(Text, default="")
    avatar_path = Column(String, nullable=True)
    language = Column(String, default="en")
    status = Column(String, nullable=False, default="active")
    auto_approval_enabled = Column(Boolean, default=False)
    default_processing_mode = Column(String, default="balanced")
    default_rights_status = Column(String, default="unknown")
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="profiles")
    platforms = relationship("ProfilePlatform", back_populates="profile", cascade="all, delete-orphan")
    profile_sources = relationship("ProfileSource", back_populates="profile", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="profile", cascade="all, delete-orphan")
    candidates = relationship("Candidate", back_populates="profile", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="profile", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="profile", cascade="all, delete-orphan")


class ProfilePlatform(Base):
    __tablename__ = "profile_platforms"

    id = Column(String, primary_key=True, default=gen_uuid)
    profile_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String, nullable=False)
    handle = Column(String, default="")
    account_id = Column(String, nullable=True)
    is_connected = Column(Boolean, default=False)
    posting_enabled = Column(Boolean, default=False)
    daily_post_limit = Column(Integer, default=3)
    timezone = Column(String, default="UTC")
    credentials_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    profile = relationship("Profile", back_populates="platforms")


class ProfileSource(Base):
    __tablename__ = "profile_sources"

    id = Column(String, primary_key=True, default=gen_uuid)
    profile_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    source_name = Column(String, nullable=False)
    authorization_status = Column(String, default="unauthorized")
    watcher_enabled = Column(Boolean, default=False)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    profile = relationship("Profile", back_populates="profile_sources")


# ============================================================
# SOURCES
# ============================================================
class Source(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True, default=gen_uuid)
    profile_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False, default="upload")
    source_kind = Column(String, default="video")
    original_filename = Column(String, nullable=True)
    original_url = Column(String, nullable=True)
    storage_key = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    extension = Column(String, nullable=True)
    file_hash = Column(String, nullable=True)
    checksum_sha256 = Column(String, nullable=True)
    audio_fingerprint = Column(String, nullable=True)
    visual_fingerprint = Column(String, nullable=True)
    duration_ms = Column(Integer, default=0)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    frame_rate = Column(Float, default=0.0)
    codec = Column(String, nullable=True)
    video_codec = Column(String, nullable=True)
    audio_codec = Column(String, nullable=True)
    audio_channels = Column(Integer, nullable=True)
    audio_sample_rate = Column(Integer, nullable=True)
    bitrate = Column(Integer, nullable=True)
    container_format = Column(String, nullable=True)
    file_size_bytes = Column(Integer, default=0)
    language = Column(String, default="en")
    rights_status = Column(String, default="unknown")
    status = Column(String, nullable=False, default="new")
    inspection_status = Column(String, default="pending")
    inspection_error = Column(String, nullable=True)
    thumbnail_storage_key = Column(String, nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    imported_at = Column(DateTime, default=utcnow)
    inspected_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    profile = relationship("Profile", back_populates="sources")
    candidates = relationship("Candidate", back_populates="source", cascade="all, delete-orphan")


# ============================================================
# CANDIDATES
# ============================================================
class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=gen_uuid)
    source_id = Column(String, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    analysis_run_id = Column(String, nullable=True)
    profile_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    start_ms = Column(Integer, default=0)
    end_ms = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    title = Column(String, default="")
    transcript_excerpt = Column(Text, default="")
    hook_text = Column(String, default="")
    selection_reason = Column(String, default="")
    overall_score = Column(Float, default=0.0)
    crop_confidence = Column(Float, default=0.0)
    audio_quality_score = Column(Float, default=0.0)
    visual_quality_score = Column(Float, default=0.0)
    duplicate_risk = Column(Float, default=0.0)
    safety_status = Column(String, default="safe")
    rights_status = Column(String, default="unknown")
    approval_status = Column(String, nullable=False, default="pending")
    recommended_platform = Column(String, default="tiktok")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    source = relationship("Source", back_populates="candidates")
    profile = relationship("Profile", back_populates="candidates")
    scores = relationship("CandidateScore", back_populates="candidate", cascade="all, delete-orphan")


class CandidateScore(Base):
    __tablename__ = "candidate_scores"

    id = Column(String, primary_key=True, default=gen_uuid)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    signal_name = Column(String, nullable=False)
    raw_value = Column(Float, default=0.0)
    normalized_value = Column(Float, default=0.0)
    weight = Column(Float, default=0.0)
    weighted_score = Column(Float, default=0.0)
    explanation = Column(String, default="")
    created_at = Column(DateTime, default=utcnow)

    candidate = relationship("Candidate", back_populates="scores")


# ============================================================
# JOBS
# ============================================================
class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=gen_uuid)
    job_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    profile_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    priority = Column(String, default="normal")
    status = Column(String, nullable=False, default="pending")
    progress_percent = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    retryable = Column(Boolean, default=True)
    locked_by = Column(String, nullable=True)
    locked_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    payload_json = Column(JSON, nullable=True)
    result_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    profile = relationship("Profile", back_populates="jobs")


# ============================================================
# NOTIFICATIONS
# ============================================================
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True)
    type = Column(String, nullable=False, default="informational")
    title = Column(String, nullable=False)
    message = Column(Text, default="")
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="notifications")
    profile = relationship("Profile", back_populates="notifications")


# ============================================================
# SETTINGS
# ============================================================
class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(String, primary_key=True, default=gen_uuid)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False, default="")
    value_type = Column(String, default="string")
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class ProfileSetting(Base):
    __tablename__ = "profile_settings"

    id = Column(String, primary_key=True, default=gen_uuid)
    profile_id = Column(String, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False, default="")
    value_type = Column(String, default="string")
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


# ============================================================
# AUDIT LOGS
# ============================================================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    old_values_json = Column(JSON, nullable=True)
    new_values_json = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)