"""Storage abstraction for CLIPZ media files.

Interface + LocalStorageAdapter implementation.
All storage paths use UUID-based keys, never original filenames.
"""

import os
import hashlib
import uuid
from pathlib import Path
from typing import Optional
from abc import ABC, abstractmethod

from app.core.config import settings


class StorageAdapter(ABC):
    """Abstract storage interface."""

    @abstractmethod
    async def save(self, key: str, data: bytes) -> str:
        """Save data to storage, return the full path."""
        ...

    @abstractmethod
    async def open(self, key: str) -> Optional[bytes]:
        """Read data from storage."""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in storage."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key from storage."""
        ...

    @abstractmethod
    async def size(self, key: str) -> int:
        """Return file size in bytes."""
        ...

    @abstractmethod
    def resolve_path(self, key: str) -> str:
        """Resolve a storage key to an absolute filesystem path."""
        ...


class LocalStorageAdapter(StorageAdapter):
    """Stores files on the local filesystem under STORAGE_ROOT."""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.storage_root)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        """Resolve a key to a safe filesystem path, preventing traversal."""
        sanitized = Path(key).as_posix().lstrip("/")
        resolved = (self.base_path / sanitized).resolve()
        if not str(resolved).startswith(str(self.base_path.resolve())):
            raise ValueError(f"Path traversal detected: {key}")
        return resolved

    async def save(self, key: str, data: bytes) -> str:
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    async def open(self, key: str) -> Optional[bytes]:
        path = self._resolve(key)
        if not path.exists():
            return None
        return path.read_bytes()

    async def exists(self, key: str) -> bool:
        return self._resolve(key).exists()

    async def delete(self, key: str) -> bool:
        path = self._resolve(key)
        if not path.exists():
            return False
        path.unlink()
        return True

    async def size(self, key: str) -> int:
        return self._resolve(key).stat().st_size

    def resolve_path(self, key: str) -> str:
        return str(self._resolve(key))


def calculate_sha256(data: bytes) -> str:
    """Calculate SHA-256 checksum of binary data."""
    return hashlib.sha256(data).hexdigest()


def generate_storage_key(directory: str, extension: str) -> str:
    """Generate a UUID-based storage key.

    Args:
        directory: Subdirectory (e.g., 'sources', 'thumbnails')
        extension: File extension (e.g., '.mp4', '.jpg')

    Returns:
        Storage key like 'sources/a1b2c3d4-e5f6-7890-abcd-ef1234567890.mp4'
    """
    return f"{directory}/{uuid.uuid4()}{extension}"


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for metadata storage.

    Strips path separators and null bytes.
    Preserves the original filename as metadata only — never as a storage path.
    """
    # Remove null bytes
    clean = filename.replace("\x00", "")
    # Remove path separators
    clean = clean.replace("/", "_").replace("\\", "_")
    # Limit length
    if len(clean) > 255:
        name, ext = os.path.splitext(clean)
        clean = name[:250] + ext
    return clean


ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".mpg", ".mpeg"}
ALLOWED_MIME_TYPES = {
    "video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska",
    "video/webm", "video/x-flv", "video/x-ms-wmv", "video/mp4",
    "video/mpeg", "application/octet-stream",  # Allow octet-stream for unknown
}
MAX_UPLOAD_SIZE_BYTES = settings.max_upload_size_mb * 1024 * 1024