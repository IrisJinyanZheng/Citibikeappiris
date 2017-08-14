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

from citibikeapp import app

DATABASE = '/var/www/html/citibikeapp/citibikeapp/citibike_change.db'

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows


def convertTime(et):
    """'2017-06-01 11:41:53 AM' to '2017-06-01 11:41:53' """ 
    hour = int(et[11:13])
    if et.find('PM') != -1 and hour != 12:
        dateString = et[:10]
        hour = hour + 12
        et = dateString + ' ' + str(hour) + et[13:19]
    elif et.find('AM') != -1 and hour == 12:
        dateString = et[:10]
        hour = 0
        et = dateString + ' ' + '0'+str(hour) + et[13:19]
    else:
        et = et[:19]

    return et


def updateStations():
    url = 'https://feeds.citibikenyc.com/stations/stations.json'
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    EXECUTION_TIME = data['executionTime']
    stationList = data['stationBeanList']

    output_cols = ['sID','stationName','availableDocks','totalDocks', 'latitude', 'longitude','statusValue','statusKey','availableBikes', 'stAddress1', 'stAddress2', 'city', 'postalCode', 'location','altitude','testStation','LCT', 'landMark','executionTime']

    df = pd.DataFrame(stationList)

    df['exeTime'] = convertTime(EXECUTION_TIME)
    df['sID'] = df['id']
    df['LCT'] = df['lastCommunicationTime']
    df['executionTime'] = df ['exeTime']

    con = connect_to_database()
  
    df[output_cols].to_sql('Stations', con, index=False, if_exists='replace')

    con.commit()
    con.close()

def getNYtimenow():
    tz = pytz.timezone('America/New_York')
    time = str(datetime.now(tz))[:19]
    return time

def datetimeStringToObject(timeString):
    try:
        year = int(timeString[:4])
        month = int(timeString[5:7])
        day = int(timeString[8:10])
        hour = int(timeString[11:13])
        minute = int(timeString[14:16])
        result = datetime(year, month, day, hour, minute)
        return result
    except:
        return None

def timeStringToObject(timeString):
    try:
        # year = datetime.now().year
        # month = datetime.now().month
        # day = datetime.now().day
        hour = int(timeString[11:13])
        minute = int(timeString[14:16])
        result = datetime.today().replace(hour=hour, minute=minute, second=0, microsecond=0)
        return result
    except:
        return None

def notSignedIn(vID):
    """Return true is the drivers did not enter vehicle ID, 
    return False if the drivers have entered the vehicle ID"""
    if str(vID) == '0':
        return True
    return False


def resetEstComp(cur, vID):
    """estimate completion time goes to 0""" 
    cur.execute("""UPDATE OpenTasks SET estComplete = null WHERE vID = ? """,[vID])

def getNextFixOrderNum(vID):
    """return the integer which is one larger than the order number of the last fixed task"""
    orderNum = execute_query("""SELECT Count(*) FROM OpenTasks where vID = ? and fixTask = 1""", [vID])[0][0]
    orderNum = int(orderNum) + 1
    return orderNum

def fixOrderBeforeInsert(cur,vID,orderNum):
    """Increment later tasks' order number by 1, orderNum is the order of the inserted task
    should be called before inserting the task """
    cur.execute("""UPDATE OpenTasks SET orderNum = orderNum + 1 WHERE vID = ? and orderNum >= ?""",[vID, orderNum])