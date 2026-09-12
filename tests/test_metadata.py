import pytest

from src.metadata import build_result, calculate_aspect_ratio, normalize_media_type


def test_media_type():
    assert normalize_media_type("image/jpeg") == "image"
    assert normalize_media_type("video/mp4") == "video"


def test_aspect_ratio_is_reduced():
    assert calculate_aspect_ratio(1920, 1080) == "16:9"
    assert calculate_aspect_ratio(1080, 1080) == "1:1"


def test_image_result_is_deterministic():
    result = build_result(asset_id="asset-1", mime_type="image/jpeg", width=1200, height=800)
    assert result.media_type == "image"
    assert result.aspect_ratio == "3:2"
    assert result.source == "deterministic"
    assert result.duration_seconds is None
    assert result.asset_id == "asset-1"


def test_video_result_contains_duration_and_frame_rate():
    result = build_result(
        asset_id="asset-2", mime_type="video/mp4", width=3840, height=2160,
        duration_seconds=12.5, frame_rate=29.97,
    )
    assert result.media_type == "video"
    assert result.aspect_ratio == "16:9"
    assert result.duration_seconds == 12.5
    assert result.frame_rate == 29.97


def test_image_cannot_have_video_fields():
    with pytest.raises(ValueError):
        build_result(mime_type="image/png", width=10, height=10, duration_seconds=1)
