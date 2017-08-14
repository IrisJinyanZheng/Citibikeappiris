# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-07-31 23:49:20
# @Last Modified by:   sy
# @Last Modified time: 2017-08-09 14:38:23

from collections import Counter
import csv
import sqlite3
import time
import logging
from datetime import datetime, timedelta
import pandas as pd
import pytz
import json
import urllib
import numpy as np



DATABASE = '/home/ubuntu/citibikeapp/citibikeapp/citibike_change.db'

def getNYtimenow():
    tz = pytz.timezone('America/New_York')
    time = str(datetime.now(tz))[:19]
    return time


def updatePriority(con):
	nowtime = getNYtimenow()

	cur = con.cursor()
	cur.execute("""UPDATE OpenTasks SET priority = 5, pDL = 1 WHERE pDL = 0 and priority = 1 and completionTime < ?""",[nowtime])
	cur.execute("""UPDATE OpenTasks SET priority = 7, pDL = 1 WHERE pDL = 0 and priority = 5 and completionTime < ?""",[nowtime])
	cur.execute("""UPDATE OpenTasks SET pDL = 0 WHERE pDL is null""")
	con.commit()
	con.close()



if __name__ == '__main__':
    conn = sqlite3.connect(DATABASE)
    # csv2sql(conn, stationList)
    updatePriority(conn)
