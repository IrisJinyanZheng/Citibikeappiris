# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-09 14:17:42
# @Last Modified by:   sy
# @Last Modified time: 2017-08-13 20:48:55

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
import cPickle as pickle
from globalfunc2 import * 

from Algo.Greedy3.StationMap import Task, Station, Truck, StationMap, Break
from Algo.Greedy3 import Algorithms

print "imported Data"


# DATABASE = '/home/ubuntu/citibikeapp/citibikeapp/citibike_change.db'
DATABASE = 'citibike_change.db'
# prefix_url = "/home/ubuntu/citibikeapp/citibikeapp/Algo/Greedy3/"

def create_smap():
    '''Return a stationmap object
    Declare, clean, and update StationMap Object example'''
    smap = StationMap()
    smap.clean()
    smap.update_json()
    return smap

def create_fbs(con,smap):
    """create forbidden stations"""
    forbidden_stations = {}
    nowTime = getNYtimenow()
    sql = """SELECT * FROM ForbiddenStationsTemp where startD <= " """+ nowTime + """ "  and endD >= " """+ nowTime + """ " """
    df = pd.read_sql(sql, con)
    for index, row in df.iterrows():
        station = smap.stations[int(row["sID"])]
        start = datetimeStringToObject(str(row["startD"]))
        end = datetimeStringToObject(str(row["endD"]))
        # Add forbidden station to map
        forbidden_stations[station] = (start, end)

    sql = """SELECT * FROM ForbiddenStations"""
    df = pd.read_sql(sql, con)
    for index, row in df.iterrows():
        if str(datetime.now().isoweekday()) in str(row["repeat"]):
            station = smap.stations[int(row["sID"])]
            start = timeStringToObject(str(row["startTime"]))
            end = timeStringToObject(str(row["endTime"]))
            # Add forbidden station to map
            forbidden_stations[station] = (start, end)

    return forbidden_stations



def parse_breaks(con):
    """Parse and return a dictionary from vehicle id to list of breaks"""
    break_dic = {}
    breaks = []
    sql = """SELECT * FROM Breaks """
    df = pd.read_sql(sql, con)
    for index, row in df.iterrows():
        break_duration = 15 #default 15min break
        if int(row["tType"]) == 16:
            break_duration = 30 #lunch break for 30
        # if int(row["tType"]) == 17 or int(row["tType"]) == 18:
        #   break_duration = 15
        break_time = timeStringToObject(str(row["publishTime"]))
        breaks.append(Break(break_time,break_duration))
        break_time = break_time + timedelta(days=1) #account for crossing day 
        breaks.append(Break(break_time,break_duration))
        break_dic[int(row["vID"])] = breaks
    return break_dic

# def estimate_day_shift(con):
#   sql = """SELECT MIN(endTime) FROM Vehicles"""
#   result = con.execute(sql).fetchall()[0][0]

def create_shift_ends(con):
    shift_end = {}
    sql = """SELECT * FROM Vehicles """
    df = pd.read_sql(sql, con)
    for index, row in df.iterrows():
        endTime = timeStringToObject(str(row["endTime"]))
        shift_end[int(row["vID"])] = endTime
    return shift_end

