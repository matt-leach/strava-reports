import datetime
import json

from flask import Flask, request, render_template, redirect, session

from stravalib.client import Client


app = Flask(__name__)
app.config.from_pyfile('settings.py')


@app.route("/")
def home():
    c = Client()
    url = c.authorization_url(client_id=app.config['STRAVA_ID'], redirect_uri="http://localhost:5000/auth")
    return render_template('index.html', url=url)


@app.route("/auth")
def auth():
    code = request.args.get("code")
    c = Client()
    token = c.exchange_code_for_token(app.config['STRAVA_ID'], app.config['STRAVA_SECRET'], code)
    session["token"] = token
    c.access_token = token
    a = c.get_athlete()
    session["athlete"] = {"firstname": a.firstname, "picture": a.profile_medium}
    return redirect("/")


@app.route("/fitness")
def fitness():
    c = Client(access_token=session["token"])
    athlete = c.get_athlete()

    try:
        limit = int(request.args.get("limit"))
    except (TypeError, ValueError):
        limit = None
    try:
        smooth = int(request.args.get("smooth")) / 2
    except (ValueError, TypeError):
        smooth = 3

    activities = list(c.get_activities(limit=limit))

    # Bit of a mess. Long run is 2. Old activities are 0, new activities are None
    ALLOWED_ACTIVITIES = [None, 0, 2, u"0", u"2"]

    activities = list(reversed([a for a in activities if a.average_heartrate and a.workout_type in ALLOWED_ACTIVITIES and a.type == "Run"]))

    activities = [a for a in activities if a.average_heartrate > 100 and 1000 * float(a.average_speed) / (a.average_heartrate - 60) < 80]  # Sanity for me

    vals = [1000 * float(a.average_speed) / (a.average_heartrate - 60) for a in activities]
    names = ["{} {}".format(a.name, a.start_date) for a in activities]

    smoothed_vals = []
    for index, val in enumerate(vals):
        slice = vals[max(0, index-smooth):index+smooth+1]
        smoothed_vals.append(sum(slice) / (0.0 + len(slice)))

    vals_and_dist = [(1000 * float(a.average_speed) / (a.average_heartrate - 60), float(a.distance)) for a in activities]
    dist_smoothed_vals = []
    for index, val in enumerate(vals):
        slice = vals_and_dist[max(0, index-smooth):index+smooth+1]
        tot = 0
        dist = 0
        for run in slice:
            tot += run[0] * run[1]
            dist += run[1]
        dist_smoothed_vals.append(tot / float(dist))

    data = [names, vals, smoothed_vals, dist_smoothed_vals]
    return render_template('fitness.html', data=data)


@app.route("/mileage")
def mileage():
    c = Client(access_token=secret.ACCESS_TOKEN)

    activities = list(c.get_activities(limit=200))

    date = activities[-1].start_date.date()
    dates = []
    week_vals = []
    month_vals = []
    while date <= datetime.datetime.now().date():
        dates.append(datetime.datetime.combine(date, datetime.datetime.min.time()))
        min_week_date = date - datetime.timedelta(days=7)
        min_month_date = date - datetime.timedelta(days=30)
        M_PER_MILE = 1609
        week_vals.append(sum(float(a.distance) / M_PER_MILE for a in activities if a.start_date.date() <= date and a.start_date.date() > min_week_date))
        month_vals.append((7 / 30.0) * sum(float(a.distance) / M_PER_MILE for a in activities if a.start_date.date() <= date and a.start_date.date() > min_month_date))

        date += datetime.timedelta(days=1)

    data = [dates, week_vals, month_vals]
    return render_template('mileage.html', data=data)


if __name__ == "__main__":
    app.run(debug=True)
