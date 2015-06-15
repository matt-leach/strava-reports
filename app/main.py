from flask import Flask
from stravalib.client import Client

import secret

app = Flask(__name__)


@app.route("/")
def hello():
    c = Client(access_token=secret.ACCESS_TOKEN)
    a = c.get_athlete()
    return "Hello {}!".format(a.firstname)

if __name__ == "__main__":
    app.run(debug=True)