def create_vehicle_dic(con,smap):
    #create a vehicle dictionary without driverless vehicle
    break_dic = parse_breaks(con)
    trucks = {}
    sql = """SELECT * FROM Vehicles Where vID != -111 """ 
    df = pd.read_sql(sql, con)
    for index, row in df.iterrows():
        start_string = str(row["startTime"])
        if str(start_string).lower() != "null" and str(start_string) != "" and str(start_string).lower() != "none": #only pass in signed-in vehicles
            start_time = timeStringToObject(str(row["LFTime"])) # Create datetime obj at truck sign in time for beginning of truck's shift
            # start_time = datetime.today().replace(second=0, microsecond=0)  # Create datetime obj at current time for beginning of truck's shift
            if start_time is None:
                start_time = datetime.now()
            finish_time = timeStringToObject(str(row["endTime"])) # Create datetime obj at estimate truck sign out time for end of truck's shift
            if finish_time is None:
                finish_time = start_time + timedelta(hours=6) # if end time is null
            elif finish_time < start_time:
                finish_time = finish_time + timedelta(days=1)# account for crossing days
            #finish_time = start_time + timedelta(hours=6)  # Create datetime obj 6 hours from now for end of truck's shift
            start_location = smap.stations[int(row["vSsID"])]  # Get Station w/ ID 356 for truck's starting location
            end_location = smap.stations[int(row["vEsID"])]  # Get Station w/ ID 72 for truck's ending location

            try:
                current_location = smap.stations[int(row["vACsID"])] 
            except KeyError, e:
                try:
                    current_location = smap.stations[int(row["vNXsID"])]
                except:
                    current_location = start_location
            try:
                breaks = break_dic[int(row["vID"])]
            except KeyError, e:
                breaks = None # if the vehicle does not have break

            fill = int(row["vBike"])
            broken_bikes = int(row["vBikeBroken"])
            capacity = int(row["capacity"])
            # Create truck object with parameters created above

            # print int(row["vID"]), capacity, fill, broken_bikes, breaks, start_location, current_location, end_location, start_time, finish_time
            trucks[int(row["vID"])] = Truck(iden=int(row["vID"]), capacity=capacity, fill=fill, broken_bikes = broken_bikes, breaks=breaks, origin=start_location, location=current_location, destination=end_location,
                      start=start_time, end=finish_time)
    return trucks

def add_to_solution(solutions, truck, task):
    try:
        solutions[truck].append(task)
    except:
        solutions[truck] = [task]

def create_previous_solutions(con,smap):
    """Return a dictionary {solution:{}, prefix:{},driverless:[]}"""
    prefix_routes = {}
    previous_solution = {}
    driverless_tasks = []

    # trucks_dic = create_vehicle_dic(con,smap)
    sql = """SELECT ot.tID, ot.orderNum, Tasks.deltaBike, ot.bikeNum, ot.fixTask, ot.completionTime, ot.vID, ot.tType, ot.sID, ot.publishTime
            FROM OpenTasks AS ot
            Left JOIN Tasks on Tasks.tType = ot.tType"""
    df = pd.read_sql(sql, con)
    for index, row in df.iterrows():
        # truck = trucks_dic.get(int(row["vID"])) #if driverless, truck = None
        truck = int(row["vID"])
        station = smap.stations.get(int(row["sID"])) #if break, sID=0 and station=None
        bikes = int(row["bikeNum"])
        
        #pick up or drop of bikes
        to_truck = False
        if int(row["deltaBike"]) > 0:
            to_truck = True

        # if a task involve broken bikes 
        broken = False
        if int(row["tType"]) == 2 or int(row["tType"]) == 4:
            broken = True


        # assign break or task
        if int(row["tType"])== 16 or int(row["tType"])== 17 or int(row["tType"])== 18:
            task = Break(datetimeStringToObject(str(row["publishTime"])),30)
        elif int(row["tType"])== 17 or int(row["tType"])== 18:
            task = Break(datetimeStringToObject(str(row["publishTime"])),15)
        else:
            task = Task(station, bikes=bikes, to_truck=to_truck, broken=broken)

        if int(row["vID"]) == -111:
            # create driverless tasks list
            deadline = datetimeStringToObject(str(row["completionTime"]))
            driverless_tasks.append((task,deadline))
        elif int(row["fixTask"]) == 1:
            # create fixed solutions dictionary 
            add_to_solution(prefix_routes, truck, task)
        else:
            # create previous solutions dictionary 
            add_to_solution(previous_solution, truck, task)
        
    return {"solution":previous_solution, "prefix":prefix_routes,"driverless":driverless_tasks}

def parseForType(task):
    if isinstance(task, Task):
        if task.to_truck:
            if task.broken:
                return 2
            else:
                return 1
        else:
            if task.broken:
                return 4
            else:
                return 3
    elif isinstance(task,Break):
        tType = 18
        if task.duration.seconds == 30 * 60:
            tType = 16
        elif task.duration.seconds == 15 * 60:
            tType = 17
        return  tType
    else:
        print "can't parse task type", task
        return 0


def update_fixed_tasks(cur,new_prefix_routes):
    # update fixed tasks
    for vID in new_prefix_routes:
        for task in new_prefix_routes[vID]:
            if isinstance(task,Task):
                bikeNum = task.bikes
                sID = task.station.id
                tType = parseForType(task)
                cur.execute("""UPDATE OpenTasks SET bikeNum = ? WHERE vID=? and sID = ? and tType = ?""",[bikeNum, vID, sID, tType])
            # if isinstance(task,Break): #don't update break

