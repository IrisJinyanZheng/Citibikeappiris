# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-04 11:36:42
# @Last Modified by:   sy
# @Last Modified time: 2017-08-14 09:45:47


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



############################ iOS APP Response Vehicle Info ############################################################################################
@app.route("/getVehicles.json")
def getVehicles():
    con = connect_to_database()
    sql = """SELECT * FROM Vehicles"""
    df = pd.read_sql(sql, con)
    con.close()

    json = df.to_json(orient='records')
    return json

@app.route("/vID/<vID>")
def getVehicleID(vID):
    """Used by the iOS app to display updated vehicle information"""
    vInfo = execute_query("""SELECT vName, dID1, dID2, capacity, vBike, vBikeBroken FROM Vehicles Where vID = ?
         """,
         [vID])

    vName = vInfo[0][0]
    dID1 = vInfo[0][1]
    dID2 = vInfo[0][2]
    capacity = vInfo[0][3]
    vBike = vInfo[0][4]
    vBikeBroken = vInfo[0][5]

    return "vehicle #" + vID + " " + vName + "\nDriver: " + dID1 + ", " + dID2 + " \nCapacity: " + str(capacity) + "\nTotal Bike on bus: " + str(vBike) + "\nBroken Bike on bus: " + str(vBikeBroken)

@app.route("/updateVehicleInfo")
def updateVehicleInfo():
    """Respond to a query of the format:
    myapp/updateVehicleInfo?vid=10&dID1=qq123&dID2=ww123&vBike=20&lati=40.72&longi=-73.97&vBikeBroken=\(vBikeBroken)"""
    result = "there is a problem"
    print "updating vehicle info"
    vID = request.args.get('vid')         
    dID1 = request.args.get('dID1')
    dID2 = request.args.get('dID2')
    vBike = request.args.get('vBike')
    vACLatitude = request.args.get('lati')
    vACLongitude = request.args.get('longi')
    vBikeBroken = request.args.get('vBikeBroken')

    print "got all attributes"

    # tz = pytz.timezone('America/New_York')
    # nowTime = str(datetime.now(tz))[:19]

    con = connect_to_database()
    cur = con.cursor()
    
    if True:
        print "updating"
        cur.execute("""UPDATE Vehicles SET dID1 = ?, dID2 = ?, vBike = ?, vACLatitude = ?, vACLongitude = ?, vBikeBroken = ?  WHERE vID=?""",[dID1, dID2, vBike,vACLatitude, vACLongitude, vBikeBroken, vID])
        result = "Updated Vehicle #" + vID

    con.commit()
    con.close()

    print "updating finished"
    if True:
        rows = execute_query("""SELECT * FROM Vehicles WHERE vID = ? AND dID1 = ? AND dID2 = ?""", [vID, dID1, dID2])

    if len(rows) == 0:
        rows2 = execute_query("""SELECT * FROM Vehicles WHERE vID = ? """, [vID])
        result = "Oops, there is a problem"
        if len(rows2) == 0:
            result = "No vehicle #" + str(vID)
    
    print result

    return result #'<br>'.join(str(row) for row in rows)

############################ iOS APP Response Task ############################################################################################
@app.route('/reasonCode.json')
def reasonCodeJson():
    con = connect_to_database()
    sql = """SELECT * FROM ReasonCode"""
    df = pd.read_sql(sql, con)
    con.close()

    resultJson = df.to_json(orient='records')
    return resultJson

@app.route("/getTasks.json")
def getTasks():
    """Jsonify open tasks"""
    con = connect_to_database()
    sql = """SELECT * FROM OpenTasks ORDER BY orderNum """
    df = pd.read_sql(sql, con)
    con.close()

    json = df.to_json(orient='index')
    return json

@app.route("/getTaskTypes.json")
def getTaskTypes():
    """Jsonify task types"""
    con = connect_to_database()
    sql = """SELECT * FROM Tasks"""
    df = pd.read_sql(sql, con)
    con.close()

    json = df.to_json(orient='records')
    return json

@app.route("/getStations.json")
def getStations():
    """Jsonify stations"""
    con = connect_to_database()
    sql = """SELECT sID, stationName, latitude, longitude, stAddress1  FROM Stations"""
    df = pd.read_sql(sql, con)
    con.close()

    json = df.to_json(orient='records')
    return json

