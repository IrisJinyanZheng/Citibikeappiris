# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-04 11:49:45
# @Last Modified by:   sy
# @Last Modified time: 2017-08-09 14:12:56


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



############################ Manage Tables ############################################################################################
@app.route('/manageTabelJson/<table>.json')
@login_required
def manageTabelJson(table):
    if table == "Users":
        print "trying to access table User in /manageTableJson"
        abort(404)
    con = connect_to_database()
    if table == "OpenTasks":
        sql = """SELECT ot.tID, ot.orderNum, Tasks.tName, Stations.stationName, ot.bikeNum, PriorityCode.pName as priorityN, ReasonCode.reasonName, ot.comment, ot.fixTask, ot.completionTime, ot.acceptTime, ot.rejTime, ot.arrivalTime, ot.publishTime, ot.vID, ot.tType, ot.sID, ot.requirement,  ot.estComplete, ot.priority, ot.reasonID
            FROM OpenTasks AS ot
            Left JOIN Tasks on Tasks.tType = ot.tType
            Left JOIN Stations  on Stations.sID = ot.sID
            Left JOIN PriorityCode  on PriorityCode.priority = ot.priority
            left JOIN ReasonCode ON ot.reasonID = ReasonCode.reasonName
            Order By ot.vID, ot.orderNum"""
    elif table == "Vehicles":
        sql = """SELECT * FROM Vehicles"""
    elif table == "Drivers":
        sql = """SELECT * FROM Drivers"""
    elif table == "Tasks":
        sql = """SELECT * FROM Tasks"""
    elif table == "ClosedTasks":
        sql = """SELECT * FROM ClosedTasks"""
    elif table == "ForbiddenStations":
        sql = """SELECT * FROM ForbiddenStations"""
    elif table == "ForbiddenStationsTemp":
        sql = """SELECT * FROM ForbiddenStationsTemp"""
    elif table == "DriversShift":
        sql = """SELECT * FROM DriversShift"""
    else:
        abort(404)
    df = pd.read_sql(sql, con)
    con.close()

    resultJson = df.to_json(orient='records')
    return resultJson


############################ Delete Entry ############################################################################################

