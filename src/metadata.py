from dataclasses import dataclass


@dataclass(frozen=True)
class MetadataResult:
    media_type: str
    mime_type: str
    width: int | None = None
    height: int | None = None
    duration_seconds: float | None = None


def normalize_media_type(mime_type: str) -> str:
    if mime_type.startswith("image/"):
        return "image"
    if mime_type.startswith("video/"):
        return "video"
    raise ValueError(f"unsupported media type: {mime_type}")