@app.route('/stationid/<id>')
def get_id(id):
    rows = execute_query(
        """SELECT * FROM Stations 
        WHERE sID= ?
        """,
        [int(id)])
    return '<br>'.join(str(row) for row in rows)


@app.route('/response')#, methods=['GET']
def response():
    """Respond to a query of the format:
    myapp/response?tid=600&res=1&reason=qwe
    http://ec2-54-196-202-203.compute-1.amazonaws.com/response?tid=54&res=1&reason=accepted&lati=40.720498&longi=-73.907929&vID=13&nxs=127&nxlati=40.72&nxlongi=-73.97"""
    result = "there is a problem"
    print "responsing"
    tID = request.args.get('tid')         
    res = request.args.get('res')
    reason = request.args.get('reason')
    vACLatitude = request.args.get('lati')
    vACLongitude = request.args.get('longi')
    vID = request.args.get('vID')

    if notSignedIn(vID):
        print "Please enter vehicle info"
        return "Please enter vehicle info"

    task = execute_query(
        """SELECT orderNum FROM OpenTasks where tID = ?
        """, [tID])
    preOrder = task[0][0]

    tz = pytz.timezone('America/New_York')
    nowTime = str(datetime.now(tz))[:19]

    print "got all attributes"

    con = connect_to_database()
    cur = con.cursor()

    cur.execute("""UPDATE Vehicles SET vACLatitude = ?, vACLongitude = ? WHERE vID=?""",[vACLatitude,vACLongitude,vID])
    
    if res == '1':
        print "accepting"
        vNXsID = request.args.get('nxs')
        vNXLatitude = request.args.get('nxlati')
        vNXLongitude = request.args.get('nxlongi')

        cur.execute("""UPDATE Vehicles SET tID = ?, vNXLatitude = ?, vNXLongitude = ?, vNXsID = ? WHERE vID=?""",[tID, vNXLatitude,vNXLongitude,vNXsID,vID])
        cur.execute("""UPDATE OpenTasks SET acceptTime = ?, fixTask = 1 WHERE tID=?""",[nowTime,tID])
        result = "Accepted Task #" + tID

    if res == '0':
        print "rejecting"
        #insert into closedtask

        reasonID = request.args.get('reasonID')

        cur.execute("""UPDATE OpenTasks SET rejTime = ?, comment = ?, reasonID = ? WHERE tID = ?""",[nowTime,reason,reasonID,tID]) 

        # the following commented actions requires permission of dispatcher 

        # cur.execute("""INSERT INTO ClosedTasks (tID, requirement, acceptTime, priority, vID, dID1, dID2, tType, sID,bikeNum, completionTime, comment, publishTime, estComplete, arrivalTime) 
        #     SELECT tID, requirement, acceptTime, priority, 
        #     vID, dID1, dID2, tType, sID, bikeNum, completionTime, comment, publishTime, estComplete, arrivalTime FROM OpenTasks where tID=?
        #  """,
        #  [tID])
        # cur.execute("""UPDATE ClosedTasks SET status = 0, closeTime=?, comment=? WHERE tID=?""",[nowTime, reason, tID])
        # #delete from open task
        # cur.execute("""Delete from OpenTasks where tID = ?""",[tID])
        # cur.execute("""UPDATE OpenTasks SET orderNum = orderNum - 1 WHERE vID = ? and orderNum > ?""",[vID, preOrder]) 
        
        #the app will look for the word "Rejected" to determine if it's successfully rejected 
        result = "Requested Rejected Task #" + tID 

    con.commit()
    con.close()

    print "response finished"
    if res == '1':
        rows = execute_query("""SELECT * FROM OpenTasks WHERE tID = ?""", [tID])
    if res == '0':
        rows = execute_query("""SELECT * FROM ClosedTasks WHERE tID = ?""", [tID])

    if len(rows) == 0:
        result = "there is a problem"

    return result #'<br>'.join(str(row) for row in rows)

