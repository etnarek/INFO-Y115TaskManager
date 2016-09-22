from flask import g, url_for, redirect
import psycopg2
import psycopg2.extras
import config
from functools import wraps


def auth_required(fn):
    @wraps(fn)
    def outer(*args, **kwargs):
        if g.user.is_authenticated():
            return fn(*args, **kwargs)
        else:
            return redirect(url_for('users_api.login'))
    return outer


def connect_db():
    conn = psycopg2.connect(config.DB_URL, cursor_factory=psycopg2.extras.DictCursor)
    conn.autocommit = True
    return conn
