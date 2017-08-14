# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-04 12:00:16
# @Last Modified by:   sy
# @Last Modified time: 2017-08-04 12:00:35



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


############################ Search Tasks ############################################################################################
def checkVariable(a):
    a = '%' if a == "" else a
    return a

@app.route('/searchTask', methods=['GET', 'POST'])
@login_required
def searchTask():
    tasks = execute_query(
        """SELECT * FROM Tasks
        """)
    return render_template("search_task_form.html",tasks = tasks, title = "Search Task")

@app.route('/searchTaskResult', methods=['GET', 'POST'])
@login_required
def searchTaskResult():
    try:
        vID = request.form['vID']
    except Exception as e:
        vID = '%'

    try:
        fromPublishTime = request.form['fromPublishTime']
    except Exception as e:
        fromPublishTime = '%'

    try:
        toPublishTime = request.form['toPublishTime']
    except Exception as e:
        toPublishTime = '%'

    try:
        tType = request.form['tType']
    except Exception as e:
        tType = '%'

    try:
        sID = request.form['fromS']
    except Exception as e:
        sID = '%'

    try:
        bikeNum = request.form['bikeNum']
    except Exception as e:
        bikeNum = '%'

    try:
        priority = request.form['priority']
    except Exception as e:
        priority = '%'


    vID = checkVariable(vID)
    fromPublishTime = checkVariable(fromPublishTime)
    toPublishTime = checkVariable(toPublishTime)
    tType = checkVariable(tType)
    sID = checkVariable(sID)
    bikeNum = checkVariable(bikeNum)
    priority = checkVariable(priority)

    con = connect_to_database()

    sql = """SELECT * from OpenTasks where vID like ? and (DATETIME(publishTime) BETWEEN ? AND ?) and tType like ? and sID like ? and bikeNum like ? and priority like ? Order By vID"""
    df = pd.read_sql(sql, con, params=[vID,fromPublishTime,toPublishTime,tType, sID, bikeNum, priority])
    open_html = df.to_html(classes = 'table table-striped')
    

    sql = """SELECT * from ClosedTasks where vID like ? and (DATETIME(publishTime) BETWEEN ? AND ?) and tType like ? and sID like ? and bikeNum like ? and priority like ? Order By vID"""
    df = pd.read_sql(sql, con, params=[vID,fromPublishTime,toPublishTime,tType, sID, bikeNum, priority])
    close_html = df.to_html(classes = 'table table-striped')


    sql = """SELECT * from ClosedTasks where status = 0 and vID like ? and (DATETIME(publishTime) BETWEEN ? AND ?) and tType like ? and sID like ? and bikeNum like ? and priority like ? Order By vID"""
    df = pd.read_sql(sql, con, params=[vID,fromPublishTime,toPublishTime,tType, sID, bikeNum, priority])
    close_html_reject = df.to_html(classes = 'table table-striped')

    sql = """SELECT * from ClosedTasks where status = 1 and vID like ? and (DATETIME(publishTime) BETWEEN ? AND ?) and tType like ? and sID like ? and bikeNum like ? and priority like ? Order By vID"""
    df = pd.read_sql(sql, con, params=[vID,fromPublishTime,toPublishTime,tType, sID, bikeNum, priority])
    close_html_comp = df.to_html(classes = 'table table-striped')

    sql = """SELECT * from ClosedTasks where status = 2 and vID like ? and (DATETIME(publishTime) BETWEEN ? AND ?) and tType like ? and sID like ? and bikeNum like ? and priority like ? Order By vID"""
    df = pd.read_sql(sql, con, params=[vID,fromPublishTime,toPublishTime,tType, sID, bikeNum, priority])
    close_html_parcomp = df.to_html(classes = 'table table-striped')


    sql = """SELECT * from TempTasks where vID like ? and tType like ? and sID like ? and bikeNum like ? Order By vID"""
    df = pd.read_sql(sql, con, params=[vID, tType, sID, bikeNum])
    temp_html = df.to_html(classes = 'table table-striped')



    con.close()

    return render_template("search_table.html", open_table = open_html, close_table = close_html, close_table_reject = close_html_reject, close_table_comp = close_html_comp, close_table_parcomp = close_html_parcomp, temp_table = temp_html)

