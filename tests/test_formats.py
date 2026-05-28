from raw_to_jpeg.formats import classify_path, output_name_for


def test_classifies_supported_formats():
    assert classify_path("photo.jpg") == "jpeg"
    assert classify_path("photo.PNG") == "pillow"
    assert classify_path("photo.heic") == "heic"
    assert classify_path("photo.CR3") == "raw"
    assert classify_path("notes.txt") is None


def test_output_name_keeps_jpeg_name_and_normalizes_others():
    from pathlib import Path

    assert output_name_for(Path("photo.jpeg")) == "photo.jpeg"
    assert output_name_for(Path("photo.png")) == "photo.jpg"

