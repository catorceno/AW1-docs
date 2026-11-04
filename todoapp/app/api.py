from flask import Blueprint, jsonify

from .models import Todo

api_bp = Blueprint("api", __name__)

@api_bp.get("/todos")
def list_todos():
    return jsonify([
        {"id": t.id, "title": t.title, "completed": t.completed}
        for t in Todo.query.all()
    ])