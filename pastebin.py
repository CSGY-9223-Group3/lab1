import datetime
import json
import logging
import os
import secrets
from functools import wraps
from logging.config import dictConfig

import jwt
from flask import (
    Flask,
    Response,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)
from flask_wtf import FlaskForm
from html_sanitizer import Sanitizer
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError


# Configure logging
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

logger = logging.getLogger(__name__)

# Retrieve or generate SECRET_KEY
# SECRET_KEY = os.environ.get("SECRET_KEY")
SECRET_KEY = "2odi1RzpU1v18BkSecw="
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(32)
    logger.warning(
        "No SECRET_KEY set for Flask application; using a temporary key. "
        "Set the SECRET_KEY environment variable for production."
    )

# Initialize the HTML sanitizer
sanitizer = Sanitizer()

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["WTF_CSRF_TIME_LIMIT"] = None  # Disable CSRF token expiration for simplicity

# In-memory storage (use a database for production)
notes = {}
users = {}

# ----------------------------
# Authentication Decorators
# ----------------------------


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return Response("Invalid token format", 401)

        if not token:
            return Response("Token is missing", 401)

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = data["sub"]
        except jwt.ExpiredSignatureError:
            return Response("Token has expired", 401)
        except jwt.InvalidTokenError:
            return Response("Invalid token", 401)

        return f(current_user, *args, **kwargs)

    return decorated


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(session["user_id"], *args, **kwargs)

    return decorated


# ----------------------------
# Flask-WTF Forms
# ----------------------------


