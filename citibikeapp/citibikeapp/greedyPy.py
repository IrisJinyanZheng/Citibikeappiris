# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-04 11:52:34
# @Last Modified by:   sy
# @Last Modified time: 2017-08-04 12:45:48

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




############################ Greedy ############################################################################################
@app.route('/greedy')
@login_required
def greedy():
    try:
        from Algo.Greedy2 import StationMap
        from Algo.Greedy2.StationMap import Task, Station, Truck, StationMap
        from Algo.Greedy2 import Main
        from Algo.Greedy2.Main import Routes
        print "imported Data"
    except Exception as error:
        print "cannot import Data"
        print error
        return "The algorithm file is not imported"   
    urlfix = "/var/www/html/citibikeapp/citibikeapp/Algo/Greedy2/"
    x = StationMap()
    # with open(urlfix+'Data/StationMap.txt', 'r') as input:
    #     x = pickle.load(input)
    x.clean()
    # x.updateJSON()

    con = connect_to_database()
    sql = """SELECT * FROM Vehicles"""
    df = pd.read_sql(sql, con)
    con.close()

    trucks = []
    for index, row in df.iterrows():
        if str(row["vID"]) != "-111":
            t = Truck(iden=int(row["vID"]), capacity=int(row["capacity"]), fill=int(row["vBike"]), origin=x.stations[int(row["vSsID"])], destination=x.stations[int(row["vEsID"])], location=x.stations[int(row["vSsID"])])
            trucks.append(t)
    Routes(trucks, x)
    result = []
    for truck in trucks:
        for task in truck.route:
            dic = {}
            dic["sID"] = task.station.id
            dic["bikeNum"] = task.bikes
            dic["vID"] = truck.id
            dic["tType"] = 3
            if task.toTruck:
                dic["tType"] = 1
            result.append(dic)

    con = connect_to_database()
    cur = con.cursor()
    df = pd.DataFrame(result)
    #output_cols = [vID, dID1, dID2, requirement, completionTime, priority, tType, sID, bikeNum, comment, estComplete]
    df['requirement'] = None
    df['completionTime'] = None
    df['priority'] = None
    df['comment'] = "algo test"
    df['estComplete'] = None

    tablehtml = df.to_html(classes = 'table table-striped table-responsive', index=True)
    con.execute("DROP TABLE IF EXISTS TempTasks")
    df.to_sql('TempTasks', con, index=True, if_exists='replace')

    con.commit()
    con.close()

    #return render_template("greedy.html",table = tablehtml, name = "Recommand Tasks", title = "Recommand Tasks")
    return redirect("/table/TempTasks")


# @app.route('/assigngreedy')
# @login_required
# def assigngreedy():
#     execute_query("""INSERT INTO OpenTasks (tID, requirement, acceptTime, priority, vID, dID1, dID2, tType, sID,bikeNum, completionTime, comment, publishTime, estComplete) 
#             SELECT tID, requirement, acceptTime, priority, 
#             vID, dID1, dID2, tType, sID, bikeNum, completionTime, comment, publishTime, estComplete FROM OpenTasks where tID=?
#          """)