from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'


@app.route('/note/<id>', methods=["GET"])
def read_note(id):
    return 'read {}'.format(id)


@app.route('/note/<id>', methods=["PUT"])
def create_note(id):
    return 'put {}'.format(id)


@app.route('/note/<id>', methods=["POST"])
def update_note(id):
    return 'post {}'.format(id)


@app.route('/note/<id>', methods=["DELETE"])
def delete_note(id):
    return 'delete {}'.format(id)
