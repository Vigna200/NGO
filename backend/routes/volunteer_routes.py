from flask import Blueprint

from controllers.volunteer_controller import get_volunteers

volunteer_bp = Blueprint("volunteer_bp", __name__)


@volunteer_bp.route("/api/volunteers", methods=["GET"])
def volunteers():
    return get_volunteers()
