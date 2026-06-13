from flask import Flask, render_template, redirect
from external_auth import oauth_bp, oauth, oauth_ok
from database import initialize_database
from flask_login import LoginManager, logout_user
from database import User
import os
import dotenv

dotenv.load_dotenv()
initialize_database()
login_manager = LoginManager()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
oauth.init_app(app)
login_manager.init_app(app)
app.register_blueprint(oauth_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

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

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
