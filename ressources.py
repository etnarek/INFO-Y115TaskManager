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


def get_token():
    return request.cookies.get('token')


def get_random_string(length=64,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    import random
    random = random.SystemRandom()
    return ''.join(random.choice(allowed_chars) for i in range(length))


def connect_db():
    conn = psycopg2.connect(config.DB_URL, cursor_factory=psycopg2.extras.DictCursor)
    conn.autocommit = True
    return conn
