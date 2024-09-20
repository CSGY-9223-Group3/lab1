import datetime
import json
import logging
from functools import wraps
from logging.config import dictConfig

import jwt
from flask import Flask, Response, request

# In a production environment, this should be stored securely (e.g., as an environment variable)
SECRET_KEY = "cf4d68b60166f3e77fa11213797e2ee9ace4e813eead3fdbc522079ecee9beb2"


# Define the token_required decorator
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
        except jwt.exceptions.InvalidTokenError:
            return Response("Invalid token", 401)

        return f(current_user, *args, **kwargs)

    return decorated


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

app = Flask(__name__)

notes = {}
users = {}

logger = logging.getLogger(__name__)


@app.route("/")
def hello():
    return "<h1>Hello, World!</h1>"


@app.route("/notes/<note_id>", methods=["GET"])
@token_required
def handle_read_note(current_user, note_id):
    return read_note(note_id, current_user)


@app.route("/notes/<note_id>", methods=["POST"])
@token_required
def handle_create_note(current_user, note_id):
    is_public = request.args.get("public", default=False, type=is_true)
    return create_note(note_id, current_user, request.data.decode("utf-8"), is_public)


@app.route("/notes/<note_id>", methods=["PUT"])
@token_required
def handle_update_note(current_user, note_id):
    return update_note(note_id, current_user, request.data.decode("utf-8"))


@app.route("/notes/<note_id>", methods=["DELETE"])
@token_required
def handle_delete_note(current_user, note_id):
    return delete_note(note_id, current_user)


@app.route("/users", methods=["POST"])
def handle_create_user():
    new_token = generate_bearer_token(request.data.decode("utf-8"))
    users[request.data.decode("utf-8")] = new_token
    logger.info("Created user {user}".format(user=request.data.decode("utf-8")))
    return Response(new_token, status=200, mimetype="text/plain")


@app.route("/users", methods=["GET"])
def handle_get_user():
    return Response(json.dumps(users), status=200, mimetype="application/json")


# check if user is allowed to view the note
def can_user_read(user, note_id):
    if notes[note_id]["isPublic"] is True or user == notes[note_id]["author"]:
        return True
    return False


# check if user is the author
def can_user_modify(user, note_id):
    if user == notes[note_id]["author"]:
        return True
    return False


# check if query param value is truthy
def is_true(value):
    return value.lower() == "true"


def read_note(note_id, user):
    if note_id in notes:
        # found existing note
        if can_user_read(user, note_id):
            resp = {
                "id": str(note_id),
                "note": notes[note_id]["text"],
                "author": notes[note_id]["author"],
                "isPublic": notes[note_id]["isPublic"],
            }

            logger.info(
                "User '{user}' read note '{note_id}'".format(user=user, note_id=note_id)
            )
            return Response(json.dumps(resp), status=200, mimetype="application/json")
        else:
            # note is private and not owned by caller, return forbidden
            logger.warning(
                "User {user} attempted to read private note '{note_id}'; not authorized".format(
                    user=user, note_id=note_id
                )
            )
            return Response(status=403)
    else:
        # note doesn't exist, return not found
        logger.info(
            "User '{user}' attempted to read note '{note_id}'; note not found".format(
                user=user, note_id=note_id
            )
        )
        return Response(status=404)


def create_note(note_id, user, data, is_public):
    if note_id not in notes:
        # no existing note found, create

        notes[note_id] = {"text": data, "author": user, "isPublic": is_public}

        logger.info(
            "User '{user}' created note '{note_id}'".format(user=user, note_id=note_id)
        )
        return Response(
            '{"id":"' + note_id + '"}', status=201, mimetype="application/json"
        )
    else:
        # note already exists, return conflict
        logger.info(
            "User '{user}' attempted to create note '{note_id}'; note already exists".format(
                user=user, note_id=note_id
            )
        )
        return Response(status=409)


def update_note(note_id, user, data):
    if note_id in notes:
        # existing note found, update

        if can_user_modify(user, note_id):
            notes[note_id]["text"] = data

            logger.info(
                "User '{user}' updated note '{note_id}'".format(
                    user=user, note_id=note_id
                )
            )
            return Response(
                '{"id":"' + note_id + '"}', status=200, mimetype="application/json"
            )
        else:
            # note not owned by caller, return forbidden
            logger.warning(
                "User {user} attempted to update private note '{note_id}'; not authorized".format(
                    user=user, note_id=note_id
                )
            )
            return Response(status=403)
    else:
        # note doesn't exist, return not found
        logger.info(
            "User '{user}' attempted to update note '{note_id}'; note not found".format(
                user=user, note_id=note_id
            )
        )
        return Response(status=404)


def delete_note(note_id, user):
    if note_id in notes:
        # existing note found, update

        if can_user_modify(user, note_id):
            del notes[note_id]

            logger.info(
                "User '{user}' deleted note '{note_id}'".format(
                    user=user, note_id=note_id
                )
            )
            return Response(
                '{"id":"' + note_id + '"}', status=200, mimetype="application/json"
            )
        else:
            # note not owned by caller, return forbidden
            logger.warning(
                "User {user} attempted to delete private note '{note_id}'; not authorized".format(
                    user=user, note_id=note_id
                )
            )
            return Response(status=403)
    else:
        # note doesn't exist, return not found
        logger.info(
            "User '{user}' attempted to update note '{note_id}'; note not found".format(
                user=user, note_id=note_id
            )
        )
        return Response(status=404)


def generate_bearer_token(user_id):
    try:
        token = jwt.encode(
            {
                "sub": user_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        return token
    except Exception as e:
        return str(e)
