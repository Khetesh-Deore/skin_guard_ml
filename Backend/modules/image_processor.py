
from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from io import BytesIO
from typing import Any

import numpy as np
from PIL import Image, ImageOps


_EXT_TO_MIME = {
    "jpg": {"image/jpeg"},
    "jpeg": {"image/jpeg"},
    "png": {"image/png"},
}


def _get_extension(filename: str | None) -> str | None:
    if not filename or "." not in filename:
        return None
    return filename.rsplit(".", 1)[1].lower()


def _read_bytes(file_object: Any) -> bytes:
    stream = getattr(file_object, "stream", file_object)
    pos = None
    try:
        pos = stream.tell()
    except Exception:
        pos = None

    try:
        data = stream.read()
    finally:
        if pos is not None:
            try:
                stream.seek(pos)
            except Exception:
                pass

    return data


def _get_file_size_bytes(file_object: Any, data: bytes | None = None) -> int:
    content_length = getattr(file_object, "content_length", None)
    if isinstance(content_length, int) and content_length >= 0:
        return content_length
    if data is not None:
        return len(data)

    stream = getattr(file_object, "stream", file_object)
    pos = None
    try:
        pos = stream.tell()
        stream.seek(0, os.SEEK_END)
        size = int(stream.tell())
        stream.seek(pos)
        return size
    except Exception:
        data2 = _read_bytes(file_object)
        return len(data2)


def _default_max_size_bytes() -> int:
    v = os.getenv("MAX_CONTENT_LENGTH")
    if v and v.isdigit():
        return int(v)
    return 5 * 1024 * 1024


def _default_allowed_extensions() -> set[str]:
    v = os.getenv("ALLOWED_EXTENSIONS")
    if v:
        return {x.strip().lower().lstrip(".") for x in v.split(",") if x.strip()}
    return {"jpg", "jpeg", "png"}


def _default_input_size() -> tuple[int, int]:
    v = os.getenv("MODEL_INPUT_SIZE") or os.getenv("MODEL_IMG_SIZE")
    if v and "x" in v:
        w, h = v.lower().split("x", 1)
        if w.strip().isdigit() and h.strip().isdigit():
            return int(w), int(h)
    if v and v.strip().isdigit():
        n = int(v.strip())
        return n, n
    return 224, 224


def _normalization_mode() -> str:
    return (os.getenv("NORMALIZATION", "0_1") or "0_1").strip().lower()


@dataclass
class ImageMetadata:
    original_width: int
    original_height: int
    mode: str
    had_exif_orientation: bool
    filename: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None


def validate_image(file_object: Any) -> tuple[bool, str | None]:
    if file_object is None:
        return False, "Missing file"

    filename = getattr(file_object, "filename", None)
    ext = _get_extension(filename)
    if ext is None:
        return False, "Missing file extension"

    allowed = _default_allowed_extensions()
    if ext not in allowed:
        return False, "Unsupported file type"

    data = _read_bytes(file_object)
    if not data:
        return False, "Empty file"

    size_bytes = _get_file_size_bytes(file_object, data=data)
    max_size = _default_max_size_bytes()
    if size_bytes > max_size:
        return False, "File too large"

    mime = (getattr(file_object, "mimetype", None) or "").lower()
    expected = _EXT_TO_MIME.get(ext, set())
    if mime and expected and mime not in expected:
        return False, "MIME type does not match file extension"

    try:
        with Image.open(BytesIO(data)) as img:
            img.verify()
    except Exception:
        return False, "Invalid or corrupted image"

    try:
        with Image.open(BytesIO(data)) as img2:
            w, h = img2.size
            if w <= 0 or h <= 0:
                return False, "Invalid image dimensions"
    except Exception:
        return False, "Invalid or corrupted image"

    if size_bytes > 20 * 1024 * 1024:
        warnings.warn("Extremely large image detected; processing may be slow.")

    return True, None


def _load_image(file_object: Any) -> tuple[Image.Image, ImageMetadata]:
    data = _read_bytes(file_object)
    with Image.open(BytesIO(data)) as img:
        had_exif_orientation = bool(getattr(img, "getexif", lambda: None)())
        img = ImageOps.exif_transpose(img)

        if img.mode != "RGB":
            img = img.convert("RGB")

        meta = ImageMetadata(
            original_width=img.size[0],
            original_height=img.size[1],
            mode=img.mode,
            had_exif_orientation=had_exif_orientation,
            filename=getattr(file_object, "filename", None),
            mime_type=getattr(file_object, "mimetype", None),
            size_bytes=_get_file_size_bytes(file_object, data=data),
        )
        return img.copy(), meta


def process_image(file_object: Any) -> np.ndarray:
    ok, err = validate_image(file_object)
    if not ok:
        raise ValueError(err or "Invalid image")

    img, _meta = _load_image(file_object)
    target_w, target_h = _default_input_size()

    img_resized = img.resize((target_w, target_h), resample=Image.BILINEAR)
    arr = np.asarray(img_resized)

    arr = arr.astype(np.float32)

    mode = _normalization_mode()
    if mode in {"0_1", "0-1", "zero_one"}:
        arr = arr / 255.0
    elif mode in {"-1_1", "-1to1", "minus_one_one"}:
        arr = (arr / 127.5) - 1.0
    else:
        arr = arr / 255.0

    arr = np.expand_dims(arr, axis=0)
    return arr

