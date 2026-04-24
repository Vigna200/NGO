from flask import Flask, jsonify
from flask_cors import CORS

from config import MAX_CONTENT_LENGTH, UPLOAD_FOLDER
from database.db import initialize_database
from routes.task_routes import task_bp
from routes.upload_routes import upload_bp
from routes.volunteer_routes import volunteer_bp


def create_app():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    CORS(app)
    initialize_database()

    app.register_blueprint(upload_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(volunteer_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
