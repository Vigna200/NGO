from flask import jsonify

from database.db import get_store


def get_volunteers():
    return jsonify({"volunteers": get_store().get_volunteers()})
