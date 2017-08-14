# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-04 12:17:30
# @Last Modified by:   sy
# @Last Modified time: 2017-08-10 14:53:11


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


############################ Task Type ############################################################################################

@app.route('/inputTaskType', methods=['POST', 'GET'])
@login_required
def inputTaskType():
    print "accessing assign task type form"
    return render_template("task_type_form.html", title = "Assign Task Type")

@app.route('/assignTaskType', methods=['GET', 'POST'])
@login_required
def addTaskType():
    print "assign task form submitted"
    tName = request.form['tName']
    deltaBike = request.form['deltaBike']

    print "got all attributes"

    con = connect_to_database()
    cur = con.cursor()

    cur.execute("""INSERT INTO Tasks (tName, deltaBike) VALUES (?,?)""",[tName,deltaBike])
    tTypes = cur.execute("""SELECT * from (SELECT tType from Tasks ORDER BY tType DESC) ORDER BY tType DESC""")
    temp = str(tTypes.fetchone()[0])
    cur.execute("""ALTER TABLE Drivers ADD Field"""+ temp +""" INTEGER;""")
    cur.execute("""UPDATE Drivers Set Field"""+ temp +"""=0;""")

    con.commit()
    con.close()

    print "added task type"
    result = execute_query("""SELECT * FROM Tasks Where tName = ? """,[tName])

    return redirect('/success2?tName='+ tName+'&tType='+str(result[0][0]))

@app.route('/success2', methods=['GET', 'POST'])
@login_required
def success2():
    print "adding task type success"
    tName = request.args.get('tName')
    tType = request.args.get('tType')
    return render_template("taskTypeAdded.html",tName = tName, tType = tType, title = "Task Type Assigned") 

########################### Add Driver ############################################################################################
@app.route('/addDriverForm')
@login_required
def addDriverForm():
    tasktypes = execute_query(
        """SELECT tType, tName FROM Tasks
        """)
    drivers = execute_query(
        """SELECT dID FROM Drivers
        """)
    return render_template("addDriver.html", tasktypes = tasktypes, drivers = drivers)

@app.route('/addDriverSubmit', methods=['GET', 'POST'])
@login_required
def addDriverSubmit():
    print "add Driver form submitted"
    dID = request.form['dID']
    dName = request.form['dName']

    columnString = ""
    valuesString = ""

    con = connect_to_database()
    cur = con.cursor()

    tTypes = cur.execute("""SELECT tType from Tasks DESC""")

    for t in tTypes:
        columnString += ", Field" + str(t[0])
        valuesString += ", " + str(request.form["Field" + str(t[0])])

    print "got all attributes"

    cur.execute("""INSERT INTO Drivers (dID, dName""" + columnString+""") VALUES (?,?""" + valuesString+""")""",[dID, dName])
    cur.execute("""INSERT INTO DriversShift (dID, lunchCount, breakCount,disproved) VALUES (?,0,0,0)""",[dID])

    con.commit()
    con.close()

    print "added driver"

    return redirect('/successAddDriver?dName='+ str(dName) +'&dID='+ str(dID))

@app.route('/successAddDriver', methods=['GET', 'POST'])
@login_required
def successAddDriver():
    print "adding driver success"
    dName = request.args.get('dName')
    dID = request.args.get('dID')

    con = connect_to_database()
    sql = """SELECT * FROM Drivers WHERE dID = '""" + str(dID) + """' and dName = '""" + str(dName) +"';"
    df = pd.read_sql(sql, con)
    con.close()

    # df = df.set_index(df.columns.tolist()[0])
    tablehtml = df.to_html(classes = 'table table-striped table-responsive', index=False)

    return render_template("SuccessWithTable.html",table = tablehtml, title = "New Driver Added") 

########################### Add Vehicle ############################################################################################
@app.route('/addVehicleForm')
@login_required
def addVehicleForm():
    return render_template("addVehicle.html")

@app.route('/addVehicleSubmit', methods=['GET', 'POST'])
@login_required
def addVehicleSubmit():
    print "add Vehicle form submitted"
    vName = request.form['vName']
    capacity = request.form['capacity']
    vSLatitude = request.form['vSLatitude']
    vSLongitude = request.form['vSLongitude']
    vELatitude = request.form['vELatitude']
    vELongitude = request.form['vELongitude'] 
    vSsID = request.form['vSsID']  
    vEsID = request.form['vEsID']

    con = connect_to_database()
    cur = con.cursor()

    print "got all attributes"

    cur.execute("""INSERT INTO Vehicles (vName, dID1, dID2, capacity, vBike, tID, vACLatitude, vACLongitude, vNXsID,  vNXLatitude, vNXLongitude, vSLatitude, vSLongitude, vELatitude,  vELongitude, vSsID, vEsID, vACsID, vBikeBroken) 
        VALUES (?,-111,-111,?,0,0,0,0,0,0,0,?,?,?,?,?,?,?,0)""",
        [vName, capacity, vSLatitude, vSLongitude, vELatitude,  vELongitude, vSsID, vEsID,vSsID])


    con.commit()
    con.close()

    print "added vehicle"
    return redirect('/successAddVehicle?vName='+ str(vName) +'&cap='+ str(capacity))

@app.route('/successAddVehicle', methods=['GET', 'POST'])
@login_required
def successAddVehicle():
    print "adding vehicle success"
    vName = request.args.get('vName')
    capacity = request.args.get('cap')

    con = connect_to_database()
    sql = """SELECT * FROM Vehicles WHERE vName = '""" + str(vName) + """' and capacity = """ + str(capacity) +";"
    df = pd.read_sql(sql, con)
    con.close()

    # df = df.set_index(df.columns.tolist()[0])
    tablehtml = df.to_html(classes = 'table table-striped table-responsive', index=False)

    return render_template("SuccessWithTable.html",table = tablehtml, title = "New Vehicle Added") 

########################### Add Forbidden Station ############################################################################################
@app.route('/addForbiddenStationForm', methods=['GET', 'POST'])
@login_required
def addForbiddenStationForm():
    print "accessing add forbidden station form"
    updateStations()
    stations = execute_query(
        """SELECT sID, stationName, availableDocks, availableBikes, totalDocks FROM Stations
        """)
    return render_template("addForbiddenStation.html", title = "Add Forbidden Station", stations = stations)


@app.route('/addForbiddenStationSubmit', methods=['GET', 'POST'])
@login_required
def addForbiddenStationSubmit():
    print "add forbidden station form submitted"
    sID = request.form['sID']
    sComment = request.form['sComment']
    startTime = request.form['startTime']
    endTime = request.form['endTime']
    repeat = request.form['repeat']
    nowTime = getNYtimenow()
    print "got all attributes"

    con = connect_to_database()
    cur = con.cursor()

    cur.execute("""INSERT INTO ForbiddenStations (sID, sComment, startTime, endTime, repeat, publishTime) Values (?,?,?,?,?,?)""",[sID, sComment, startTime, endTime, repeat,nowTime])

    con.commit()
    con.close()    

    print "added forbidden station" + str(sID)

    return redirect("/table/ForbiddenStations")

