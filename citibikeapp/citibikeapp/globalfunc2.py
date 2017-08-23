import csv
import sqlite3
import time
from datetime import datetime, timedelta
import pandas as pd
import pytz
import json
import urllib
import numpy as np

DATABASE = '/var/www/html/citibikeapp/citibikeapp/citibike_change.db'

def execute_query(cur,query, args=()):
    cur = cur.execute(query, args)
    rows = cur.fetchall()
    # cur.close()
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


def getNYtimenow():
    tz = pytz.timezone('America/New_York')
    time = str(datetime.now(tz))[:19]
    return time

def datetimeStringToObject(timeString):
    """convert a string in format YYYY-MM-DD hh:mm:ss to a datetime object"""
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
    """convert a string in format hh:mm:ss to a datetime object with current date"""
    try:
        # year = datetime.now().year
        # month = datetime.now().month
        # day = datetime.now().day
        hour = int(timeString[:2])
        minute = int(timeString[3:5])
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

def getNextFixOrderNum(cur,vID):
    """return the integer which is one larger than the order number of the last fixed task"""
    orderNum = execute_query(cur, """SELECT Count(*) FROM OpenTasks where vID = ? and fixTask = 1""", [vID])[0][0]
    orderNum = int(orderNum) + 1
    return orderNum

def getNextOrderNum(cur,vID):
    """return the integer which is one larger than the order number of the last task"""
    orderNum = execute_query(cur,"""SELECT Count(*) FROM OpenTasks where vID = ?""", [vID])[0][0]
    orderNum = int(orderNum) + 1
    return orderNum

def fixOrderBeforeInsert(cur,vID,orderNum):
    """Increment later tasks' order number by 1, orderNum is the order of the inserted task
    should be called before inserting the task """
    cur.execute("""UPDATE OpenTasks SET orderNum = orderNum + 1 WHERE vID = ? and orderNum >= ?""",[vID, orderNum])