from flask import render_template

from main import app


@app.route("/")
def home():
    url = Client().authorization_url(client_id=app.config['STRAVA_ID'],
                                     redirect_uri="http://localhost:5000/auth",
                                     approval_prompt="force",
                                     )
    return render_template('index.html', auth_url=url)


from views.auth import *
from views.reports import *
