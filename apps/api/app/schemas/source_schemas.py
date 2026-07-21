from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SourceUploadResponse(BaseModel):
    id: str
    profile_id: str
    title: str
    source_type: str
    original_filename: Optional[str] = None
    file_size_bytes: int = 0
    mime_type: Optional[str] = None
    checksum_sha256: Optional[str] = None
    status: str
    inspection_status: str = "pending"
    storage_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SourceInspectionResponse(BaseModel):
    duration_ms: int = 0
    width: int = 0
    height: int = 0
    frame_rate: float = 0.0
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    audio_channels: Optional[int] = None
    audio_sample_rate: Optional[int] = None
    bitrate: Optional[int] = None
    container_format: Optional[str] = None
    inspection_status: str
    inspection_error: Optional[str] = None
    inspected_at: Optional[datetime] = None

    model_config = {"from_attributes": True}