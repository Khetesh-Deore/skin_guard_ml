
from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from modules.image_processor import process_image, validate_image


predict_bp = Blueprint("predict", __name__)


def _allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", set())


@predict_bp.post("/predict")
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Missing file field 'image'"}), 400

    file = request.files["image"]
    if not file or not file.filename:
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    ok, err = validate_image(file)
    if not ok:
        return jsonify({"error": err or "Invalid image"}), 400

    try:
        arr = process_image(file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Failed to process image"}), 500

    return jsonify(
        {
            "status": "processed",
            "filename": file.filename,
            "shape": list(arr.shape),
            "dtype": str(arr.dtype),
            "normalization": current_app.config.get("NORMALIZATION", "0_1"),
            "min": float(arr.min()),
            "max": float(arr.max()),
        }
    )

