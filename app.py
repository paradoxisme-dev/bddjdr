from flask import Flask, render_template
from external_auth import oauth_bp, oauth, oauth_ok
from database import initialize_database
import os
import dotenv

dotenv.load_dotenv()
initialize_database()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
oauth.init_app(app)
app.register_blueprint(oauth_bp)

@app.context_processor
def inject_oauth_ok():
    return dict(oauth_ok=oauth_ok)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