class RegistrationForm(FlaskForm):
    user_id = StringField("User ID", validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Register")

    def validate_user_id(self, field):
        if field.data in users:
            raise ValidationError("User ID already exists.")


class LoginForm(FlaskForm):
    user_id = StringField("User ID", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class NoteForm(FlaskForm):
    note_id = StringField("Note ID", validators=[DataRequired(), Length(min=1, max=50)])
    text = TextAreaField("Note Text", validators=[DataRequired()])
    is_public = BooleanField("Public")
    submit = SubmitField("Submit")


class EditNoteForm(FlaskForm):
    text = TextAreaField("Note Text", validators=[DataRequired()])
    is_public = BooleanField("Public")
    submit = SubmitField("Update")


# ----------------------------
# Helper Functions
# ----------------------------


def generate_api_key():
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def generate_jwt_token(user_id):
    """Generate a JWT token for the user."""
    try:
        token = jwt.encode(
            {
                "sub": user_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return None


def can_user_read(user, note_id):
    """Check if the user can read the note."""
    if notes[note_id]["isPublic"] or user == notes[note_id]["author"]:
        return True
    return False


def can_user_modify(user, note_id):
    """Check if the user can modify the note."""
    return user == notes[note_id]["author"]


def sanitize_input(data):
    """Sanitize user input to prevent XSS."""
    return sanitizer.sanitize(data)


# ----------------------------
# Routes
# ----------------------------


@app.route("/")
def home():
    return render_template("home.html")


# User Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = sanitize_input(form.user_id.data)
        password = form.password.data  # In production, hash the password

        # Generate API key
        api_key = generate_api_key()

        # Store user
        users[user_id] = {
            "password": password,  # Store hashed password in production
            "api_key": api_key,
        }

        logger.info(f"Registered new user '{user_id}'")

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


# User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = sanitize_input(form.user_id.data)
        password = form.password.data

        user = users.get(user_id)
        if user and user["password"] == password:
            # Successful login
            session["user_id"] = user_id
            session["api_key"] = user["api_key"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("list_notes"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("login.html", form=form)


# User Logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("api_key", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("home"))


# List Notes
@app.route("/notes")
@login_required
def list_notes(current_user):
    user_notes = []
    for note_id, note in notes.items():
        if can_user_read(current_user, note_id):
            user_notes.append(
                {
                    "id": note_id,
                    "text": note["text"],
                    "author": note["author"],
                    "isPublic": note["isPublic"],
                }
            )
    return render_template("notes.html", notes=user_notes, user=current_user)


# Create Note
@app.route("/notes/create", methods=["GET", "POST"])
@login_required
def create_note_route(current_user):
    form = NoteForm()
    if form.validate_on_submit():
        note_id = form.note_id.data
        text = form.text.data
        is_public = form.is_public.data

        if note_id in notes:
            flash("Note ID already exists.", "danger")
            return render_template("create_note.html", form=form)

        sanitized_text = sanitize_input(text)

        notes[note_id] = {
            "text": sanitized_text,
            "author": current_user,
            "isPublic": is_public,
        }

        logger.info(f"User '{current_user}' created note '{note_id}'")

        flash("Note created successfully!", "success")
        return redirect(url_for("list_notes"))
    return render_template("create_note.html", form=form)


# View Note
@app.route("/notes/<note_id>")
@login_required
def view_note_route(current_user, note_id):
    note = notes.get(note_id)
    if note:
        if can_user_read(current_user, note_id):
            return render_template(
                "view_note.html",
                note={
                    "id": note_id,
                    "text": note["text"],
                    "author": note["author"],
                    "isPublic": note["isPublic"],
                },
            )
        else:
            flash("You are not authorized to view this note.", "danger")
            return redirect(url_for("list_notes"))
    else:
        flash("Note not found.", "warning")
        return redirect(url_for("list_notes"))


# Edit Note
@app.route("/notes/<note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note_route(current_user, note_id):
    note = notes.get(note_id)
    if not note:
        flash("Note not found.", "warning")
        return redirect(url_for("list_notes"))
    if not can_user_modify(current_user, note_id):
        flash("You are not authorized to edit this note.", "danger")
        return redirect(url_for("list_notes"))

    form = EditNoteForm()
    if form.validate_on_submit():
        text = form.text.data
        is_public = form.is_public.data

        sanitized_text = sanitize_input(text)

        notes[note_id]["text"] = sanitized_text
        notes[note_id]["isPublic"] = is_public

        logger.info(f"User '{current_user}' updated note '{note_id}'")

        flash("Note updated successfully!", "success")
        return redirect(url_for("view_note_route", note_id=note_id))
    elif request.method == "GET":
        form.text.data = note["text"]
        form.is_public.data = note["isPublic"]
    return render_template("edit_note.html", form=form, note_id=note_id)


# Delete Note
@app.route("/notes/<note_id>/delete", methods=["POST"])
@login_required
def delete_note_route(current_user, note_id):
    note = notes.get(note_id)
    if not note:
        flash("Note not found.", "warning")
        return redirect(url_for("list_notes"))
    if not can_user_modify(current_user, note_id):
        flash("You are not authorized to delete this note.", "danger")
        return redirect(url_for("list_notes"))

    del notes[note_id]

    logger.info(f"User '{current_user}' deleted note '{note_id}'")

    flash("Note deleted successfully!", "success")
    return redirect(url_for("list_notes"))


# ----------------------------
# API Routes
# ----------------------------


# Create Note via API
@app.route("/api/notes", methods=["POST"])
@token_required
def api_create_note(current_user):
    data = request.get_json()
    if not data:
        return Response("Invalid JSON data", status=400)

    note_id = data.get("id")
    text = data.get("text")
    is_public = data.get("isPublic", False)

    if not note_id or not text:
        return Response("Missing 'id' or 'text' fields", status=400)

    if note_id in notes:
        return Response("Note ID already exists", status=409)

    sanitized_text = sanitize_input(text)

    notes[note_id] = {
        "text": sanitized_text,
        "author": current_user,
        "isPublic": is_public,
    }

    logger.info(f"User '{current_user}' created note '{note_id}' via API")

    return Response(
        json.dumps({"id": note_id}), status=201, mimetype="application/json"
    )


# Read Note via API
@app.route("/api/notes/<note_id>", methods=["GET"])
@token_required
def api_read_note(current_user, note_id):
    note = notes.get(note_id)
    if note:
        if can_user_read(current_user, note_id):
            resp = {
                "id": note_id,
                "text": note["text"],
                "author": note["author"],
                "isPublic": note["isPublic"],
            }
            logger.info(f"User '{current_user}' read note '{note_id}' via API")
            return Response(json.dumps(resp), status=200, mimetype="application/json")
        else:
            logger.warning(
                f"User '{current_user}' unauthorized to read note '{note_id}' via API"
            )
            return Response("Forbidden", status=403)
    else:
        logger.info(
            f"User '{current_user}' attempted to read non-existent note '{note_id}' via API"
        )
        return Response("Not Found", status=404)


# Update Note via API
@app.route("/api/notes/<note_id>", methods=["PUT"])
@token_required
def api_update_note(current_user, note_id):
    note = notes.get(note_id)
    if not note:
        return Response("Not Found", status=404)
    if not can_user_modify(current_user, note_id):
        return Response("Forbidden", status=403)

    data = request.get_json()
    if not data:
        return Response("Invalid JSON data", status=400)

    text = data.get("text")
    is_public = data.get("isPublic")

    if text is None or is_public is None:
        return Response("Missing 'text' or 'isPublic' fields", status=400)

    sanitized_text = sanitize_input(text)

    notes[note_id]["text"] = sanitized_text
    notes[note_id]["isPublic"] = is_public

    logger.info(f"User '{current_user}' updated note '{note_id}' via API")

    return Response(
        json.dumps({"id": note_id}), status=200, mimetype="application/json"
    )


# Delete Note via API
@app.route("/api/notes/<note_id>", methods=["DELETE"])
@token_required
def api_delete_note(current_user, note_id):
    note = notes.get(note_id)
    if not note:
        return Response("Not Found", status=404)
    if not can_user_modify(current_user, note_id):
        return Response("Forbidden", status=403)

    del notes[note_id]

    logger.info(f"User '{current_user}' deleted note '{note_id}' via API")

    return Response(
        json.dumps({"id": note_id}), status=200, mimetype="application/json"
    )


# List Public Notes via API
@app.route("/api/notes", methods=["GET"])
@token_required
def api_list_notes(current_user):
    public_notes = [
        {
            "id": nid,
            "text": note["text"],
            "author": note["author"],
            "isPublic": note["isPublic"],
        }
        for nid, note in notes.items()
        if note["isPublic"] or note["author"] == current_user
    ]
    return Response(json.dumps(public_notes), status=200, mimetype="application/json")


# User Registration via API
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    if not data:
        return Response("Invalid JSON data", status=400)

    user_id = sanitize_input(data.get("user_id"))
    password = data.get("password")

    if not user_id or not password:
        return Response("Missing 'user_id' or 'password'", status=400)

    if user_id in users:
        return Response("User ID already exists", status=409)

    api_key = generate_api_key()
    users[user_id] = {"password": password, "api_key": api_key}  # Hash in production

    logger.info(f"Registered new user '{user_id}' via API")

    return Response(
        json.dumps({"api_key": api_key}), status=201, mimetype="application/json"
    )


# User Login via API
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    if not data:
        return Response("Invalid JSON data", status=400)

    user_id = sanitize_input(data.get("user_id"))
    password = data.get("password")

    if not user_id or not password:
        return Response("Missing 'user_id' or 'password'", status=400)

    user = users.get(user_id)
    if user and user["password"] == password:
        token = generate_jwt_token(user_id)
        if token:
            logger.info(f"User '{user_id}' logged in via API")
            return Response(
                json.dumps({"token": token}), status=200, mimetype="application/json"
            )
        else:
            return Response("Token generation failed", status=500)
    else:
        return Response("Invalid credentials", status=401)


# Get User Info via API
@app.route("/api/users/<user_id>", methods=["GET"])
@token_required
def api_get_user(current_user, user_id):
    if current_user != user_id:
        return Response("Forbidden", status=403)

    user = users.get(user_id)
    if user:
        safe_user_data = {
            "user_id": user_id,
            # "api_key": user["api_key"],
        }
        return Response(
            json.dumps(safe_user_data), status=200, mimetype="application/json"
        )
    else:
        return Response("User not found", status=404)


# ----------------------------
# Run the Application
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True)
