from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .metadata import build_result

app = FastAPI(title="asset-metadata-service", version="0.1.0")


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
