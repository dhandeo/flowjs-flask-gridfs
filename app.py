__author__ = 'dhan'

import flask
import time

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def index():
    return flask.send_from_directory("static", "index.html")


@app.route("/upload", methods=("get", "post"))
def upload():

    stri = "Got chunk: " + str(flask.request.form["flowChunkNumber"]) + " of " + str(flask.request.form["flowFilename"])
    app.logger.error(stri)

    # app.logger.error(str(flask.request.files.keys()))
    # app.logger.error(str(flask.request.files.keys()))
    f = flask.request.files["file"]

    # return flask.jsonify(response)
    return flask.Response(flask.request.form["flowChunkNumber"])

