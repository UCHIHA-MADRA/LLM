from flask import Flask, request, redirect, session, jsonify
from requests_oauthlib import OAuth2Session
import sys
import os
from functools import wraps

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_OAUTH_DOMAIN
)


oauth_app = Flask(__name__)
app.secret_key = os.urandom(24)

# GitHub OAuth endpoints
AUTHORIZATION_BASE_URL = 'https://github.com/login/oauth/authorize'
TOKEN_URL = 'https://github.com/login/oauth/access_token'
USER_INFO_URL = 'https://api.github.com/user'

def get_github_oauth():
    return OAuth2Session(
        GITHUB_CLIENT_ID,
        redirect_uri=f"http://{GITHUB_OAUTH_DOMAIN}:3000/callback",
        scope=['read:user', 'user:email', 'read:org']
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'oauth_token' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def get_user_info(oauth_token):
    github = OAuth2Session(GITHUB_CLIENT_ID, token=oauth_token)
    return github.get(USER_INFO_URL).json()

@app.route('/login')
def github_login():
    github = get_github_oauth()
    authorization_url, state = github.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def github_callback():
    if 'oauth_state' not in session:
        return redirect('/login')
        
    github = get_github_oauth()
    try:
        token = github.fetch_token(
            TOKEN_URL,
            client_secret=GITHUB_CLIENT_SECRET,
            authorization_response=request.url
        )
        session['oauth_token'] = token
        
        # Get and store user info
        user_info = get_user_info(token)
        session['user_info'] = {
            'login': user_info.get('login'),
            'name': user_info.get('name'),
            'avatar_url': user_info.get('avatar_url'),
            'email': user_info.get('email')
        }
        
        return redirect('/')
    except Exception as e:
        session.clear()
        return f"Error during authentication: {str(e)}", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/profile')
@login_required
def profile():
    return jsonify(session.get('user_info', {}))

@app.route('/check-auth')
def check_auth():
    return jsonify({
        'authenticated': 'oauth_token' in session,
        'user': session.get('user_info', None)
    })

# Method to mount Gradio app
def mount_gradio_app(gradio_app):
    from gradio.routes import App
    gradio_app.auth = None  # Disable Gradio's built-in auth since we're using Flask
    app.mount_wsgi_app = lambda path, wsgi_app: None  # Placeholder
    return gradio_app


@oauth_app.route('/')
def home():
    return "Welcome to the application. Please <a href='/login'>login</a>."

if __name__ == "__main__":
    oauth_app.run(port=3000)