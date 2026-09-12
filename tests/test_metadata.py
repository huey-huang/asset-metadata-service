from src.metadata import normalize_media_type


def test_media_type():
    assert normalize_media_type("image/jpeg") == "image"
    assert normalize_media_type("video/mp4") == "video"

