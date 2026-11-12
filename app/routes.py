from flask import Blueprint, render_template

bp = Blueprint("todos", __name__)

@bp.route("/")
def index():
    """The page is a public shell with no data in it.

    Its JavaScript signs in through /auth/login and loads the todos from
    /api/todos with the Bearer header: the data is what is protected.
    """
    
    return render_template("index.html")