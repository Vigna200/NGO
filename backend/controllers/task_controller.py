from flask import jsonify, request

from database.db import get_store


def get_tasks():
    return jsonify({"tasks": get_store().get_tasks()})


def get_dashboard():
    return jsonify(get_store().get_dashboard_snapshot())


def update_task_assignment():
    payload = request.get_json(silent=True) or {}
    task_id = payload.get("task_id")
    volunteer_id = payload.get("volunteer_id")

    if not task_id or not volunteer_id:
        return jsonify({"error": "task_id and volunteer_id are required."}), 400

    updated_task = get_store().assign_volunteer(task_id, volunteer_id)
    if not updated_task:
        return jsonify({"error": "Task or volunteer not found."}), 404

    return jsonify(updated_task)


def update_task_status(task_id):
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")

    if not status:
        return jsonify({"error": "status is required."}), 400

    updated_task = get_store().update_task_status(task_id, status)
    if updated_task == "invalid_status":
        return jsonify({"error": "Invalid status supplied."}), 400
    if not updated_task:
        return jsonify({"error": "Task not found."}), 404

    return jsonify(updated_task)
