
from flask import Blueprint, render_template, request, g, redirect, url_for, abort
import forms
import models

from ressources import auth_required


comment_api = Blueprint('task_api', __name__)


@comment_api.route("/add/", methods=["POST"])
@auth_required
def add_comment(epk, uid):
    form = forms.Task(request.form)
    if request.method == 'POST' and form.validate():
        task = models.Task()
        form.populate_obj(task)

        task.user_id = uid
        task.insert(g.cursor)

    return redirect(url_for('index'))


@comment_api.route("/edit/<int:tid>", methods=["GET", "POST"])
@auth_required
def edit_comment(tid):
    query = """
    SELECT {} FROM task
    WHERE task.id=%s
    """.format(models.Task.star())

    g.cursor.execute(query, [tid])
    data = g.cursor.fetchone()
    if not data:
        return abort(404)

    task = models.Task.from_dict(data)
    uid = task.user_id
    date = task.date

    if g.user.id == uid:
        form = forms.Task(request.form, obj=task)
        if request.method == 'POST' and form.validate():
            form.populate_obj(task)
            task.user_id = uid
            task.date = date
            task.update(g.cursor)
            return redirect(url_for('index'))
    else:
        return abort(401)

    return render_template('edit_task.html', form=form)


@comment_api.route("/delete/<int:tid>")
@auth_required
def delete(tid):
    queryGet = """
    SELECT {} FROM task
    WHERE task.id=%s
    """.format(models.Task.star())
    queryDel = """
    DELETE FROM task
    WHERE id=%s
    """

    g.cursor.execute(queryGet, [tid])
    data = g.cursor.fetchone()
    if not data:
        return abort(404)

    task = models.Task.from_dict(data)
    uid = task.user_id

    if g.user.id == uid:
        g.cursor.execute(queryDel, [tid])
        return redirect("index")
    return abort(401)
