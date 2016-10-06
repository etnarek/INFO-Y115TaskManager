from flask_wtf import Form
from flask_wtf.html5 import EmailField
from wtforms import TextField, SubmitField, validators, PasswordField


class Login(Form):
    username = TextField("Nom d'utilisateur")
    password = PasswordField('Mot de passe')

    submit = SubmitField("Envoyer")


class User(Form):
    username = TextField("Nom d'utilisateur")
    email = EmailField("Adresse mail")
    password = PasswordField('Mot de passe', [
        validators.Required(),
        validators.EqualTo('confirm', message='Les mots de passe doivent être identiques')
    ])
    confirm = PasswordField('Mot de passe (à nouveau)')

    submit = SubmitField("Envoyer")


class PasswordUser(Form):
    password = PasswordField('Mot de passe', [
        validators.Required(),
        validators.EqualTo('confirm', message='Les mots de passe doivent être identiques')
    ])
    confirm = PasswordField('Mot de passe (à nouveau)')

    submit = SubmitField("Envoyer")


class Task(Form):
    text = TextField("Text", [validators.Length(min=2, max=500)])
    submit = SubmitField("Envoyer")
