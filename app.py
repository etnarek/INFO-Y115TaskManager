from flask import Flask, render_template, g, session, Markup
from flask_bootstrap import Bootstrap
import config
import models
import humanize
from datetime import date, timedelta
import markdown

from ressources import connect_db, auth_required

from users import users_api
from task import task_api
import forms


app = Flask(__name__)
app.secret_key = config.SECRET
Bootstrap(app)


@app.before_request
def open_db():
    g.db = connect_db()
    g.cursor = g.db.cursor()


@app.before_request
def get_user_cookie():
    if "user_id" in session:
        query = "SELECT * FROM users WHERE id=%s"
        g.cursor.execute(query, [session['user_id']])
        user = models.User.from_dict(g.cursor.fetchone())
        g.user = user
    else:
        g.user = models.AnonymousUser()


@app.teardown_request
def close_db(exception):
    cursor = getattr(g, 'cursor', None)
    if cursor is not None:
        cursor.close()

    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403


@app.context_processor
def inject_user():
    return dict(user=g.user)


app.register_blueprint(users_api, url_prefix='/users')
app.register_blueprint(task_api, url_prefix='/task')


@app.route("/")
@auth_required
def index():
    query = """
    SELECT task.* from task WHERE user_id=%s ORDER BY created
    """

    tasks = models.list_of(query, [g.user.id], models.Task)

    return render_template('index.html', tasks=tasks, taskForm=forms.Task())


@app.template_filter('humanize_date')
def humanize_date(d):
    humanize.i18n.activate('fr')
    diff = date.today() - d
    if(diff < timedelta(hours=24)):
        return "aujourd'hui"

    return humanize.naturaltime(diff)


@app.template_filter('markdown')
def markdown_f(string):
    return Markup(markdown.markdown(string))

if __name__ == "__main__":
    app.run(debug=config.DEBUG, host="0.0.0.0", port=8000)