@app.route('/deleteEntryById/<table>/<ID>')
@login_required
def deleteEntryById(table, ID):
    time = getNYtimenow()
    vID = -12222 #this id should not exist to prevent bug
    preOrder = 0
    col = ""

    if table == "Users":
        abort(404)
    if table == "OpenTasks":
        task = execute_query(
            """SELECT vID, orderNum,sID FROM OpenTasks where tID = ?
            """, [ID])
        vID = task[0][0]
        preOrder = task[0][1]
        sID = task[0][2]

    con = connect_to_database()
    cur = con.cursor()

    if table == "OpenTasks":
        duration = int(request.args.get('du'))
        #can't forbid less than 5 minutes
        if int(duration)<5:
            duration = 5
        startD = getNYtimenow()
        startTime = startD[11:]
        publishTime = getNYtimenow()
        tz = pytz.timezone('America/New_York')
        endD = str(datetime.now(tz) + timedelta(minutes=duration))[:19]
        endTime = endD[11:]

        cur.execute("""INSERT INTO DeletedTasks (tID, publishTime, acceptTime, vID, dID1, dID2, requirement, completionTime, priority, tType, sID,bikeNum, comment, publishTime, estComplete, arrivalTime, rejTime, reasonID) 
            SELECT  tID, publishTime, acceptTime, vID, dID1, dID2, requirement, completionTime, priority, tType, sID,bikeNum, comment, publishTime, estComplete, arrivalTime, rejTime, reasonID FROM OpenTasks where tID=?
         """,
         [ID])
        cur.execute("""UPDATE DeletedTasks SET deleteTime=? WHERE tID=?""",[time, ID])
        cur.execute("""DELETE from OpenTasks where tID = ?""",[ID])
        cur.execute("""UPDATE OpenTasks SET orderNum = orderNum - 1 WHERE vID = ? and orderNum > ?""",[vID, preOrder]) 
        cur.execute("""INSERT INTO ForbiddenStationsTemp(sID, sComment,startTime,endTime,publishTime,startD,endD) VALUES(?,'deleted',?,?,?,?,?)""",[sID,startTime,endTime,publishTime,startD,endD])

        col = "tID"
    # can't delete Closed Tasks
    # elif table == "ClosedTasks":
    #     cur.execute("""INSERT INTO DeletedTasks (tID, publishTime, acceptTime, vID, dID1, dID2, requirement, completionTime, priority, tType, sID,bikeNum, comment, publishTime, estComplete, arrivalTime, rejTime, reasonID) 
    #         SELECT  tID, publishTime, acceptTime, vID, dID1, dID2, requirement, completionTime, priority, tType, sID,bikeNum, comment, publishTime, estComplete, arrivalTime, rejTime, reasonID FROM ClosedTasks where tID=?
    #      """,
    #      [ID])
    #     cur.execute("""UPDATE DeletedTasks SET deleteTime=? WHERE tID=?""",[time, ID])
    #     cur.execute("""DELETE from ClosedTasks where tID = ?""",[ID])

    #     col = "tID"
    elif table == "Vehicles":
        cur.execute("""DELETE from Vehicles where vID = ?""",[ID])
        col = "vID"
    elif table == "Drivers":
        cur.execute("""DELETE from Drivers where dID = ?""",[ID])
        cur.execute("""DELETE from DriversShift where dID = ?""",[ID])
        col = "dID"
    elif table == "ForbiddenStations":
        cur.execute("""INSERT INTO ClosedForbiddenStations (fsID, sID, sComment,startTime,endTime,repeat,publishTime) 
            SELECT  fsID, sID, sComment,startTime,endTime,repeat,publishTime FROM ForbiddenStations where fsID=?
         """,
         [ID])
        cur.execute("""UPDATE ClosedForbiddenStations  SET closeTime=? WHERE fsID=?""",[time, ID])
        cur.execute("""DELETE from ForbiddenStations where fsID = ?""",[ID])
        col = "fsID"
    elif table == "ForbiddenStationsTemp":
        cur.execute("""INSERT INTO ClosedForbiddenStationsTemp (fstID, sID, sComment,startTime,endTime,publishTime,startD,endD) 
            SELECT  fstID, sID, sComment,startTime,endTime, publishTime,startD,endD FROM ForbiddenStationsTemp where fstID=?
         """,
         [ID])
        cur.execute("""UPDATE ClosedForbiddenStationsTemp  SET closeTime=? WHERE fstID=?""",[time, ID])
        cur.execute("""DELETE from ForbiddenStationsTemp where fstID = ?""",[ID])
        col = "fstID"
    elif table == "Breaks":
        tType = int(request.args.get('tType'))
        cur.execute("""DELETE from Breaks where vID = ? and tType = ?""",[ID,tType])
    else:
        abort(404)
    

    con.commit()
    con.close()

    if table == "OpenTasks":
        return redirect('/manageTask')
    if table == "Breaks":
        return redirect('/manageBreak')

    return redirect('/manageTable/'+table+"+"+col)

@app.route('/manageTable/<table>+<col>')
@login_required
def manageTable(table,col):
    shouldUpdate = "True"
    if table == "ClosedTasks":
        shouldUpdate = "False"
    if table == "ForbiddenStations" or table == "ForbiddenStationsTemp":
        shouldUpdate = "NoUpdate"
    if table == "DriversShift":
        return render_template("table_driversshift_manage.html")
    return render_template("manage_table.html", table_name = table, id_col = col, shouldUpdate = shouldUpdate )

