from datetime import datetime, timezone
import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from .metadata import build_result

app = FastAPI(title="asset-metadata-service", version="0.2.0")


class MetadataRequest(BaseModel):
    asset_id: str = Field(min_length=1)
    mime_type: str = Field(min_length=1)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    duration_seconds: float | None = Field(default=None, ge=0)
    frame_rate: float | None = Field(default=None, gt=0)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/metadata")
def extract_metadata(request: MetadataRequest) -> dict:
    try:
        result = build_result(
            asset_id=request.asset_id,
            mime_type=request.mime_type,
            width=request.width,
            height=request.height,
            duration_seconds=request.duration_seconds,
            frame_rate=request.frame_rate,
            extracted_at=datetime.now(timezone.utc).isoformat(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result.to_dict()


@app.post("/v1/video-preview")
async def video_preview(request: Request) -> Response:
    """Return a 2x2 contact sheet sampled across an uploaded video."""
    max_bytes = 512 * 1024 * 1024
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_bytes:
        raise HTTPException(status_code=413, detail="video exceeds 512 MiB limit")

    with tempfile.TemporaryDirectory(prefix="video-preview-") as temp_dir:
        source = Path(temp_dir) / "source.mp4"
        output = Path(temp_dir) / "preview.jpg"
        total = 0
        try:
            with source.open("wb") as handle:
                async for chunk in request.stream():
                    total += len(chunk)
                    if total > max_bytes:
                        raise HTTPException(
                            status_code=413,
                            detail="video exceeds 512 MiB limit",
                        )
                    handle.write(chunk)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"invalid video upload: {exc}") from exc

        if total == 0:
            raise HTTPException(status_code=400, detail="empty video upload")

        try:
            duration_text = subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(source),
                ],
                text=True,
                timeout=30,
            ).strip()
            duration = max(float(duration_text), 0.1)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            raise HTTPException(status_code=422, detail="unable to read video duration") from exc

        interval = max(duration / 4, 0.1)
        video_filter = (
            f"fps=1/{interval:.6f}:start_time={interval / 2:.6f},"
            "scale=640:640:force_original_aspect_ratio=decrease,"
            "pad=640:640:(ow-iw)/2:(oh-ih)/2:black,tile=2x2"
        )
        completed = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-threads",
                "1",
                "-i",
                str(source),
                "-vf",
                video_filter,
                "-frames:v",
                "1",
                "-q:v",
                "3",
                str(output),
            ],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if completed.returncode != 0 or not output.exists():
            detail = completed.stderr.strip()[-500:] or "unable to create preview"
            raise HTTPException(status_code=422, detail=detail)

        return Response(
            content=output.read_bytes(),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-store",
                "X-Video-Duration": f"{duration:.3f}",
            },
        )
