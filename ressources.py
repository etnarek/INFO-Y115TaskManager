from flask import g, url_for, redirect, request
import psycopg2
import psycopg2.extras
import config
from functools import wraps
import hashlib
import hmac


def after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f


def auth_required(fn):
    @wraps(fn)
    def outer(*args, **kwargs):
        if g.user.is_authenticated():
            return fn(*args, **kwargs)
        else:
            return redirect(url_for('users_api.login'))
    return outer


def get_userID():
    user_id = request.cookies.get('user_id')
    hashmac = request.cookies.get('hash')

    if user_id and hashmac:
        digest = hmac.new(config.SECRET.encode(), user_id.encode(), hashlib.sha512).hexdigest()
        if hmac.compare_digest(hashmac, digest):
            return int(user_id)
    return None


def connect_db():
    conn = psycopg2.connect(config.DB_URL, cursor_factory=psycopg2.extras.DictCursor)
    conn.autocommit = True
    return conn