def assign_driverless_tasks(cur,assigned_driverless):
    #assign driverless tasks and delete them from -111 truck
    for vID in assigned_driverless:
        for task in assigned_driverless[vID]:
            orderNum = getNextFixOrderNum(cur, vID)
            fixTask = 1
            if isinstance(task,Task):
                bikeNum = task.bikes
                sID = task.station.id
                tType = parseForType(task)
                task_info = execute_query(cur,"""SELECT orderNum from OpenTasks where vID=-111 and sID = ? and tType = ?""",[sID, tType])
                if len(task_info) == 0:
                    continue
                preOrder = task_info[0][0]
                cur.execute("""UPDATE OpenTasks SET orderNum = orderNum - 1 WHERE vID = -111 and orderNum > ?""",[preOrder])
                cur.execute("""UPDATE OpenTasks SET orderNum = orderNum + 1 WHERE vID = ? and orderNum >= ?""",[vID, orderNum])
                cur.execute("""UPDATE OpenTasks SET vID = ?, bikeNum = ?, orderNum = ?, fixTask = ? WHERE vID=-111 and sID = ? and tType = ?""",[vID, bikeNum, orderNum, fixTask, sID, tType])
            if isinstance(task,Break): #new breaks assigned
                dIDs = execute_query(cur,"""SELECT dID1, dID2 FROM Vehicles Where vID = ?""",[vID])
                dID1 = dIDs[0][0]
                dID2 = dIDs[0][1]
                assign_algo_break(cur, task, vID, dID1, dID2, orderNum, fixTask)
                
def available_tID(cur,vID):
    task_search = execute_query(cur,"""SELECT MIN(tID) from OpenTasksTemp""")
    tID = task_search[0][0]
    if tID is None:
        return None
    if is_tID_in_Open(cur,tID):
        return available_tID(cur,vID)
    return tID

def is_tID_in_Open(cur,tID):
    task_search2 = execute_query(cur,"""SELECT tID from OpenTasks where tID=?""",[tID])
    cur.execute("""DELETE FROM OpenTasksTemp WHERE tID = ?""",[tID])#won't use this tID anymore, either insert or exist in opentasks table
    if len(task_search2) == 0:
        return False
    else:
        return True

def similar_tID(cur,vID,sID,tType):
    """return the task ID if found one , return None otherwise"""
    task_search = execute_query(cur,"""SELECT tID from OpenTasksTemp where vID=? and sID = ? and tType = ? and fixTask = 0 and vID != -111""",[vID, sID, tType])
    if len(task_search) == 0:
        return available_tID(cur,vID)
    else:
        tID = task_search[0][0]
        if not is_tID_in_Open(cur,tID):
            return tID
        else:
            return available_tID(cur,vID)

def assign_algo_break(cur, task, vID, dID1, dID2, orderNum, fixTask):
    tType = parseForType(task)

    nowTime = getNYtimenow()
    completionTime = str(task.end_time)[:19]
    priority = 1
    sID = 0
    bikeNum = 0
    comment = None

    tID = similar_tID(cur,vID,sID,tType)

    if tID is None:
        cur.execute("""INSERT INTO OpenTasks (publishTime, vID, tType, sID,bikeNum, completionTime, comment, dID1, dID2, priority, orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,0,?)
            """,
          [nowTime, vID, tType, sID, bikeNum, completionTime, comment, dID1, dID2, priority, orderNum, fixTask])
    else:
        cur.execute("""INSERT INTO OpenTasks (tID, publishTime, vID, tType, sID,bikeNum, completionTime, comment, dID1, dID2, priority, orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0,?)
            """,
          [tID, nowTime, vID, tType, sID, bikeNum, completionTime, comment, dID1, dID2, priority, orderNum, fixTask])

def assign_algo_regular_task(cur, task, vID, dID1, dID2, orderNum, fixTask):
    nowTime = getNYtimenow()
    bikeNum = task.bikes
    sID = task.station.id
    tType = parseForType(task)
    completionTime = None
    comment = None
    priority = 1

    tID = similar_tID(cur,vID,sID,tType)

    if tID is None:
        cur.execute("""INSERT INTO OpenTasks (publishTime, vID, tType, sID,bikeNum, completionTime, comment, dID1, dID2, priority, orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,0,?)
            """,
          [nowTime, vID, tType, sID, bikeNum, completionTime, comment, dID1, dID2, priority, orderNum, fixTask])
    else:
        cur.execute("""INSERT INTO OpenTasks (tID, publishTime, vID, tType, sID,bikeNum, completionTime, comment, dID1, dID2, priority, orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0,?)
            """,
          [tID, nowTime, vID, tType, sID, bikeNum, completionTime, comment, dID1, dID2, priority, orderNum, fixTask])