@app.route('/complete', methods=['GET'])
def complete():
    """Respond to a query of the format:
    myapp/complete?tid=600&lati=40.72&longi=-73.97&vID=11&vBike=10&vBikeBroken=0&res=0&actBikeNum=9&reason=comment"""
    result = "there is a problem"
    print "completing"
    tID = request.args.get('tid')
    vACLatitude = request.args.get('lati')
    vACLongitude = request.args.get('longi')
    vID = request.args.get('vID')
    vBike = request.args.get('vBike')
    vBikeBroken = request.args.get('vBikeBroken')
    comment = request.args.get('reason')
    res = request.args.get('res')
    actBikeNum = request.args.get('actBikeNum')

    if notSignedIn(vID):
        print "Please enter vehicle info"
        return "Please enter vehicle info"

    task = execute_query(
        """SELECT orderNum, tType, sID FROM OpenTasks where tID = ?
        """, [tID])
    preOrder = task[0][0]
    tType = task[0][1]
    sID = task[0][2]

    vInfo = execute_query("""SELECT vName, dID1, dID2 FROM Vehicles Where vID = ?
         """,
         [vID])

    dID1 = vInfo[0][1]
    dID2 = vInfo[0][2]
    print "got attributes"

    tz = pytz.timezone('America/New_York')
    nowTime = str(datetime.now(tz))[:19]

    con = connect_to_database()
    cur = con.cursor()

    cur.execute("""UPDATE Vehicles SET vBike = ?, vACLatitude = ?, vACLongitude = ?, vBikeBroken = ?, LFTime = ?, vACsID = ? WHERE vID=?""",[vBike, vACLatitude,vACLongitude, vBikeBroken, nowTime,sID,vID])

    #increment break count 
    if tType == 16:
        cur.execute("""UPDATE DriversShift SET lunchCount = lunchCount+1 WHERE dID=? or dID = ?""",[dID1, dID2])
    if tType == 17 or tType == 18:
        cur.execute("""UPDATE DriversShift SET breakCount = breakCount+1 WHERE dID=? or dID = ?""",[dID1, dID2])

    cur.execute("""INSERT INTO ClosedTasks (tID, requirement, acceptTime, priority, vID, dID1, dID2, tType, sID,bikeNum, completionTime, comment, publishTime, estComplete, arrivalTime, rejTime, reasonID) 
            SELECT tID, requirement, acceptTime, priority, 
            vID, dID1, dID2, tType, sID, bikeNum, completionTime, comment, publishTime, estComplete,arrivalTime, rejTime, reasonID FROM OpenTasks where tID=?
         """,
         [tID])
    cur.execute("""Delete from OpenTasks where tID = ?""",[tID])
    cur.execute("""UPDATE OpenTasks SET orderNum = orderNum - 1 WHERE vID = ? and orderNum > ?""",[vID, preOrder]) 
    cur.execute("""UPDATE ClosedTasks SET status = ?, closeTime=?, comment=?, actBikeNum = ? WHERE tID=?""",[res, nowTime, comment, actBikeNum, tID])
    result = "Completed Task #" + tID

    con.commit()
    con.close()
    
    rows = execute_query("""SELECT * FROM ClosedTasks WHERE tID = ?""", [tID])

    if len(rows) == 0:
        result = "there is a problem"

    print "complete finished"

    return result

@app.route('/arrive', methods=['GET'])
def arrive():
    """Respond to a query of the format:
    myapp/arrive?tid=600&lati=40.72&longi=-73.97&vID=11&reason=comment"""
    result = "there is a problem"
    print "arriving"
    tID = request.args.get('tid')
    vACLatitude = request.args.get('lati')
    vACLongitude = request.args.get('longi')
    vID = request.args.get('vID')
    comment = request.args.get('reason')

    if notSignedIn(vID):
        print "Please enter vehicle info"
        return "Please enter vehicle info"

    print "got attributes"

    tz = pytz.timezone('America/New_York')
    nowTime = str(datetime.now(tz))[:19]

    con = connect_to_database()
    cur = con.cursor()

    cur.execute("""UPDATE Vehicles SET vACLatitude = ?, vACLongitude = ? WHERE vID=?""",[vACLatitude,vACLongitude,vID])
    cur.execute("""UPDATE OpenTasks SET arrivalTime = ? WHERE tID=?""",[nowTime,tID])

    result = "Arrived for Task #" + tID

    con.commit()
    con.close()
    
    rows = execute_query("""SELECT * FROM OpenTasks WHERE tID = ?""", [tID])

    if len(rows) == 0:
        result = "there is a problem"

    print "arrival finished"

    return result

