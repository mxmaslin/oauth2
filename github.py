import secrets

import requests

from dotenv import load_dotenv
from flask import Flask, request, render_template_string, session

from constants import (
    GITHUB_CLIENT_ID, AUTHORIZE_URL, TOKEN_URL, API_URL_BASE, BASE_URL
)

load_dotenv()

app = Flask(__name__)
app.secret_key = 'my_secret_key'


def api_request(url):
    headers = {
        'Accept': 'application/vnd.github.v3+json, application/json',
        'User-Agent': 'https://example-app.com/',
    }

    access_token = session.get('access_token')
    if access_token:
        headers.update({'Authorization': f'Bearer {access_token}'})

    response = requests.get(url, headers=headers)
    return response.json()


@app.route('/login')
def login():
    action = request.args.get('action')
    access_token = session.get('access_token')
    if not action:
        if access_token:
            return render_template_string("""
                <h3>Logged In</h3>
                <p><a href='?action=repos'>View Repos</a></p>
                <p><a href="?action=logout">Log Out</a></p>      
            """)
        return render_template_string("""
            <h3>Not logged in</h3>
            <p><a href='?action=login'>Log In</a></p>
        """)
    elif action == 'login':
        session.pop('access_token', None)
        state = secrets.token_urlsafe(16)
        session['state'] = state
        query_params = {
            'response_type': 'code',
            'client_id': GITHUB_CLIENT_ID,
            'redirect_uri': BASE_URL,
            'scope': 'user,public_repo',
            'state': state
        }
        response = requests.get(AUTHORIZE_URL, params=query_params)
        return response.content


if __name__ == '__main__':
    app.run(debug=True)
