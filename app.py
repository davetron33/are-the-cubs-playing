from flask import Flask, render_template
from datetime import datetime, timezone, timedelta
import logging
import jmespath
import requests
import json
import ast

logging.basicConfig(level=logging.DEBUG)

utc_minus_5 = timezone(timedelta(hours=-5))
now = datetime.now(utc_minus_5)
gamedate = str(now.strftime("%m/%d/%Y"))

headers= {
    'X-Message-for-SRE':'Hi, Im just a very bored python dev. Sorry if this is hammering your API',
}

response = requests.get(f'https://www.livesportsontv.com/api/fixtures/grouped?day=2026-04-03&dayBreakHour=0&tz=America/Chicago', headers=headers).json()

r_data = str(response[0])
sports = ast.literal_eval(r_data)
sports = json.dumps(sports)

fixture = json.loads(sports)

home_team_slug = jmespath.search('sports[].sports[].leagues[].fixtures[?contains(fixture_slug `chicago-cubs`)].home_team_slug', fixture)
visiting_team_slug = jmespath.search('sports[].sports[].leagues[].fixtures[?contains(fixture_slug `chicago-cubs`)].visiting_team_slug', fixture)

matchup = jmespath.search( 
    'sports[].sports[].leagues[].fixtures[?contains(fixture_slug `chicago-cubs`)].title[]', fixture
)
matchup = " ".join(matchup)

venue = jmespath.search( 
    'sports[].sports[].leagues[].fixtures[?contains(fixture_slug `chicago-cubs`)].venue[]', fixture
)
venue = " ".join(venue)

channels = jmespath.search(
    'sports[].sports[].leagues[].fixtures[?contains(fixture_slug `chicago-cubs`)].channels[][].shortname', fixture
)
chans = list(channels)
home_team = jmespath.search(
    'sports[].sports[].leagues[].fixtures[?contains(fixture_slug `chicago-cubs`)].home_team[]', fixture
)
home_team = " ".join(home_team)
visiting_team = jmespath.search(
    'sports[].sports[].leagues[].fixtures[?contains(fixture_slug `chicago-cubs`)].visiting_team[]', fixture
)
visiting_team = " ".join(visiting_team)

start_time = jmespath.search('sports[].sports[].leagues[].fixtures[?contains(fixture_slug `chicago-cubs`)].localtime[][].time[]', fixture)
start_time = " ".join(start_time)


def isThereAGameToday():
    if matchup == "":
        return False
    else:
        return True

isThereAGameToday = isThereAGameToday()

logging.debug(isThereAGameToday)
logging.debug(matchup)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
def index():
    return render_template('index.html', \
                           items=chans, \
                           home_team=home_team, \
                           visiting_team=visiting_team, \
                           venue=venue, \
                           gamedate=gamedate, \
                           start_time=start_time, \
                           isThereAGameToday=isThereAGameToday
                           )

if __name__ == "__main__":
    app.run(debug=True)

