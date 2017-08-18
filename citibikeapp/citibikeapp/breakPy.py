# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-04 23:28:02
# @Last Modified by:   sy
# @Last Modified time: 2017-08-18 14:14:11

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



# completing breaks operation in iosresponsePy.py, /complete
############################ Manage Breaks ############################################################################################

@app.route('/breaks.json')
@login_required
def breaksJson():
    con = connect_to_database()
    sql = """SELECT Breaks.vID, Breaks.tType, Tasks.tName, Breaks.publishTime FROM Breaks 
        Left JOIN Tasks on Tasks.tType = Breaks.tType""" 
        # left JOIN Vehicles on Vehicles.vID = Breaks.vID ,Vehicles.startTime, Vehicles.endTime
    df = pd.read_sql(sql, con)
    con.close()

    resultJson = df.to_json(orient='records')
    return resultJson

@app.route('/manageBreak')
@login_required
def manageBreak():
    con = connect_to_database()
    sql = """SELECT Vehicles.vID, Vehicles.vName, Vehicles.dID1,  d1.dName as dName1, Vehicles.dID2,  d2.dName as dName2, Vehicles.capacity, 
            Vehicles.vBike, Vehicles.tID, Vehicles.startTime, Vehicles.endTime,
            ds1.signInTime as signInTime1, ds1.signOutReqTime as signOutReqTime1, ds1.lunchCount as lunchCount1, ds1.breakCount as breakCount1,
            ds2.signInTime as signInTime2, ds2.signOutReqTime as signOutReqTime2, ds2.lunchCount as lunchCount2, ds2.breakCount as breakCount2
            FROM Vehicles             
            left JOIN Drivers AS d1 on d1.dID = Vehicles.dID1
            left JOIN Drivers AS d2 on d2.dID = Vehicles.dID2
            left JOIN DriversShift AS ds1 on ds1.dID = Vehicles.dID1
            left JOIN DriversShift AS ds2 on ds2.dID = Vehicles.dID2""" 
    df = pd.read_sql(sql, con)
    con.close()

    vehicles  = df.to_records()
    return render_template("table_breaks_manage.html", vehicles  = vehicles )

@app.route('/updateDefaultBreaks', methods=['GET', 'POST'])
@login_required
def updateDefaultBreaks():
    print "update default breaks form submitted"
    vID = request.form['vID']
    lunchBreak = request.form['lunchBreak']
    shortBreak1 = request.form['shortBreak1']
    shortBreak2 = request.form['shortBreak2'] 
    breaks = request.form.getlist('breaks') 

    vInfo = execute_query("""SELECT startTime from Vehicles where vID = ?""",[vID])
    try:
        startTime = vInfo[0][0]
        startTime = datetimeStringToObject(startTime)
        lunchBreak = str(startTime+timedelta(minutes=float(lunchBreak)*60))[11:19]
        shortBreak1 = str(startTime+timedelta(minutes=float(shortBreak1)*60))[11:19]
        shortBreak2 = str(startTime+timedelta(minutes=float(shortBreak2)*60))[11:19]
    except:
        # either fail because startTime is empty or None
        return "can't assign breaks to not in shift vehicle"
    print "got all attributes"

    con = connect_to_database()
    cur = con.cursor()

    cur.execute("""DELETE FROM Breaks where vID = ?""",[vID])

    for tType in breaks:
    	if int(tType) == 16: 
    		cur.execute("""INSERT INTO Breaks (vID, tType, publishTime) values (?,?,?);""",[vID,tType,lunchBreak])
    	if int(tType) == 17: 
    		cur.execute("""INSERT INTO Breaks (vID, tType, publishTime) values (?,?,?);""",[vID,tType,shortBreak1])
    	if int(tType) == 18: 
    		cur.execute("""INSERT INTO Breaks (vID, tType, publishTime) values (?,?,?);""",[vID,tType,shortBreak2])

    con.commit()
    con.close()

    print "updated default breaks"
    return redirect('/manageBreak')
    

@app.route('/delayBreak/tID=<tID>&du=<duration>')
@login_required
def delayBreak(tID,duration):
    """Delay break with task ID tID to <duration> minutes from NOW"""
    print "delaying break by updating default break"

    task = execute_query(
        """SELECT orderNum, vID, sID, tType FROM OpenTasks where tID = ?
        """, [tID])
    preOrder = task[0][0]
    vID = task[0][1]
    sID = task[0][2]  
    tType = task[0][3]
    duration = int(duration)
    #can't delay less than 5 minutes
    if duration<5:
        duration = 5
        
    tz = pytz.timezone('America/New_York')
    newTime = str(datetime.now(tz) + timedelta(minutes=duration))[11:19]

    print "got all attributes"

    con = connect_to_database()
    cur = con.cursor()

    cur.execute("""DELETE FROM OpenTasks where tID = ? """,[tID])
    cur.execute("""DELETE FROM Breaks where vID = ? and tType = ?""",[vID, tType])
    cur.execute("""INSERT INTO Breaks (vID, tType, publishTime) values (?,?,?);""",[vID,tType,newTime])

    con.commit()
    con.close()

    print "delayed breaks"
    return redirect('/manageTask') 
