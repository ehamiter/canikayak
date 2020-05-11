import json
import requests

from flask import Flask
from flask import render_template
from flask_caching import Cache


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

SITE = '03433500'  # Harpeth River at Bellevue, TN

@app.route('/')
@app.route('/<string:site_id>')
@cache.cached(timeout=60)
def kayak_info(site_id=SITE):
    data = fetch_river_info(site_id)
    if data is None:
        return render_template("404.html"), 404

    site_name = str(data['value']['timeSeries'][0]['sourceInfo']['siteName']).title()
    discharge = int(data['value']['timeSeries'][0]['values'][0]['value'][0]['value'])
    gage = float(data['value']['timeSeries'][1]['values'][0]['value'][0]['value'])
    discharge_info = get_discharge_info(discharge)
    gage_info = get_gage_info(gage)

    data = {
        'site_name': site_name,
        'discharge': discharge,
        'discharge_info': discharge_info,
        'gage': gage,
        'gage_info': gage_info,
    }
    return render_template('base.html', **data)

def fetch_river_info(site_id):
    base = 'https://waterservices.usgs.gov/nwis/iv/'
    data_url = f'{base}?format=json&indent=on&sites={site_id}&parameterCd=00060,00065&siteStatus=all'
    try:
        data_r = requests.get(data_url)
        data = json.loads(data_r.content.decode('utf-8'))
    except ValueError:
        data = None
    return data

def get_discharge_info(discharge):
    result = None
    if discharge < 50:
        result = 'The river is running super duper slow.'
    if 50 < discharge < 150:
        result = 'The river is running pretty slow today.'
    if 150 < discharge < 300:
        result = 'The river is running a little slow today.'
    if 300 < discharge < 800:
        result = 'The river is running great today.'
    if 800 < discharge < 1100:
        result = 'The river is running fast today.'
    if 1100 < discharge < 2000:
        result = 'The river is running very fast today.'
    if 2000 < discharge < 4000:
        result = 'The river is running extremely fast today. Be careful.'
    if discharge > 4000:
        result = 'The river is probably running too fast to kayak today.'
    return result

def get_gage_info(gage):
    result = None
    if gage < 1.5:
        result ='It\'s bone dry and not possible to kayak.'
    if 1.5 < gage < 1.9:
        result = 'You\'ll probaby have to portage some.'
    if 1.9 < gage < 2.3:
        result = 'The water level is a little lower than average.'
    if 2.3 < gage < 2.8:
        result = 'The water level is right around the average.'
    if 2.8 < gage < 3.5:
        result = 'The water level is great, you should be fine.'
    if 3.5 < gage < 4.0:
        result = 'The water level is a little high.'
    if 4.0 < gage < 4.5:
        result = 'Be careful, the water is higher than normal.'
    if 4.5 < gage < 5.0:
        result = 'Water is very high. Might be risky.'
    if 5.0 < gage < 6.0:
        result = 'Probably not a good idea to kayak today.'
    if gage > 6.0:
        result = 'The water is too damn high!'
    return result

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/maps')
def maps():
    return render_template('maps.html')

@app.route('/harpeth_state_park')
def harpeth_state_park():
    return render_template('harpeth_state_park.html')

@app.route('/harpeth_franklin')
def harpeth_franklin():
    return render_template('harpeth_franklin.html')
