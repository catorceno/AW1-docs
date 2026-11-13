from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from .auth import requires_auth
from .extensions import db
from .models import Todo

bp = Blueprint("todos", __name__)

# Decorator order matters: @bp.route goes on top so Flask registers the
# already-protected function.
@bp.route("/")
@requires_auth("get:todos")
def index(payload):
    # print(payload)
    # print(session["access_token"])
    todos = Todo.query.order_by(Todo.completed.asc(), Todo.created_at.desc()).all()
    return render_template("index.html", todos=todos)

@bp.route("/todos", methods=["POST"])
@requires_auth("post:todos")
def create(payload):
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip() or None
    
    if not title:
        flash("Title is required.", "error")
        return redirect(url_for("todos.index"))
    
    db.session.add(Todo(title=title, description=description))
    db.session.commit()
    flash("Todo created.", "success")
    return redirect(url_for("todos.index"))

@bp.route("/todos/<int:todo_id>/toggle", methods=["POST"])
@requires_auth("patch:todos")
def toggle(payload, todo_id):
    todo = db.get_or_404(Todo, todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for("todos.index"))

@bp.route("/todos/<int:todo_id>/edit", methods=["GET", "POST"])
@requires_auth("patch:todos")
def edit(payload, todo_id):
    todo = db.get_or_404(Todo, todo_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        
        if not title:
            flash("Title is required.", "error")
            return render_template("edit.html", todo=todo)
        
        todo.title = title
        todo.description = request.form.get("description", "").strip() or None
        db.session.commit()
        flash("Todo updated.", "success")
        return redirect(url_for("todos.index"))
    
    return render_template("edit.html", todo=todo)

@bp.route("/todos/<int:todo_id>/delete", methods=["POST"])
@requires_auth("delete:todos")
def delete(payload, todo_id):
    todo = db.get_or_404(Todo, todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash("Todo deleted.", "success")
    return redirect(url_for("todos.index"))