#!/usr/bin/env python

from flask import Flask
import gevent.wsgi
import gevent.monkey
import werkzeug.serving

from app import app
gevent.monkey.patch_all()
app.debug = True

@werkzeug.serving.run_with_reloader
def run_server():
    ws = gevent.wsgi.WSGIServer(listener=('0.0.0.0', 8000),
                                application=app)
    ws.serve_forever()

if __name__ == "__main__":
    run_server()