def assign_algo_tasks(cur, algo_tasks):
    for vID in algo_tasks:
        dIDs = execute_query(cur,"""SELECT dID1, dID2 FROM Vehicles Where vID = ?""",[vID])
        dID1 = dIDs[0][0]
        dID2 = dIDs[0][1]
        for task in algo_tasks[vID]:
            orderNum = getNextOrderNum(cur,vID)
            fixTask = 0
            if orderNum == 1:
                fixTask = 1
            if isinstance(task, Task):
                assign_algo_regular_task(cur, task, vID, dID1, dID2, orderNum, fixTask)
            if isinstance(task, Break):
                assign_algo_break(cur, task, vID, dID1, dID2, orderNum, fixTask)

def complete_dic(trucks,route_dict):
    # better if don;t use this method
    """if a vehicle is not in the dictionary, create v:[] in the dictionary"""
    for truck in trucks:
        try:
            route_dict[truck.id]
        except KeyError, e:
            route_dict[truck.id] = []

def run_daytime_algo(con, smap):
    trucks_dic = create_vehicle_dic(con,smap)
    trucks = trucks_dic.values() #list of trucks
    forbidden_stations = create_fbs(con,smap)
    solution_dic = create_previous_solutions(con,smap)
    shift_end = create_shift_ends(con)
    prefix_routes = solution_dic["prefix"]
    previous_solution = solution_dic["solution"]
    driverless_tasks = solution_dic["driverless"]

    with open("forbidden_stations0.pkl", 'w') as input:
        pickle.dump(forbidden_stations, input)
    with open("prefix_routes0.pkl", 'w') as input:
        pickle.dump(prefix_routes, input)
    with open("previous_solution0.pkl", 'w') as input:
        pickle.dump(previous_solution, input)
    with open("driverless_tasks0.pkl", 'w') as input:
        pickle.dump(driverless_tasks, input)
    with open("shift_end0.pkl", 'w') as input:
        pickle.dump(shift_end, input)
    with open("trucks0.pkl", 'w') as input:
        pickle.dump(trucks, input)
    new_solutions = Algorithms.daytime_routing(forbidden_stations, prefix_routes, previous_solution, driverless_tasks, shift_end=shift_end,trucks=trucks, runtime=45, look_ahead=120)

    # clear memory
    del trucks_dic
    del forbidden_stations 
    del solution_dic 
    del shift_end 
    del prefix_routes 
    del previous_solution 
    del driverless_tasks
    del smap

    return new_solutions

def assign_tasks(cur,new_solutions):
    new_prefix_routes = new_solutions[0]
    assigned_driverless = new_solutions[1]
    algo_tasks = new_solutions[2]
    update_fixed_tasks(cur,new_prefix_routes)
    cur.execute("""INSERT INTO OpenTasksTemp SELECT * FROM OpenTasks WHERE fixTask = 0 and vID != -111;""") #save a copy of unfixed tasks for searching task ID later
    cur.execute("""DELETE FROM OpenTasks where fixTask = 0 and vID != -111""") #delete unfixed tasks
    assign_driverless_tasks(cur,assigned_driverless)
    assign_algo_tasks(cur, algo_tasks)
    cur.execute("""DELETE FROM OpenTasksTemp where fixTask = 0 and vID != -111""") #clear table for search

def greedyalgo(con):   
    urlfix = "/var/www/html/citibikeapp/citibikeapp/Algo/Greedy3/"
    cur = con.cursor()
    smap = create_smap()
    # add_fbs(con,smap)

    new_solutions = run_daytime_algo(con, smap)
    assign_tasks(cur,new_solutions)


if __name__ == '__main__':
    con = sqlite3.connect(DATABASE)
    greedyalgo(con)
    # test(con)
    # smap = create_smap()
    # run_daytime_algo(con, smap)
    con.commit()
    con.close()