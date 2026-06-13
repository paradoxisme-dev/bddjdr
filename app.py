from flask import Flask, render_template, redirect, url_for
from external_auth import oauth_bp, oauth, oauth_ok
from database import initialize_database
from flask_login import LoginManager, logout_user, login_user
from database import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from peewee import IntegrityError
import os
import dotenv


dotenv.load_dotenv()
initialize_database()
login_manager = LoginManager()
login_manager.login_view = "login"

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur ou email', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
oauth.init_app(app)
login_manager.init_app(app)
app.register_blueprint(oauth_bp)


@login_manager.user_loader
def load_user(user_id):
    return User.get(User.id == user_id)


@app.context_processor
def inject_oauth_ok():
    return dict(oauth_ok=oauth_ok)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            new_user = User(username=form.username.data, email=form.email.data)
            new_user.set_password(form.password.data)
            new_user.save()
            return redirect(url_for('login'))
        except IntegrityError:
            if User.select().where((User.username == form.username.data)).exists():
                form.username.errors.append('Nom d\'utilisateur ou email déjà utilisé.')
            elif User.select().where((User.email == form.email.data)).exists():
                form.email.errors.append('Nom d\'utilisateur ou email déjà utilisé.')
    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
