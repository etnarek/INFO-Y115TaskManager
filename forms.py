from flask_wtf import Form
from flask_wtf.html5 import EmailField
from wtforms import TextField, SubmitField, validators, PasswordField


class Login(Form):
    username = TextField("Nom d'utilisateur")
    password = PasswordField('Mot de passe')

    submit = SubmitField("Envoyer")


class User(Form):
    username = TextField("Nom d'utilisateur", [validators.Length(min=6, max=250)])
    email = EmailField("Adresse mail", [validators.DataRequired(), validators.Email(), validators.Length(max=250)])
    password = PasswordField('Mot de passe', [
        validators.Required(),
        validators.EqualTo('confirm', message='Les mots de passe doivent être identiques'),
        validators.Length(min=8)
    ])
    confirm = PasswordField('Mot de passe (à nouveau)')

    submit = SubmitField("Envoyer")


class PasswordUser(Form):
    password = PasswordField('Mot de passe', [
        validators.Required(),
        validators.EqualTo('confirm', message='Les mots de passe doivent être identiques'),
        validators.Length(min=8)
    ])
    confirm = PasswordField('Mot de passe (à nouveau)')

    submit = SubmitField("Envoyer")


class Task(Form):
    text = TextField("Text", [validators.Length(min=2, max=500)])
    submit = SubmitField("Envoyer")
