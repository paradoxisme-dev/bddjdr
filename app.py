from flask import Flask, render_template
from blueprint.external_auth import oauth_bp, oauth, oauth_ok
from blueprint.user import user_bp
from blueprint.game import game_bp
from database import initialize_database
from flask_login import LoginManager
from database import User
import os
import dotenv


dotenv.load_dotenv()
initialize_database()
login_manager = LoginManager()
login_manager.login_view = "user.login"
use_classic_login = os.getenv("USE_CLASSIC_LOGIN", "false").lower() == "true"


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
oauth.init_app(app)
login_manager.init_app(app)
app.register_blueprint(oauth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(game_bp)


@login_manager.user_loader
def load_user(user_id):
    return User.get(User.id == user_id)


@app.context_processor
def inject_oauth_ok():
    return dict(
        oauth_ok=oauth_ok,
        use_classic_login=use_classic_login
    )


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
