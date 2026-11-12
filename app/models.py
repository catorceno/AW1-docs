from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

def utcnow():
    return datetime.now(timezone.utc)

class Todo(db.Model):
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    due_date = db.Column(db.Date , nullable=True)
    priority = db.Column(db.Integer , nullable=False, default=1)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        # ¿qué jace !r?
        return f"<Todo {self.id} {self.title!r} completed={self.completed}>"

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False) # scrypt hash with a random salt: never the plain password
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # para cuando el usuario no existe
    @staticmethod
    def verify_hash(password_hash, password):
        return check_password_hash(password_hash, password)

    def __repr__(self):
        return f"<User {self.id} {self.username!r}>"
    