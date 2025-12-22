
import os
import signal
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from config import get_config_class
from routes.predict_routes import predict_bp
from modules import predictor


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)

    config_cls = get_config_class()
    app.config.from_object(config_cls)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    
    # Load ML model and disease mapping at startup
    _initialize_model(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", [])}},
        supports_credentials=False,
    )

    @app.get("/api/health")
    def health_check():
        model_info = predictor.get_model_info()
        return jsonify(
            {
                "status": "ok",
                "env": app.config.get("ENV"),
                "model_loaded": model_info.get("loaded", False),
                "num_classes": model_info.get("num_classes", 0)
            }
        )

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not Found"}), 404

    @app.errorhandler(413)
    def file_too_large(_error):
        return jsonify({"error": "File too large"}), 413

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "Internal Server Error"}), 500

    app.register_blueprint(predict_bp, url_prefix="/api")

    def _handle_termination(_signum, _frame):
        raise SystemExit(0)

    if os.name != "nt":
        signal.signal(signal.SIGTERM, _handle_termination)
    signal.signal(signal.SIGINT, _handle_termination)

    return app


def _initialize_model(app: Flask) -> None:
    """Initialize ML model and disease mapping at startup"""
    try:
        # Get model path from config
        model_path = app.config.get("MODEL_PATH")
        
        # Check if the configured model exists, otherwise use the actual model file
        if not os.path.exists(model_path):
            # Try the actual model file in the models directory
            base_dir = Path(__file__).resolve().parent
            actual_model = base_dir / "models" / "skin_efficientnet_v2_final_90plus.h5"
            if actual_model.exists():
                model_path = str(actual_model)
                app.logger.info(f"Using actual model: {model_path}")
            else:
                app.logger.error(f"Model file not found at {model_path}")
                raise FileNotFoundError(f"Model file not found")
        
        # Load the model
        predictor.load_model(model_path)
        
        # Load disease mapping
        base_dir = Path(__file__).resolve().parent
        mapping_path = base_dir / "models" / "disease_mapping.json"
        predictor.load_disease_mapping(str(mapping_path))
        
        app.logger.info("Model and disease mapping loaded successfully")
        
    except Exception as e:
        app.logger.error(f"Failed to initialize model: {str(e)}")
        # Don't crash the app, but log the error
        app.logger.warning("Application started without model loaded")


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))

