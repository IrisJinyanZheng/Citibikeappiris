# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-03 21:37:45
# @Last Modified by:   sy
# @Last Modified time: 2017-08-04 22:10:20

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

############################ Assign Tasks ############################################################################################

@app.route('/inputTask', methods=['POST', 'GET'])
@login_required
def inputTask():
    print "accessing assign task form"
    tasks = execute_query(
        """SELECT * FROM Tasks
        """)
    vehicles = execute_query(
        """SELECT vID, vName, dID1, dID2 FROM Vehicles
        """)
    updateStations()
    stations = execute_query(
        """SELECT sID, stationName, availableDocks, availableBikes, totalDocks FROM Stations
        """)

    df = pd.read_csv('/var/www/html/citibikeapp/citibikeapp/datafiles/bike.csv')
    bikes_ID = np.array(df['id']).tolist()
    return render_template("task_form_2.html", bikes = bikes_ID, tasks = tasks, title = "Assign Task", vehicles = vehicles, stations = stations)

@app.route('/assignTask/', methods=['GET', 'POST'])
@login_required
def assignTask():
    print "assign task form submitted"

    vID = request.form['vID']

    fromS = request.form['fromS']
    toS = request.form['toS']
    bikeNum = request.form['bikeNum'] 
    completionTime = request.form['completionTime']
    comment = request.form['comment'] 
    isMove = request.form['isMove']
    priority = request.form['priority']

    dID1 = -111
    dID2 = -111

    if completionTime == "0000-00-00 00:00:00":
        completionTime = None
    if fromS == '-1':
        fromS = None
    if toS == '-1':
        toS = None
    if vID != '-111':
        dIDs = execute_query("""SELECT dID1, dID2 FROM Vehicles Where vID = ?
         """,
         [vID])

        dID1 = dIDs[0][0]
        dID2 = dIDs[0][1]

    #find the order number of the last fixed task, then increment 1
    orderNum = getNextFixOrderNum(vID)

    print "got all attributes"

    tz = pytz.timezone('America/New_York')
    publishTime = str(datetime.now(tz))[:19]

    con = connect_to_database()
    cur = con.cursor()

    resetEstComp(cur, vID)

    if isMove == '0':
        tType = request.form['tType']
        fixOrderBeforeInsert(cur,vID,orderNum)
        cur.execute("""INSERT INTO OpenTasks (vID, tType, sID,bikeNum, completionTime, comment, publishTime, dID1, dID2, priority, orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,0,1)
         """,
         [vID, tType, fromS, bikeNum, completionTime, comment, publishTime, dID1, dID2, priority, orderNum])


    if isMove == '1':
        fixOrderBeforeInsert(cur,vID,orderNum)
        cur.execute("""INSERT INTO OpenTasks (vID, tType, sID,bikeNum, completionTime, comment, publishTime, dID1, dID2, priority, orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,0,1)
         """,
         [vID, 1, fromS, bikeNum, completionTime, comment, publishTime, dID1, dID2,priority,orderNum])

        orderNum = orderNum + 1

        fixOrderBeforeInsert(cur,vID,orderNum)
        cur.execute("""INSERT INTO OpenTasks (vID, tType, sID,bikeNum, completionTime, comment, publishTime, dID1, dID2,priority,orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,0,1)
         """,
         [vID, 3, toS, bikeNum, completionTime, comment, publishTime, dID1, dID2,priority,orderNum])

        tType = 3

    con.commit()
    con.close()

    print "assigned task"
    result = execute_query("""SELECT * FROM OpenTasks Where vID = ? and tType = ? and comment = ? and publishTime = ?
         """,
         [vID, tType, comment, publishTime])

    return redirect('/success?vID='+str(vID)+'&tID='+str(result[0][0]))

@app.route('/success', methods=['GET', 'POST'])
@login_required
def success():
    print "adding task success"
    vID = request.args.get('vID')
    tID = request.args.get('tID')

    if vID == '-111':
        vID = "Any"
    
    return render_template("taskAdded.html",tID = tID, vID = vID, title = "Task Assigned")

