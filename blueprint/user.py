from flask import Blueprint, redirect, url_for, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from peewee import IntegrityError
from database import User
from flask_login import login_user, logout_user

user_bp = Blueprint('user', __name__, url_prefix='/user')


class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur ou email', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if '@'  in form.username.data:
            user = User.select().where(User.email == form.username.data).first()
        else:
            user = User.select().where(User.username == form.username.data).first()
        if user is None:
            form.username.errors.append('Nom d\'utilisateur ou email non trouvé.')
        elif not user.check_password(form.password.data):
            form.password.errors.append('Mot de passe incorrect.')
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form)


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            new_user = User(username=form.username.data, email=form.email.data)
            new_user.set_password(form.password.data)
            new_user.save()
            return redirect(url_for('user.login'))
        except IntegrityError:
            if User.select().where((User.username == form.username.data)).exists():
                form.username.errors.append('Nom d\'utilisateur ou email déjà utilisé.')
            elif User.select().where((User.email == form.email.data)).exists():
                form.email.errors.append('Nom d\'utilisateur ou email déjà utilisé.')
    return render_template('register.html', form=form)


@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
