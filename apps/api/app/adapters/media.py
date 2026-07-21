"""Media inspection adapters.

Provides FFprobe for metadata extraction and FFmpeg for thumbnail extraction.
"""

import json
import subprocess
from typing import Dict, Any
from abc import ABC, abstractmethod



class MediaInspector(ABC):
    """Abstract media inspection interface."""

    @abstractmethod
    async def inspect(self, file_path: str) -> Dict[str, Any]:
        """Extract media metadata from a file path."""
        ...


class FFprobeMediaInspector(MediaInspector):
    """Inspects media files using FFprobe."""

    def __init__(self, ffprobe_path: str = "ffprobe", timeout: int = 30):
        self.ffprobe_path = ffprobe_path
        self.timeout = timeout

    async def inspect(self, file_path: str) -> Dict[str, Any]:
        """Run FFprobe and parse metadata."""
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path,
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except FileNotFoundError:
            raise RuntimeError(f"FFprobe not found at '{self.ffprobe_path}'")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"FFprobe timed out after {self.timeout}s")

        if result.returncode != 0:
            raise RuntimeError(f"FFprobe failed (exit {result.returncode}): {result.stderr[:500]}")

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"FFprobe returned invalid JSON: {e}")

        return self._parse_ffprobe_output(data)

    def _parse_ffprobe_output(self, data: Dict) -> Dict[str, Any]:
        """Parse FFprobe JSON output into structured metadata."""
        fmt = data.get("format", {})
        streams = data.get("streams", [])

        video_stream = None
        audio_stream = None
        for s in streams:
            if s.get("codec_type") == "video" and not video_stream:
                video_stream = s
            elif s.get("codec_type") == "audio" and not audio_stream:
                audio_stream = s

        metadata = {
            "duration_ms": int(float(fmt.get("duration", 0)) * 1000),
            "file_size_bytes": int(fmt.get("size", 0)),
            "bitrate": int(fmt.get("bit_rate", 0)),
            "container_format": fmt.get("format_name", ""),
            "video_codec": video_stream.get("codec_name") if video_stream else None,
            "width": int(video_stream.get("width", 0)) if video_stream else 0,
            "height": int(video_stream.get("height", 0)) if video_stream else 0,
            "frame_rate": self._parse_frame_rate(video_stream.get("r_frame_rate", "0/1")) if video_stream else 0.0,
            "has_video": video_stream is not None,
            "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
            "audio_channels": int(audio_stream.get("channels", 0)) if audio_stream else None,
            "audio_sample_rate": int(audio_stream.get("sample_rate", 0)) if audio_stream else None,
            "has_audio": audio_stream is not None,
        }
        return metadata

    def _parse_frame_rate(self, frame_rate_str: str) -> float:
        """Parse a frame rate string like '30000/1001' to float."""
        try:
            parts = frame_rate_str.split("/")
            if len(parts) == 2:
                return round(float(parts[0]) / float(parts[1]), 3)
            return float(frame_rate_str)
        except (ValueError, ZeroDivisionError):
            return 0.0


class ThumbnailExtractor:
    """Extracts a representative frame using FFmpeg."""

    def __init__(self, ffmpeg_path: str = "ffmpeg", timeout: int = 30):
        self.ffmpeg_path = ffmpeg_path
        self.timeout = timeout

    async def extract(self, source_path: str, output_path: str) -> bool:
        """Extract one frame at the midpoint of the video."""
        cmd = [
            self.ffmpeg_path,
            "-i", source_path,
            "-ss", "00:00:01",
            "-vframes", "1",
            "-q:v", "2",
            "-y",
            output_path,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=self.timeout)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False