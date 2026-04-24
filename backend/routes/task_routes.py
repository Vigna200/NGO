from flask import Blueprint

from controllers.task_controller import get_dashboard, get_tasks, update_task_assignment, update_task_status

task_bp = Blueprint("task_bp", __name__)


@task_bp.route("/api/tasks", methods=["GET"])
def tasks():
    return get_tasks()


@task_bp.route("/api/dashboard", methods=["GET"])
def dashboard():
    return get_dashboard()


@task_bp.route("/api/assign", methods=["POST"])
def assign():
    return update_task_assignment()


@task_bp.route("/api/tasks/<task_id>/status", methods=["POST"])
def status(task_id):
    return update_task_status(task_id)