@app.route('/manageTask')
@login_required
def manageTask():
    con = connect_to_database()
    sql = """SELECT Vehicles.vID, Vehicles.vName, Vehicles.dID1,  d1.dName as dName1, Vehicles.dID2,  d2.dName as dName2, Vehicles.capacity, Vehicles.vBike, Vehicles.tID, 
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
    return render_template("table_opentasks_manage.html", vehicles  = vehicles )

@app.route('/currentOpenTask')
@login_required
def currentOpenTask():
    con = connect_to_database()
    sql = """SELECT ot.tID, ot.vID,Vehicles.vName,Tasks.tName, Stations.stationName, ot.bikeNum, PriorityCode.pName as priorityN, ReasonCode.reasonName, ot.comment, ot.acceptTime, ot.arrivalTime, ot.completionTime, ot.publishTime, ot.tType, ot.sID, ot.requirement,  ot.estComplete, ot.orderNum, ot.reasonID, ot.priority
            FROM OpenTasks AS ot
            Left JOIN Tasks on Tasks.tType = ot.tType
            Left JOIN Stations  on Stations.sID = ot.sID
            left JOIN Vehicles ON ot.vID = Vehicles.vID
            Left JOIN PriorityCode  on PriorityCode.priority = ot.priority
            left JOIN ReasonCode ON ot.reasonID = ReasonCode.reasonName
            Where ot.orderNum = 1
            Order By ot.vID""" 
    df = pd.read_sql(sql, con)
    con.close()

    tablehtml = df.to_html(classes = 'table table-striped table-responsive', index=False)

    return render_template("table.html",table = tablehtml, name = "Current Tasks", title = "Current Tasks")

@app.route('/violatingDeadlineOpenTask')
@login_required
def violatingDeadlineOpenTask():
    nowTime = getNYtimenow()
    con = connect_to_database()
    sql = """SELECT ot.tID, ot.vID,Vehicles.vName,Tasks.tName, Stations.stationName, ot.bikeNum, PriorityCode.pName as priorityN, ReasonCode.reasonName, ot.comment, ot.acceptTime, ot.arrivalTime, ot.completionTime, ot.publishTime, ot.tType, ot.sID, ot.requirement,  ot.estComplete, ot.orderNum, ot.reasonID, ot.priority
            FROM OpenTasks AS ot
            Left JOIN Tasks on Tasks.tType = ot.tType
            Left JOIN Stations  on Stations.sID = ot.sID
            left JOIN Vehicles ON ot.vID = Vehicles.vID
            Left JOIN PriorityCode  on PriorityCode.priority = ot.priority
            left JOIN ReasonCode ON ot.reasonID = ReasonCode.reasonName
            Where ot.completionTime < '""" + nowTime + """'"""
    df = pd.read_sql(sql, con)
    con.close()

    tablehtml = df.to_html(classes = 'table table-striped table-responsive', index=False)

    return render_template("table.html",table = tablehtml, name = "Violating Deadline Tasks", title = "Violating Deadline Tasks")

############################ Update By Id ############################################################################################
#should not use the following for opentasks
@app.route('/searchByCol/<table>/<col>=<id>.json')
@login_required
def searchByCol(table,col,id):
    if table == "Users":
        abort(404)
    con = connect_to_database()
    sql = """SELECT * FROM """ + table + """ WHERE """ + col +" = '" + id + "'"
    df = pd.read_sql(sql, con)
    con.close()

    jsonresult = df.to_json(orient='records')
    return jsonresult

@app.route('/updateByIdForm/<table>/<col>=<id>')
@login_required
def updateByIdForm(table, col, id):
    if table == "Users":
        abort(404)
    if table == "Drivers":
        return render_template("update_drivers_form.html", table_name = table, id = id, id_col = col)
    if table == "Vehicles":
        return render_template("update_vehicles_form.html", table_name = table, id = id, id_col = col)
    if table == "Tasks":
        return render_template("update_tasktypes_form.html", table_name = table, id = id, id_col = col)
    if table == "DriversShift":
        return render_template("update_driversshift_form.html", table_name = table, id = id, id_col = col)
    return render_template("update_form.html", table_name = table, id = id, id_col = col)


@app.route('/updateByIdSumbit/<table>/<col>=<id>', methods=['GET', 'POST'])
@login_required
def updateById(table,col, id):
    if table == "Users":
        abort(404)
    # time = getNYtimenow()
    columnList = execute_query("""PRAGMA table_info(""" + table + """)""")
    commandString = ""

    con = connect_to_database()
    cur = con.cursor()

    for c in columnList:
        value = str(request.form[str(c[1])])
        if value.lower() != "null":
            value = "'" + str(request.form[str(c[1])]) + "'"
        commandString += c[1] + " = " + value + ","
        # commandString += c[1] + " = " + "'" + str(request.form[str(c[1])]) + "',"

    print "got all attributes"

    cur.execute("""UPDATE """ + table + """ SET """ + commandString[:-1]+""" WHERE """ + col + """='""" + str(id) + """'""")

    con.commit()
    con.close()

    if table == "DriversShift":
        return redirect('/manageTable/DriversShift+dID')

    return redirect('/successUpdateById/'+str(table)+'/'+str(col)+'='+str(id))


@app.route('/successUpdateById/<table>/<col>=<id>', methods=['GET', 'POST'])
@login_required
def successUpdateById(table,col, id):
    print "updating by id success"
    con = connect_to_database()
    sql = """SELECT * FROM """ + table + """ WHERE """ + col +" = '"+ id + "'"
    df = pd.read_sql(sql, con)
    con.close()

    # df = df.set_index(df.columns.tolist()[0])
    tablehtml = df.to_html(classes = 'table table-striped table-responsive', index=False)

    return render_template("SuccessWithTable.html",table = tablehtml, title = "Updated") 

############################ Reject Open Tasks ############################################################################################
# Confirm 
@app.route('/confirmRejectTask/<tID>', methods=['GET', 'POST'])
@login_required
def confirmRejectTask(tID):
    print "confirming reject"
    #insert into closedtask

    task = execute_query(
        """SELECT orderNum, vID, sID FROM OpenTasks where tID = ?
        """, [tID])
    preOrder = task[0][0]
    vID = task[0][1]
    sID = task[0][2]
    
    tz = pytz.timezone('America/New_York')
    nowTime = str(datetime.now(tz))[:19]

    duration = int(request.args.get('du'))
    startD = getNYtimenow()
    startTime = startD[11:]
    publishTime = getNYtimenow()
    endD = str(datetime.now(tz) + timedelta(minutes=duration))[:19]
    endTime = endD[11:]

    print "got all attributes"

    con = connect_to_database()
    cur = con.cursor()



    cur.execute("""INSERT INTO ClosedTasks (tID, requirement, acceptTime, priority, vID, dID1, dID2, tType, sID,bikeNum, completionTime, comment, publishTime, estComplete, arrivalTime, rejTime, reasonID) 
        SELECT tID, requirement, acceptTime, priority, 
        vID, dID1, dID2, tType, sID, bikeNum, completionTime, comment, publishTime, estComplete, arrivalTime,rejTime, reasonID FROM OpenTasks where tID=?
     """,
     [tID])
    cur.execute("""UPDATE ClosedTasks SET actBikeNum = 0, status = 0, closeTime=? WHERE tID=?""",[nowTime, tID])

    #delete from open task
    cur.execute("""Delete from OpenTasks where tID = ?""",[tID])
    cur.execute("""UPDATE OpenTasks SET orderNum = orderNum - 1 WHERE vID = ? and orderNum > ?""",[vID, preOrder]) 

    # forbid the station temporarily
    cur.execute("""INSERT INTO ForbiddenStationsTemp(sID, sComment,startTime,endTime,publishTime,startD,endD) VALUES(?,'rejected',?,?,?,?,?)""",[sID,startTime,endTime,publishTime,startD,endD])


    con.commit()
    con.close()
    return redirect('/manageTask')

# disprove
@app.route('/disproveRejectTask/<tID>', methods=['GET', 'POST'])
@login_required
def disproveRejectTask(tID):
    print "disproving reject"
    # update rejTime to null

    task = execute_query(
        """SELECT comment FROM OpenTasks where tID = ?
        """, [tID])
    comment = task[0][0]
    
    print "got all attributes"

    con = connect_to_database()
    cur = con.cursor()

    cur.execute("""UPDATE OpenTasks SET rejTime = null,reasonID = null, comment = comment || "; disprove reject" WHERE tID = ? """,[tID]) 

    con.commit()
    con.close()

    # disproved task

    return redirect('/manageTask')


############################ Update Open Tasks ############################################################################################
@app.route('/updateOpenTasksForm/<id>', methods=['GET', 'POST'])
@login_required
def updateOpenTasksForm(id):
    print "accessing updateOpenTasksForm"
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

    taskR = execute_query(
        """SELECT vID, tType, sID, bikeNum, completionTime, priority, comment, estComplete, acceptTime FROM OpenTasks where tID = ?
        """, [id])
    
    vID =  taskR[0][0]
    tType = taskR[0][1]
    sID = taskR[0][2]
    bikeNum = taskR[0][3]
    completionTime = taskR[0][4]
    priority = taskR[0][5]
    comment = taskR[0][6]
    # estComplete = taskR[0][7]
    acceptTime = taskR[0][8]

    return render_template("update_opentasks_form.html", bikes = bikes_ID, tasks = tasks, title = "Update Open Task", vehicles = vehicles, stations = stations, tID = id,
        vID =  vID, tType = tType, sID = sID, bikeNum = bikeNum, completionTime = completionTime, priority = priority, comment = comment, acceptTime = acceptTime) #, estComplete = estComplete, 


@app.route('/updateOpenTasksSumbit/tID=<tID>', methods=['GET', 'POST'])
@login_required
def updateOpenTasks(tID):
    print "update open task form submitted"

    vID = request.form['vID']
    fromS = request.form['fromS']
    bikeNum = request.form['bikeNum'] 
    completionTime = request.form['completionTime']
    comment = request.form['comment'] 
    priority = request.form['priority']
    tType = request.form['tType']

    dID1 = -111
    dID2 = -111

    if completionTime == "0000-00-00 00:00:00":
        completionTime = None
    if fromS == '-1':
        fromS = None
    if vID != '-111':
        dIDs = execute_query("""SELECT dID1, dID2 FROM Vehicles Where vID = ?
         """,
         [vID])

        dID1 = dIDs[0][0]
        dID2 = dIDs[0][1]

    task = execute_query(
        """SELECT vID, orderNum,completionTime,acceptTime, arrivalTime FROM OpenTasks where tID = ?
        """, [tID])
    prevID = task[0][0]
    preOrder = task[0][1]
    preCompletionTime = task[0][2]
    preAcceptTime = task[0][3]
    arrivalTime = task[0][4]

    #find the order number of the last fixed task, then increment 1
    orderNum = getNextFixOrderNum(vID)
    print "got all attributes"

    # tz = pytz.timezone('America/New_York')
    # publishTime = str(datetime.now(tz))[:19]

    if str(arrivalTime).lower() != "null" and str(arrivalTime) != "" and str(arrivalTime).lower() != "none":
        #if the rebalancer has arrived, no changes are made
        return redirect('/manageTask')

    con = connect_to_database()
    cur = con.cursor()

    #when update tasks, estimate completion time goes to 0
    resetEstComp(cur, vID)
    resetEstComp(cur, prevID)


    if str(preAcceptTime).lower() != "null" and str(preAcceptTime) != "" and str(preAcceptTime).lower() != "none":
        #if the task has been accepted
        cur.execute("""UPDATE OpenTasks SET bikeNum = ?, completionTime = ?, comment = ?, priority = ?
        WHERE tID = ?
         """,
         [bikeNum, completionTime, comment, priority, tID])
    else:    
        #if the task has not been accepted
        cur.execute("""UPDATE OpenTasks SET vID = ?, tType = ?, sID = ?,bikeNum = ?, completionTime = ?, comment = ?, dID1 = ?, dID2 = ?, priority = ?
        WHERE tID = ?
         """,
         [vID, tType, fromS, bikeNum, completionTime, comment, dID1, dID2, priority, tID])

        if (str(prevID) != str(vID)):
            # if vehicle changes, order should also change
            cur.execute("""UPDATE OpenTasks SET orderNum = orderNum - 1 WHERE vID = ? and orderNum > ?""",[prevID, preOrder])
            cur.execute("""UPDATE OpenTasks SET orderNum = orderNum + 1 WHERE vID = ? and orderNum >= ?""",[vID, orderNum])
            cur.execute("""UPDATE OpenTasks SET orderNum = ? WHERE tID = ? """,[orderNum, tID])    

    if (preCompletionTime != completionTime):
        #if update deadline
        cur.execute("""UPDATE OpenTasks SET pDL = 0 WHERE tID = ? """,[tID])    

    con.commit()
    con.close()

    print "updated task"

    return redirect('/manageTask')

############################ Order ############################################################################################
@app.route('/reOrder/tID=<tID>&vID=<vID>&preOrder=<preOrder>/', methods=['GET', 'POST'])
@login_required
def reOrder(tID,vID,preOrder):
    print "start reordering"
    orderNum = request.form["orderNum"]

    print "got all attributes"
    con = connect_to_database()
    cur = con.cursor()

    resetEstComp(cur, vID)

    if (int(preOrder) > int(orderNum)):
        cur.execute("""UPDATE OpenTasks SET orderNum = orderNum + 1 WHERE vID = ? and orderNum >= ? and orderNum < ?""",[vID, orderNum, preOrder])
        cur.execute("""UPDATE OpenTasks SET orderNum = ? Where tID = ?""", [orderNum, tID])
    if (int(preOrder) < int(orderNum)):
        cur.execute("""UPDATE OpenTasks SET orderNum = orderNum - 1 WHERE vID = ? and orderNum > ? and orderNum < ?""",[vID, preOrder,orderNum])
        cur.execute("""UPDATE OpenTasks SET orderNum = ? Where tID = ?""", [int(orderNum)-1, tID])

    con.commit()
    con.close()
    return redirect('/manageTask')

@app.route('/fixTask/tID=<tID>&vID=<vID>&preOrder=<preOrder>')
def fixTask(tID,vID,preOrder):
    print "start fixing task"
    orderNum = getNextFixOrderNum(vID)
    print "got all attributes"

    con = connect_to_database()
    cur = con.cursor()

    resetEstComp(cur, vID)

    if (int(preOrder) > int(orderNum)):
        cur.execute("""UPDATE OpenTasks SET orderNum = orderNum + 1 WHERE vID = ? and orderNum >= ? and orderNum < ?""",[vID, orderNum, preOrder])
        cur.execute("""UPDATE OpenTasks SET orderNum = ?, fixTask = 1 Where tID = ?""", [orderNum, tID])
    # if (int(preOrder) < int(orderNum)):
    #     cur.execute("""UPDATE OpenTasks SET orderNum = orderNum - 1 WHERE vID = ? and orderNum > ? and orderNum < ?""",[vID, preOrder,orderNum])
    #     cur.execute("""UPDATE OpenTasks SET orderNum = ? Where tID = ?""", [int(orderNum)-1, tID])

    con.commit()
    con.close()
    return redirect('/manageTask')


############################ Assign Closed Tasks ############################################################################################

@app.route('/reassignByIdForm/<table>/<col>=<id>', methods=['GET', 'POST'])
@login_required
def reassignByIdForm(table, col, id):
    print "accessing re-assign task form"
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

    taskR = execute_query(
        """SELECT vID, tType, sID, bikeNum, completionTime, priority, comment, estComplete FROM ClosedTasks where tID = ?
        """, [id])
    
    vID =  taskR[0][0]
    tType = taskR[0][1]
    sID = taskR[0][2]
    bikeNum = taskR[0][3]
    completionTime = taskR[0][4]
    priority = taskR[0][5]
    comment = taskR[0][6]
    # estComplete = taskR[0][7]

    return render_template("task_form_reassign.html", bikes = bikes_ID, tasks = tasks, title = "Assign Task", vehicles = vehicles, stations = stations,
        vID =  vID, tType = tType, sID = sID, bikeNum = bikeNum, completionTime = completionTime, priority = priority, comment = comment)#, estComplete = estComplete
