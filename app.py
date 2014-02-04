__author__ = 'dhan'

import flask
from werkzeug.wsgi import wrap_file
import re
import pymongo
import gridfs
import bson
import time
from flask.views import MethodView

from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app = flask.Flask(__name__)
app.debug = True
import werkzeug
app.url_map.converters['regex'] = RegexConverter

conn = pymongo.Connection()
datadb = conn["files"]

@app.route("/")
def index():
    return flask.send_from_directory("static", "index.html")

@app.route("/upload", methods=("get", "post"))
def upload():
    restype = "video"
    result = dict()
    result["resource"] = restype

    # Process get request
    if flask.request.method == "GET":
        resid = flask.request.args.get("id", "new")
        if resid == "new":
            result["id"] = str(bson.ObjectId())
        else:
            id = bson.ObjectId(resid)
            gf = gridfs.GridFS(datadb, restype)
            fileobj = gf.get(id)
            data = wrap_file(flask.request.environ, fileobj)
            response = flask.current_app.response_class(
                data,
                mimetype=fileobj.content_type,
                direct_passthrough=True)
            response.content_length = fileobj.length
            response.last_modified = fileobj.upload_date
            response.set_etag(fileobj.md5)
            response.cache_control.max_age = 0
            response.cache_control.s_max_age = 0
            response.cache_control.public = True
            response.headers['Content-Disposition'] = 'attachment; filename=' + fileobj.filename
            response.make_conditional(flask.request)
            return response

        result["success"] = "GET request successful"
        return flask.jsonify(result)

    if flask.request.method == "POST":
        result["id"] = flask.request.form["flowIdentifier"]
        result["success"] = "POST request successful"
        result["current_chunk"] = int(flask.request.form["flowChunkNumber"])
        result["total_chunks"] = int(flask.request.form["flowTotalChunks"])
        result["filename"] = flask.request.form["flowFilename"]
        f = flask.request.files["file"]
        first = False

        if result["current_chunk"] == 1:
            first = True
            result["first"] = 1
            # Create a file
            gf = gridfs.GridFS(datadb, restype)
            afile = gf.new_file(chunk_size=1024*1024, filename=result["filename"], _id=bson.ObjectId(result["id"]))
            afile.write(f.read())
            afile.close()

        if not first:
            obj = {}
            obj["n"] = result["current_chunk"] - 1
            obj["files_id"] = bson.ObjectId(result["id"])
            obj["data"] = bson.Binary(f.read())

            datadb[restype + ".chunks"].insert(obj)
            fileobj = datadb[restype + ".files"].find_one({"_id" : obj["files_id"]})
            datadb[restype + ".files"].update({"_id" : obj["files_id"]}, {"$set" : {"length" : fileobj["length"] + len(obj["data"])}})


        if result["current_chunk"] == result["total_chunks"]:
            last = True
            result["last"] = 1
            # Add the attachment id to the
#             if not sessobj.has_key("attachments"):
#                 sessobj["attachments"] = [ {"ref" : ObjectId(resid), "pos" : 0}]
#                 sessobj.validate()
#                 sessobj.save()
# #                print "Inserted attachments", str(sessobj["attachments"])
#             else:
#                 size_before = len(sessobj["attachments"])
#                 sessobj["attachments"].append({"ref" : ObjectId(resid), "pos" : size_before + 1})
#                 sessobj.validate()
#                 sessobj.save()
# #                print "Appended to  attachments", str(sessobj["attachments"])


        print result

    return flask.jsonify(result)
