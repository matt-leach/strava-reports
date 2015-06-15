import json

from flask import Flask, request, render_template

from stravalib.client import Client

import secret

app = Flask(__name__)


@app.route("/fitness")
def fitness():
    c = Client(access_token=secret.ACCESS_TOKEN)
    athlete = c.get_athlete()

    limit = request.args.get("limit", None)
    if limit:
        limit = int(limit)
    activities = list(c.get_activities(limit=limit))

    # Bit of a mess. Long run is 2. Old activities are 0, new activities are None
    ALLOWED_ACTIVITIES = [None, 0, 2, u"0", u"2"]

    activities = list(reversed([a for a in activities if a.average_heartrate and a.workout_type in ALLOWED_ACTIVITIES and a.type == "Run"]))

    activities = [a for a in activities if a.average_heartrate > 100 and 1000 * float(a.average_speed) / (a.average_heartrate - 60) < 80]  # Sanity for me

    vals = [1000 * float(a.average_speed) / (a.average_heartrate - 60) for a in activities]
    names = ["{} {}".format(a.name, a.start_date) for a in activities]

    smoothed_vals = []
    for index, val in enumerate(vals):
        slice = vals[max(0, index-3):index+3]
        smoothed_vals.append(sum(slice) / (0.0 + len(slice)))

    data = [names, vals, smoothed_vals]
    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)
