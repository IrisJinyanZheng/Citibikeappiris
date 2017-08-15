# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-08 23:01:48
# @Last Modified by:   sy
# @Last Modified time: 2017-08-15 15:05:14

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


############################ iOS Side Shift ############################################################################################
@app.route("/getShifts.json")
def getShifts():
    con = connect_to_database()
    sql = """SELECT * FROM DriversShift"""
    df = pd.read_sql(sql, con)
    con.close()

    json = df.to_json(orient='records')
    return json


@app.route("/updateVehicleShift/mode=<mode>&vID=<vID>")
def updateVehicleShift(mode,vID):
    print "updating vehicle shift"

    if notSignedIn(vID):
    	print "Please enter vehicle info"
    	return "Please enter vehicle info"

    nowTime = getNYtimenow()

    print "got attributes"


    con = connect_to_database()
    cur = con.cursor()

    if mode == "start":
    	cur.execute("""UPDATE Vehicles SET startTime = ?, LFTime = ? WHERE vID=?""",[nowTime, nowTime, vID])
    if mode == "end":
    	cur.execute("""UPDATE Vehicles SET startTime = null, endTime = null WHERE vID=?""",[vID])
    con.commit()
    con.close()
    
    vInfo = execute_query("""SELECT startTime FROM Vehicles Where vID = ?
         """,
         [vID])

    result = vInfo[0][0]

    if str(result).lower() == "null" or str(result) == "" or str(result).lower() == "none":
    	# if null in database, result should be "None"
        result = "not signed in"

    print "vehicle shift updated"
    print result

    return result

@app.route("/updateDriversShift/mode=<mode>&dID=<dID>&vID=<vID>")
def updateDriversShift(mode,dID,vID):
    print "updating driver shift"

    nowTime = getNYtimenow()

    print "got attributes"
    dInfo = execute_query("""SELECT signOutTimeEstimate FROM DriversShift Where dID = ?
         """,
         [dID])
    endTime = dInfo[0][0]

    con = connect_to_database()
    cur = con.cursor()

    if mode == "start":
    	print "start"
    	cur.execute("""UPDATE DriversShift SET signInTime = ?, vID = ?, lunchCount = 0, breakCount = 0 WHERE dID=?""",[nowTime, vID, dID])
    	cur.execute("""INSERT INTO ShiftHist (dID, vID, startTime) values (?,?,?)""",[dID, vID, nowTime])
        # estimate vehicle shift endTime
        cur.execute("""UPDATE Vehicles SET endTime = ? WHERE vID=? and endTime is null""",[endTime, vID]) #when endTime is null
        cur.execute("""UPDATE Vehicles SET endTime = MAX(endTime,?) WHERE vID=?""",[endTime, vID]) # when current endTime is smaller than the updated value
    if mode == "end":
    	print "end"
    	cur.execute("""UPDATE DriversShift SET signOutReqTime = ?, disproved = 0 WHERE dID=?""",[nowTime, dID])
    	# the following command need to wait for approval 
    	# cur.execute("""UPDATE ShiftHist SET endTime = ? WHERE dID=? and vID = ? and startTime = ?""",[nowTime, dID, vID, startTime])
    con.commit()
    con.close()
    
    dInfo = execute_query("""SELECT signInTime, signOutReqTime FROM DriversShift Where dID = ?
         """,
         [dID])

    if mode == "start":
    	result = dInfo[0][0]
    if mode =="end":
    	result = dInfo[0][1]

    if str(result).lower() == "null" or str(result) == "" or str(result).lower() == "none":
    	# if null in database, result should be "None"
        result = "there is a problem"

    print "driver shift updated"
    print result

    return result

############################ Web/Dispatcher Side Shift ############################################################################################
@app.route("/verifyDriversShift/dec=<decision>&dID=<dID>")
@login_required
def verifyDriversShift(decision,dID):
    print "verifying driver shift"

    nowTime = getNYtimenow()

    dInfo = execute_query("""SELECT signInTime, lunchCount, breakCount,vID FROM DriversShift Where dID = ?
         """,
         [dID])
    startTime = dInfo[0][0]
    lunchCount = dInfo[0][1]
    breakCount = dInfo[0][2]
    vID = dInfo[0][3]

    print "got attributes"


    con = connect_to_database()
    cur = con.cursor()

    if str(decision) == "1":
    	# approve

    	# reset driver's shift info
    	cur.execute("""UPDATE DriversShift SET vID = null, signOutReqTime = null, signInTime = null, comment = null, lunchCount = 0, breakCount = 0 WHERE dID=?""",[dID])
    	# archive this shift
    	cur.execute("""UPDATE ShiftHist SET endTime = ?, lunchCount = ?, breakCount = ?  WHERE dID=? and vID = ? and startTime = ?""",[nowTime, lunchCount, breakCount, dID, vID, startTime])
    	
        # Update vACsID to start location when log off
        cur.execute("""UPDATE Vehicles SET vACsID = vSsID WHERE vID=?""",[vID])
    	result = "Approved sign out"

    if str(decision) == "0":
    	# disprove

    	# remove the sign out request and update comment 
    	cur.execute("""UPDATE DriversShift SET signOutReqTime = null, comment = "disproved sign out", disproved = 1 WHERE dID=?""",[dID])
    	result = "Disproved sign out"
    con.commit()
    con.close()

    print result

    return redirect("/manageTable/DriversShift+dID")