############################ Breaks ############################################################################################
#self-assign breaks not allowed
# @app.route('/lastBreakTime/dID1=<dID1>&dID2=<dID2>&vID=<vID>')
# @login_required #the function is not used 
# def lastBreakTime(dID1, dID2, vID):
#     isOnBreak = execute_query("""SELECT * from OpenTasks where vID = ? and (tType = 16 or tType = 17)""", [vID])
#     if len(isOnBreak) != 0:
#         print 3
#         return '0'
#     endTime1 = execute_query("""SELECT closeTime from ClosedTasks where (dID1 = ? or dID2 = ?) and (tType = 16 or tType = 17) ORDER BY completionTime desc""",[dID1,dID1])
#     endTime2 = execute_query("""SELECT closeTime from ClosedTasks where (dID1 = ? or dID2 = ?) and (tType = 16 or tType = 17) ORDER BY completionTime desc""",[dID2,dID2])
    
#     try:
#         endTime1 = endTime1[0][0]
#         endTime2 = endTime2[0][0]
#         endTime = min(endTime1,endTime2)

#         FMT = '%Y-%m-%d %H:%M:%S' #2017-06-08 17:10:43
#         nowTime = getNYtimenow()
#         sixHour = timedelta(hours=6)
#         tdelta = datetime.strptime(nowTime, FMT) - datetime.strptime(endTime, FMT)
#         if tdelta > sixHour:
#             return '1'
#         return '0'
#     except IndexError as e:
#         return '1'
#     except Exception as e:
#         print "exception lastBreakTime", e
#         return '1'
    
# @app.route('/assignBreak')
# def assignBreak():
#     #/assignBreak?vID=13&tType=?&dID1=?&dID2=?&aclati=?&aclongi=?
#     print "assign break request"

#     vID = request.args.get('vID')  
#     if notSignedIn(vID):
#         print "Please enter vehicle info"
#         return "Please enter vehicle info"

#     tType = request.args.get('tType')  
#     dID1 = request.args.get('dID1')  
#     dID2 = request.args.get('dID2')  
#     vACLatitude = request.args.get('aclati')
#     vACLongitude = request.args.get('aclongi')

#     # orderNum = execute_query("""SELECT Count(*) FROM OpenTasks where vID = ?""", [vID])[0][0]
#     # orderNum = int(orderNum) + 1
#     orderNum = 1


#     tz = pytz.timezone('America/New_York')
#     publishTime = str(datetime.now(tz))[:19]
#     completionTime = None

#     if str(tType) == '16':
#         completionTime = str(datetime.now(tz) + timedelta(minutes=30))[:19]
#     if str(tType) == '17' or str(tType) == '18':
#         completionTime = str(datetime.now(tz) + timedelta(minutes=15))[:19]

#     comment = "self-assigned break"
#     priority = 1

#     print "got all attributes"
#     print tType, type(tType), completionTime

#     con = connect_to_database()
#     cur = con.cursor()

#     cur.execute("""UPDATE OpenTasks SET orderNum = orderNum + 1 WHERE vID = ? """,[vID])
#     cur.execute("""UPDATE Vehicles SET vACLatitude = ?, vACLongitude = ? WHERE vID=?""",[vACLatitude,vACLongitude,vID])
#     cur.execute("""INSERT INTO OpenTasks (vID, tType, sID,bikeNum, completionTime, comment, publishTime, dID1, dID2, priority, orderNum, acceptTime) 
#          VALUES (?,?,0,0,?,?,?,?,?,?,?,?)
#          """,
#          [vID, tType, completionTime, comment, publishTime, dID1, dID2, priority, orderNum, publishTime])
    

#     con.commit()
#     con.close()

#     print "assigned break"
#     result = execute_query("""SELECT tID FROM OpenTasks Where vID = ? and tType = ? and comment = ? and publishTime = ?
#          """,
#          [vID, tType, comment, publishTime])

#     if len(result) == 0:
#         print result, "there is a problem"
#         result = "problem"

#     tID = result[0][0]
#     result = "assign break success"
#     print result, "updating vehicle next task info"

#     con = connect_to_database()
#     cur = con.cursor()
#     cur.execute("""UPDATE Vehicles SET tID = ?, vNXLatitude = ?, vNXLongitude = ? WHERE vID=?""",[tID, vACLatitude,vACLongitude, vID])
#     con.commit()
#     con.close()

#     print "updating vehicle info successfully"

#     return result

    