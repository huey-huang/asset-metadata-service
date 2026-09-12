from dataclasses import asdict, dataclass
from fractions import Fraction
import mimetypes


@dataclass(frozen=True)
class MetadataResult:
    asset_id: str
    media_type: str
    mime_type: str
    width: int | None = None
    height: int | None = None
    duration_seconds: float | None = None
    aspect_ratio: str | None = None
    frame_rate: float | None = None
    source: str = "deterministic"
    extractor_version: str = "metadata-contract-v0.1"
    extracted_at: str | None = None

    def to_dict(self) -> dict:
        """Return a JSON-serializable result for the metadata API."""
        return asdict(self)


def normalize_media_type(mime_type: str) -> str:
    if mime_type.startswith("image/"):
        return "image"
    if mime_type.startswith("video/"):
        return "video"
    raise ValueError(f"unsupported media type: {mime_type}")


def calculate_aspect_ratio(width: int, height: int) -> str:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    ratio = Fraction(width, height)
    return f"{ratio.numerator}:{ratio.denominator}"


def build_result(
    *, mime_type: str, width: int, height: int,
    asset_id: str = "unknown-asset",
    duration_seconds: float | None = None,
    frame_rate: float | None = None,
    extracted_at: str | None = None,
    extractor_version: str = "metadata-contract-v0.1",
) -> MetadataResult:
    """Build normalized immutable metadata from probe output."""
    media_type = normalize_media_type(mime_type)
    if media_type == "image" and duration_seconds is not None:
        raise ValueError("image metadata cannot include duration_seconds")
    if media_type == "image" and frame_rate is not None:
        raise ValueError("image metadata cannot include frame_rate")
    return MetadataResult(
        asset_id=asset_id,
        media_type=media_type,
        mime_type=mime_type,
        width=width,
        height=height,
        duration_seconds=duration_seconds,
        aspect_ratio=calculate_aspect_ratio(width, height),
        frame_rate=frame_rate,
        extractor_version=extractor_version,
        extracted_at=extracted_at,
    )
