# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-04 11:54:30
# @Last Modified by:   sy
# @Last Modified time: 2017-08-27 21:33:00


from collections import Counter
import csv
import sqlite3
import time
import logging
from datetime import datetime, timedelta
from flask import Flask, request, g, jsonify, abort, make_response, redirect, url_for, send_from_directory, render_template, flash, Response, session
import pandas as pd
import pytz
import json
import urllib
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, UserMixin, login_required,login_user, current_user, logout_user
from wtforms import Form, BooleanField, StringField, validators
import numpy as np
from globalfunc import * 

from citibikeapp import app


############################ MAP MAP MAP MAP MAP ############################################################################################
@app.route('/stationgeojson')
@login_required
def stationgeojson():
    """Return the geojson of all stations except the Jersey stations in file map/JerseyStations.txt"""
    url = 'http://feeds.citibikenyc.com/stations/stations.json'
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    stations = data['stationBeanList']
    NJS = []
    f=open('/var/www/html/citibikeapp/citibikeapp/map/JerseyStations.txt','r')
    for line in f:
        index = line.index(":")
        s = line[1:index]
        NJS.append(s)
    f.close()
    #NJS = ["3183", "3184", "3185", "3186", "3187", "3188", "3189", "3190", "3191", "3192", "3193", "3194", "3195", "3196", "3197", "3198", "3199", "3200", "3201", "3202", "3203", "3205", "3206", "3207", "3209", "3210", "3211", "3212", "3213", "3214", "3215", "3216", "3217", "3220", "3225", "3267", "3268", "3269", "3270", "3271", "3272", "3273", "3274", "3275", "3276", "3277", "3278", "3279", "3280", "3281"]
    NYGeojson = { "type": "FeatureCollection", "features": []}
    for s in stations:
        if not (str(s["id"]) in NJS):
            Feature2 = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [s["longitude"],s["latitude"]]}, "properties": s }
            NYGeojson["features"].append(Feature2)
    result = json.dumps(NYGeojson)
    return result

@app.route('/vehiclegeojson')
@login_required
def vehiclegeojson():
    """Return the geojson of where all vehicles are"""
    con = connect_to_database()
    sql = """SELECT * FROM Vehicles"""
    df = pd.read_sql(sql, con)
    con.close()

    vehicles = df.to_dict(orient='records')

    VehicleGeojson = { "type": "FeatureCollection", "features": []}
    for v in vehicles:
        if str(v["vID"]) != "-111":
            Feature = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [v["vACLongitude"],v["vACLatitude"]]}, "properties": v }
            VehicleGeojson["features"].append(Feature)
    result = json.dumps(VehicleGeojson)
    return result

@app.route('/taskgeojson')
@login_required
def taskgeojson():
    """Return the geojson of the tasks(from vehicle current location to next task station)"""
    con = connect_to_database()
    sql = """SELECT * FROM Vehicles"""
    df = pd.read_sql(sql, con)
    con.close()

    vehicles = df.to_dict(orient='records')

    TaskGeojson = { "type": "FeatureCollection", "features": []}
    for v in vehicles:
        if str(v["vID"]) != "-111":
            Feature = {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[v["vACLongitude"],v["vACLatitude"]],[v["vNXLongitude"],v["vNXLatitude"]]]}, "properties": v }
            TaskGeojson["features"].append(Feature)
    result = json.dumps(TaskGeojson)
    return result
