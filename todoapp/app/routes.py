from flask import Blueprint, flash, redirect, render_template, request, url_for

from .extensions import db
from .models import Todo

# como tiene un nombre propio (todos) permite modularidad para crear otro blueprint admin por ejemplo
bp = Blueprint("todos", __name__)

# index, create are endpoints of the blueprint todos, that's why later: todos.index
@bp.route("/")
def index():
    todos = Todo.query.order_by(Todo.completed.asc(), Todo.created_at.desc()).all()
    return render_template("index.html", todos=todos)

@bp.route("/todos", methods=["POST"])
def create():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Title is required", "error")
        return redirect(url_for("todos.index"))

    description = request.form.get("description", "").strip() or None
    db.session.add(Todo(title=title, description=description))
    db.session.commit()
    flash("Todo created.", "success")
    return redirect(url_for("todos.index"))


@bp.route("/todos/<int:todo_id>/edit", methods=["GET", "POST"])
def edit(todo_id):
    todo = db.get_or_404(Todo, todo_id)  # busca por id; si no existe responde 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required", "error")
            return redirect(url_for("todos.edit", todo_id=todo.id))

        todo.title = title
        todo.description = request.form.get("description", "").strip() or None
        todo.completed = "completed" in request.form  # un checkbox sin marcar no se envia
        db.session.commit()
        flash("Todo updated.", "success")
        return redirect(url_for("todos.index"))

    # GET: muestra el formulario con los datos actuales
    return render_template("edit.html", todo=todo)


@bp.route("/todos/<int:todo_id>/toggle", methods=["POST"])
def toggle(todo_id):
    todo = db.get_or_404(Todo, todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for("todos.index"))


@bp.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete(todo_id):
    todo = db.get_or_404(Todo, todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash("Todo deleted.", "success")
    return redirect(url_for("todos.index"))
