# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-03 21:38:51
# @Last Modified by:   sy
# @Last Modified time: 2017-08-23 10:22:26


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

########################################## Dashboard & Index #################################################################
@app.route("/table/<table>")
@login_required
def viewtable(table):
    """List all entries in a table"""
    if table == "Users":
        print "trying to access Users table through /table"
        abort(404)
    table_name = str(table.title())
    if table_name == 'Stations':
        updateStations()
    con = connect_to_database()
    sql = """SELECT * FROM """+table_name
    df = pd.read_sql(sql, con)
    con.close()

    # df = df.set_index(df.columns.tolist()[0])
    tablehtml = df.to_html(classes = 'table table-striped table-responsive', index=False)
    if table_name == "Deletedtasks":
        return render_template("deleted_table.html",table = tablehtml, name = table_name, title = table_name)

    return render_template("table.html",table = tablehtml, name = table_name, title = table_name)

@app.route("/clearDeletedTasks")
@login_required
def clearDeletedTasks():
    con = connect_to_database()
    cur = con.cursor()

    cur.execute("""DELETE FROM DeletedTasks""")

    con.commit()
    con.close()
    return redirect('/table/DeletedTasks')


class DashTable():
    """Table to display in the dashboard
    table_name: string
    tablehtml: pandas df.to_html result
    parent: string
    url_name: string"""
    def __init__(self, table_name,tablehtml,parent,url_name):
        self.table_name = table_name
        self.tablehtml = tablehtml
        self.parent = parent # what to display on the button, example: "See All Closed Tasks"
        self.url_name = url_name # what this table is a subset of, example: "ClosedTasks"


@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard"""
    tables = [] # list of DashTable objects, the tables to display in the dashboard
    
    con = connect_to_database()
    sql = """SELECT tID, vID, dID1, dID2, sID, completionTime, priority, tType, bikeNum, comment FROM ClosedTasks where status = 0 ORDER BY closeTime DESC limit 5"""
    df = pd.read_sql(sql, con)

    sql2 = """SELECT tID, vID, dID1, dID2, sID, completionTime, priority, tType, bikeNum, comment FROM OpenTasks ORDER BY orderNum, vID limit 5"""
    df2 = pd.read_sql(sql2, con)

    sql3 = """SELECT tType, tName FROM Tasks"""
    df3 = pd.read_sql(sql3, con)

    sql4 = """SELECT tID, vID, dID1, dID2, sID, completionTime, priority, tType, bikeNum, comment FROM ClosedTasks where status = 1 ORDER BY closeTime DESC limit 5"""
    df4 = pd.read_sql(sql4, con)

    con.close()

    tablehtml = df.to_html(classes = 'table table-striped')
    table = DashTable("Recently Rejected Tasks", tablehtml, "See All Closed Tasks", "ClosedTasks")
    tables.append(table)

    tablehtml = df4.to_html(classes = 'table table-striped')
    table = DashTable("Recently Completed Tasks", tablehtml, "See All Closed Tasks", "ClosedTasks")
    tables.append(table)

    tablehtml = df2.to_html(classes = 'table table-striped')
    table = DashTable("Open Tasks", tablehtml, "See All Open Tasks", "OpenTasks")
    tables.append(table)

    tablehtml = df3.to_html(classes = 'table table-striped')
    table = DashTable("Task Types", tablehtml, "See All Task Types", "Tasks")
    tables.append(table)


    return render_template("dashboard.html", tables = tables, current_user = current_user)