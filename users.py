from flask import Blueprint, render_template, request, g, redirect, url_for, make_response
import psycopg2
import psycopg2.extras
import forms
import config
import models
from hashlib import pbkdf2_hmac

from ressources import auth_required, get_random_string, get_token, after_this_request

users_api = Blueprint('users_api', __name__)


def gen_token(user_id):
    ok = False
    while not ok:
        try:
            token = get_random_string()
            token_querry = "INSERT INTO token (token, user_id) VALUES (%s, %s)"
            g.cursor.execute(token_querry, [token, user_id])
            ok = True
        except psycopg2.IntegrityError as e:
            pass

    @after_this_request
    def set_id_cookie(response):
        response.set_cookie('token', str(token))


@users_api.route("/login", methods=['GET', 'POST'])
def login():
    form = forms.Login(request.form)
    if request.method == "POST" and form.validate():
        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        username = form.username.data
        password = form.password.data

        salt = config.SALT + username
        hash = pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)

        g.cursor.execute(query, [username, hash])
        row = g.cursor.fetchone()
        if row:
            user = models.User.from_dict(row)

            gen_token(user.id)
            return redirect(url_for('index'))
        else:
            form.username.errors.append("Couple utilisateur/mot de passe inconnu")

    return render_template('login.html', form=form)


@users_api.route("/register", methods=['GET', 'POST'])
def register():
    form = forms.User(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        salt = config.SALT + username
        hash = pbkdf2_hmac("sha256", form.password.data.encode(), salt.encode(), 100000)

        user = models.User(
            username=username,
            password=hash,
            email=form.email.data,
        )
        try:
            user.insert()
        except psycopg2.IntegrityError as e:
            if "(username)" in str(e):
                form.username.errors.append("Ce nom d'utilisateur est déjà pris")
            if "(email)" in str(e):
                form.email.errors.append("Cet email est déjà utilisé par un autre utilisateur")
        else:
            gen_token(user.id)
            return redirect(url_for('index'))
    return render_template('register.html', form=form)


@users_api.route("/password", methods=['GET', 'POST'])
@auth_required
def password():
    form = forms.PasswordUser(request.form)
    if request.method == 'POST' and form.validate():
        query = "SELECT * FROM users WHERE id=%s"
        user = models.get_or_404(query, [g.user.id], models.User)
        salt = config.SALT + user.username
        hash = pbkdf2_hmac("sha256", form.password.data.encode(), salt.encode(), 100000)
        user.password = hash
        user.update()

        return redirect(url_for('index'))

    return render_template('edit_user.html', form=form)


@users_api.route("/logout")
def logout():
    token = get_token()
    resp = make_response(redirect(url_for('index')))
    if token:
        querryDelToken = "DELETE FROM token WHERE token=%s"
        g.cursor.execute(querryDelToken, [token])
        resp.set_cookie('token', "", expires=0)
    return resp
