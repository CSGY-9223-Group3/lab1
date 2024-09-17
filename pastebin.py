import datetime

from flask import Flask, Response, request
import json
import logging
import jwt

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

notes = {}
users = {}


logger = logging.getLogger(__name__)


@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'


@app.route('/notes/<note_id>', methods=["GET"])
def handle_read_note(note_id):
    if validate_user(request):
        user = request.authorization.username  # TODO - replace basic auth user with bearer token user
        return read_note(note_id, user)
    else:
        # user not known, return unauthorized
        logger.warning("Unknown user attempted to read note '{note_id}'".format(note_id=note_id))
        return Response(status=401)


@app.route('/notes/<note_id>', methods=["POST"])
def handle_create_note(note_id):
    if validate_user(request):
        user = request.authorization.username  # TODO - replace basic auth user with bearer token user
        # check if public or private note
        is_public = request.args.get('public', default=False, type=is_true)
        return create_note(note_id, user, request.data.decode("utf-8"), is_public)
    else:
        # user not known, return unauthorized
        logger.warning("Unknown user attempted to write note '{note_id}'".format(note_id=note_id))
        return Response(status=401)


@app.route('/notes/<note_id>', methods=["PUT"])
def handle_update_note(note_id):
    if validate_user(request):
        user = request.authorization.username  # TODO - replace basic auth user with bearer token user
        update_note(note_id, user, request.data.decode("utf-8"))
    else:
        # user not known, return unauthorized
        logger.warning("Unknown user attempted to update note '{note_id}'".format(note_id=note_id))
        return Response(status=401)


@app.route('/notes/<note_id>', methods=["DELETE"])
def handle_delete_note(note_id):
    if validate_user(request):
        user = request.authorization.username  # TODO - replace basic auth user with bearer token user
        delete_note(note_id, user)
    else:
        # user not known, return unauthorized
        logger.warning("Unknown user attempted to read delete '{note_id}'".format(note_id=note_id))
        return Response(status=401)


@app.route('/users', methods=["POST"])
def handle_create_user():
    new_token = generate_bearer_token(request.data.decode("utf-8"))
    users[request.data.decode("utf-8")] = new_token

    logger.info("Created user {user}".format(user=request.data.decode("utf-8")))
    return Response(new_token, status=200, mimetype='text/plain')


@app.route('/users', methods=["GET"])
def handle_get_user():
    return Response(json.dumps(users), status=200, mimetype='application/json')


# check if auth is provided and user exists
def validate_user(request):
    # TODO - update this function to look at bearer token instead of basic auth
    if (request.authorization and
            request.authorization.username and
            request.authorization.username in users):
        return True
    return False


# check if user is allowed to view the note
def can_user_read(user, note_id):
    if (notes[note_id]["isPublic"] is True or
            user == notes[note_id]["author"]):
        return True
    return False


# check if user is the author
def can_user_modify(user, note_id):
    if user == notes[note_id]["author"]:
        return True
    return False


# check if query param value is truthy
def is_true(value):
    return value.lower() == 'true'


def read_note(note_id, user):
    if note_id in notes:
        # found existing note
        if can_user_read(user, note_id):
            resp = {
                "id": str(note_id),
                "note": notes[note_id]["text"],
                "author": notes[note_id]["author"],
                "isPublic": notes[note_id]["isPublic"]
            }

            logger.info("User '{user}' read note '{note_id}'".format(user=user, note_id=note_id))
            return Response(json.dumps(resp), status=200, mimetype='application/json')
        else:
            # note is private and not owned by caller, return forbidden
            logger.warning("User {user} attempted to read private note '{note_id}'; not authorized".format(user=user, note_id=note_id))
            return Response(status=403)
    else:
        # note doesn't exist, return not found
        logger.info("User '{user}' attempted to read note '{note_id}'; note not found".format(user=user, note_id=note_id))
        return Response(status=404)


def create_note(note_id, user, data, is_public):
    if note_id not in notes:
        # no existing note found, create

        notes[note_id] = {
            "text": data,
            "author": user,
            "isPublic": is_public
        }

        logger.info("User '{user}' created note '{note_id}'".format(user=user, note_id=note_id))
        return Response('{"id":"' + note_id + '"}', status=201, mimetype='application/json')
    else:
        # note already exists, return conflict
        logger.info("User '{user}' attempted to create note '{note_id}'; note already exists".format(user=user, note_id=note_id))
        return Response(status=409)


def update_note(note_id, user, data):
    if note_id in notes:
        # existing note found, update

        if can_user_modify(user, note_id):
            notes[note_id]["text"] = data

            logger.info("User '{user}' updated note '{note_id}'".format(user=user, note_id=note_id))
            return Response('{"id":"' + note_id + '"}', status=200, mimetype='application/json')
        else:
            # note not owned by caller, return forbidden
            logger.warning("User {user} attempted to update private note '{note_id}'; not authorized".format(user=user, note_id=note_id))
            return Response(status=403)
    else:
        # note doesn't exist, return not found
        logger.info("User '{user}' attempted to update note '{note_id}'; note not found".format(user=user, note_id=note_id))
        return Response(status=404)


def delete_note(note_id, user):
    if note_id in notes:
        # existing note found, update

        if can_user_modify(user, note_id):
            del notes[note_id]

            logger.info("User '{user}' deleted note '{note_id}'".format(user=user, note_id=note_id))
            return Response('{"id":"' + note_id + '"}', status=200, mimetype='application/json')
        else:
            # note not owned by caller, return forbidden
            logger.warning("User {user} attempted to delete private note '{note_id}'; not authorized".format(user=user, note_id=note_id))
            return Response(status=403)
    else:
        # note doesn't exist, return not found
        logger.info("User '{user}' attempted to update note '{note_id}'; note not found".format(user=user, note_id=note_id))
        return Response(status=404)


def generate_bearer_token(user_id):
    try:
        return jwt.encode(
            {
                "sub": user_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
            },
            'secret',
            algorithm='HS256'
        )
    except Exception as e:
        return e
