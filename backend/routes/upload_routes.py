from flask import Blueprint

from controllers.upload_controller import sync_external_sources, upload_data

upload_bp = Blueprint("upload_bp", __name__)


@upload_bp.route("/api/upload", methods=["POST"])
def upload():
    return upload_data()


@upload_bp.route("/api/monitor/sync", methods=["POST"])
def monitor_sync():
    return sync_external_sources()
