from flask import Flask, Response, request
import json

app = Flask(__name__)


notes = {}


@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'


@app.route('/note/<id>', methods=["GET"])
def read_note(id):
    if id in notes:
        # found existing note
        resp = {
            "id": str(id),
            "note": notes[id]["text"],
            "author": notes[id]["author"]
        }
        return Response(json.dumps(resp), status=200, mimetype='application/json')
    else:
        # note doesn't exist, return not found
        return Response(status=404)


@app.route('/note/<id>', methods=["POST"])
def create_note(id):
    if id not in notes:
        # no existing note found, create
        notes[id] = {
            "text": request.data.decode("utf-8"),
            "author": "default"
            }
        return Response('{"id":"' + id + '"}', status=201, mimetype='application/json')
    else:
        # note already exists, return conflict
        return Response(status=409)


@app.route('/note/<id>', methods=["PUT"])
def update_note(id):
    if id in notes:
        # existing note found, update
        notes[id] = {
            "text": request.data.decode("utf-8"),
            "author": "default"
            }
        return Response('{"id":"' + id + '"}', status=200, mimetype='application/json')
    else:
        # note doesn't exist, return not found
        return Response(status=404)


@app.route('/note/<id>', methods=["DELETE"])
def delete_note(id):
    if id in notes:
        # existing note found, update
        del notes[id]
        return Response('{"id":"' + id + '"}', status=200, mimetype='application/json')
    else:
        # note doesn't exist, return not found
        return Response(status=404)
