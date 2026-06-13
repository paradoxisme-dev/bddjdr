from flask import Blueprint, url_for, session, redirect, render_template
from flask_login import login_user
from authlib.integrations.flask_client import OAuth
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from database import User, OauthIdentity
from peewee import IntegrityError
import os
import dotenv

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])

oauth_ok = []

oauth = OAuth()

oauth_bp = Blueprint('oauth', __name__)

dotenv.load_dotenv()

discord_data = {
    "client_id": os.getenv("DISCORD_CLIENT_ID", None),
    "client_secret": os.getenv("DISCORD_CLIENT_SECRET", None),
    "redirect_uri": os.getenv("DISCORD_REDIRECT_URI", None),
}

if not all(discord_data.values()):
    discord_data = None

if discord_data:
    oauth_ok.append('discord')
    discord = oauth.register(
        name='discord',
        client_id=discord_data["client_id"],
        client_secret=discord_data["client_secret"],
        access_token_url='https://discord.com/api/oauth2/token',
        authorize_url='https://discord.com/api/oauth2/authorize',
        userinfo_endpoint='https://discord.com/api/users/@me',
        redirect_uri=discord_data["redirect_uri"],
        client_kwargs={'scope': 'identify'}
    )
    @oauth_bp.route('/discord/login')
    def login_discord():
        return discord.authorize_redirect(url_for('oauth.authorize_discord', _external=True))

    @oauth_bp.route('/oauth/discord/redirect')
    def authorize_discord():
        token = discord.authorize_access_token()
        user_info = discord.get('https://discord.com/api/users/@me').json()
        existant_user = User.select().join(OauthIdentity).where(
            (OauthIdentity.service == 'discord') &
            (OauthIdentity.service_user_id == user_info['id'])
        ).first()
        if not existant_user:
            session['user_info'] = user_info
            return redirect(url_for('oauth.complete_registration'))
        else:
            login_user(existant_user)
        return redirect(url_for('home'))

    @oauth_bp.route('/oauth/discord/register', methods=['GET', 'POST'])
    def complete_registration():
        user_info = session.get('user_info')
        if not user_info:
            return redirect(url_for('oauth.login_discord'))
        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                new_user = User(username=form.username.data)
                new_user.save()
                oauth_identity = OauthIdentity(
                    service='discord',
                    service_user_id=user_info['id'],
                    user=new_user
                )
                oauth_identity.save()
                login_user(new_user)
                session.pop('user_info', None)
                return redirect(url_for('home'))
            except IntegrityError:
                if User.select().where((User.username == form.username.data)).exists():
                    form.username.errors.append('Nom d\'utilisateur déjà utilisé.')
        else:
            form.username.data = user_info.get('username', '') if user_info else ''
        return render_template('oauth/discord_registration.html', form=form)
