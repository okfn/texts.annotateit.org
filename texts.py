import bz2
import json
from logging import getLogger
from os import environ
from urlparse import urlparse

import redis

from flask import Flask, Blueprint, Response
from flask import abort, render_template, redirect, url_for
from flask import current_app, g, request

DEBUG = environ.get('DEBUG') is not None
REDIS = environ.get('REDISTOGO_URL', 'redis://localhost:6379')

log = getLogger(__name__)

# redis connection
rc = None

main = Blueprint('main', __name__)

@main.before_request
def before_request():
    g.debug = current_app.config['DEBUG']

def page_not_found(e):
    return render_template('404.html')

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/text', methods=['POST'])
def create_text():
    if 'text' not in request.form:
        return jsonify({'message': "No 'text' field in submitted POST!"}, status=400)

    text = request.form['text']

    # 1MiB limit on uploaded files for the moment
    if len(text) > 1024 * 1024:
        raise jsonify({'message': "Sorry, but you can't upload files > 1MiB at the moment! Aborted your request."}, status=400)

    cmp_text = bz2.compress(text)
    tid = rc.incr('id:text')
    rc.set('text:%s' % tid, 'bzip' + cmp_text)

    return redirect(url_for('.read_text', id=tid))

@main.route('/text/<id>')
def read_text(id):
    cmp_text = rc.get('text:%s' % id)
    if cmp_text is None:
        return abort(404)
    else:
        if cmp_text[:4] != 'bzip':
            raise RuntimeError("Unknown data format returned from database!")
        text = bz2.decompress(cmp_text[4:])
    return render_template('text.html', id=id, text=text)

def create_app():
    global rc

    app = Flask(__name__)
    app.config.from_object(__name__)

    rc = _init_redis(app.config['REDIS'])

    app.register_blueprint(main)
    app.errorhandler(404)(page_not_found)

    return app

def jsonify(obj, *args, **kwargs):
    res = json.dumps(obj, indent=None if request.is_xhr else 2)
    if 'callback' in request.args:
        return Response('%s(%s);' % (request.args['callback'], res), mimetype='text/javascript', *args, **kwargs)
    else:
        return Response(res, mimetype='application/json', *args, **kwargs)

def _init_redis(url):
    url = urlparse(url)

    # Make sure it's a redis database.
    if url.scheme:
        assert url.scheme == 'redis'

    # Attempt to resolve database id.
    try:
        db = int(url.path.replace('/', ''))
    except (AttributeError, ValueError):
        db = 0

    return redis.StrictRedis(host=url.hostname,
                             port=url.port,
                             db=db,
                             password=url.password)
