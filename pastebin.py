from flask import Flask, Response, request
import json

app = Flask(__name__)


notes = {}


@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'


@app.route('/note/<note_id>', methods=["GET"])
def read_note(note_id):
    if note_id in notes:
        # found existing note
        resp = {
            "id": str(note_id),
            "note": notes[note_id]["text"],
            "author": notes[note_id]["author"]
        }
        return Response(json.dumps(resp), status=200, mimetype='application/json')
    else:
        # note doesn't exist, return not found
        return Response(status=404)


@app.route('/note/<note_id>', methods=["POST"])
def create_note(note_id):
    if note_id not in notes:
        # no existing note found, create
        notes[note_id] = {
            "text": request.data.decode("utf-8"),
            "author": "default"
            }
        return Response('{"id":"' + note_id + '"}', status=201, mimetype='application/json')
    else:
        # note already exists, return conflict
        return Response(status=409)


@app.route('/note/<note_id>', methods=["PUT"])
def update_note(note_id):
    if note_id in notes:
        # existing note found, update
        notes[note_id] = {
            "text": request.data.decode("utf-8"),
            "author": "default"
            }
        return Response('{"id":"' + note_id + '"}', status=200, mimetype='application/json')
    else:
        # note doesn't exist, return not found
        return Response(status=404)


@app.route('/note/<note_id>', methods=["DELETE"])
def delete_note(note_id):
    if note_id in notes:
        # existing note found, update
        del notes[note_id]
        return Response('{"id":"' + note_id + '"}', status=200, mimetype='application/json')
    else:
        # note doesn't exist, return not found
        return Response(status=404)
