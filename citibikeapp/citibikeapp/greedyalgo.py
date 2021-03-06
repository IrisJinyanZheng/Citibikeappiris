# -*- coding: utf-8 -*-
# @Author: sy
# @Date:   2017-08-09 14:17:42
# @Last Modified by:   sy
# @Last Modified time: 2017-08-27 14:54:43

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
import argparse
from globalfunc2 import * 

from Algo.Greedy3.StationMap import Task, Station, Truck, StationMap, Break
from Algo.Greedy3 import Algorithms

print "imported Data"


#database address for aws
# DATABASE = '/home/ubuntu/citibikeapp/citibikeapp/citibike_change.db'

#database address for local testing
DATABASE = 'citibike_change.db'

# where the algo is, should update this in the StationMap
# prefix_url = "/home/ubuntu/citibikeapp/citibikeapp/Algo/Greedy3/"


def create_smap():
    '''Return a stationmap object
    Declare, clean, and update StationMap Object example'''
    smap = StationMap()
    smap.clean()
    smap.update_json()
    return smap

def create_fbs(con,smap):
    """create forbidden stations
    con is sqlite3 connection
    smap is the StationMap object
    return a dictionary with Station Object -> a tuple of datetime objects"""
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
    """Parse and return a dictionary with vehicle id(int) -> list of Break object"""

    # create a dictionary from vehicle ID to how many breaks one of the two drivers
    # on the vehicle has had. {vID int -> [lunchCount int, breakCount int]}
    vb_dic = {}
    sql = """SELECT * FROM DriversShift """
    df = pd.read_sql(sql, con)
    for index, row in df.iterrows():
        lunchCount = int(row["lunchCount"])
        breakCount = int(row["breakCount"])
        if (not row["vID"] is None) and (row["vID"]==row["vID"]): #vID is not None or NaN
            vb_dic[int(row["vID"])] = [lunchCount,breakCount]

    break_dic = {}
    sql = """SELECT * FROM Breaks """
    df = pd.read_sql(sql, con)
    for index, row in df.iterrows():
        vID = int(row["vID"])
        breaks_count = vb_dic.get(vID,[0,0])

        break_duration = 15 #default 15min break
        if int(row["tType"]) == 16:
            if breaks_count[0] == 0:
                break_duration = 30 #lunch break for 30
            else:
                breaks_count[0] -= 1
                vb_dic[vID] = breaks_count
                continue
        else:
            if breaks_count[1] != 0:
                breaks_count[1] -= 1
                vb_dic[vID] = breaks_count
                continue
        # if int(row["tType"]) == 17 or int(row["tType"]) == 18:
        #   break_duration = 15
        break_time = datetimeStringToObject(str(row["publishDateTime"]))
        break_dic[vID] = break_dic.get(vID, []) + [Break(break_time,break_duration)]
    return break_dic

def create_shift_ends(con):
    """Return a dictionary with vehicle ID (int) -> datetime object"""
    shift_end = {}
    sql = """SELECT * FROM Vehicles """
    df = pd.read_sql(sql, con)
    for index, row in df.iterrows():
        endTime = timeStringToObject(str(row["endTime"]))
        shift_end[int(row["vID"])] = endTime
    return shift_end

def create_vehicle_dic(con,smap):
    """create a vehicle dictionary without driverless vehicle. 
    Return a dictionary with vehicle ID (int) -> Truck object"""
    break_dic = parse_breaks(con)
    trucks = {}
    sql = """SELECT * FROM Vehicles Where vID != -111 """ 
    df = pd.read_sql(sql, con)
    for index, row in df.iterrows():
        start_string = str(row["startTime"])
        if str(start_string).lower() != "null" and str(start_string) != "" and str(start_string).lower() != "none": #only pass in signed-in vehicles
            start_time = datetimeStringToObject(str(row["LFTime"])) # Create datetime obj at truck last task finish time for beginning of truck's shift
            # start_time = datetime.today().replace(second=0, microsecond=0)  # Create datetime obj at current time for beginning of truck's shift
            if start_time is None:
                start_time = datetime.now()
            finish_time = timeStringToObject(str(row["endTime"])) # Create datetime obj at estimate truck sign out time for end of truck's shift
            if finish_time is None:
                finish_time = start_time + timedelta(hours=6) # if end time is null, schedule for next 6 hours
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
    """helper function, append task to solution"""
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
        pickup = False
        if int(row["deltaBike"]) > 0:
            pickup = True

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
            task = Task(station, bikes=bikes, pickup=pickup, broken=broken)

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
    """Return the task type of the task in integter """
    if isinstance(task, Task):
        if task.pickup:
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
    """update fixed tasks' bike number in database"""
    for vID in new_prefix_routes:
        for task in new_prefix_routes[vID]:
            if isinstance(task,Task):
                bikeNum = task.bikes
                sID = task.station.id
                tType = parseForType(task)
                cur.execute("""UPDATE OpenTasks SET bikeNum = ? WHERE vID=? and sID = ? and tType = ?""",[bikeNum, vID, sID, tType])
            # if isinstance(task,Break): #don't update break

def assign_driverless_tasks(cur,assigned_driverless):
    """Update driverless tasks' vIDs to real vehicles and delete them from -111 truck"""
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
    """Return the smallest tID in OpenTasksTemp table, which is not in OpenTasks table, return None if no such tID is found"""
    task_search = execute_query(cur,"""SELECT MIN(tID) from OpenTasksTemp""")
    tID = task_search[0][0]
    if tID is None:
        return None
    if is_tID_in_Open(cur,tID):
        # if the tID is in OpenTasks table, find the next smallest one
        return available_tID(cur,vID)
    return tID

def is_tID_in_Open(cur,tID):
    """Return True if tID is in OpenTasks table"""
    task_search2 = execute_query(cur,"""SELECT tID from OpenTasks where tID=?""",[tID])
    cur.execute("""DELETE FROM OpenTasksTemp WHERE tID = ?""",[tID])#won't use this tID anymore, either insert or exist in opentasks table
    if len(task_search2) == 0:
        return False
    else:
        return True

def similar_tID(cur,vID,sID,tType):
    """Return a reusable task ID if found one , return None otherwise"""
    # find if the task is generated before
    task_search = execute_query(cur,"""SELECT tID from OpenTasksTemp where vID=? and sID = ? and tType = ? and fixTask = 0 and vID != -111""",[vID, sID, tType])
    
    if len(task_search) == 0: #not generated before
        return available_tID(cur,vID)
    else: #generated before
        tID = task_search[0][0]
        if not is_tID_in_Open(cur,tID): #check the tID is not in OpenTasks table
            return tID
        else:
            return available_tID(cur,vID)

def assign_algo_break(cur, task, vID, dID1, dID2, orderNum, fixTask):
    """Helper function, add a break task to databse"""
    tType = parseForType(task)

    nowTime = getNYtimenow()
    # completionTime = str(task.end_time)[:19]
    completionTime = None
    priority = 1
    sID = 0
    bikeNum = 0
    comment = None

    tID = similar_tID(cur,vID,sID,tType) #reuse task ID 

    if tID is None: #add with a new tID (task ID)
        cur.execute("""INSERT INTO OpenTasks (publishTime, vID, tType, sID,bikeNum, completionTime, comment, dID1, dID2, priority, orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,0,?)
            """,
          [nowTime, vID, tType, sID, bikeNum, completionTime, comment, dID1, dID2, priority, orderNum, fixTask])
    else: # add with old tID(taskID) 
        cur.execute("""INSERT INTO OpenTasks (tID, publishTime, vID, tType, sID,bikeNum, completionTime, comment, dID1, dID2, priority, orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0,?)
            """,
          [tID, nowTime, vID, tType, sID, bikeNum, completionTime, comment, dID1, dID2, priority, orderNum, fixTask])

def assign_algo_regular_task(cur, task, vID, dID1, dID2, orderNum, fixTask):
    """Helper function for assign_algo_tasks, add a non-break task to databse"""
    nowTime = getNYtimenow()
    bikeNum = task.bikes
    sID = task.station.id
    tType = parseForType(task)
    completionTime = None
    comment = None
    priority = 1

    tID = similar_tID(cur,vID,sID,tType) #reuse task ID 

    if tID is None: #add with a new tID (task ID)
        cur.execute("""INSERT INTO OpenTasks (publishTime, vID, tType, sID,bikeNum, completionTime, comment, dID1, dID2, priority, orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,0,?)
            """,
          [nowTime, vID, tType, sID, bikeNum, completionTime, comment, dID1, dID2, priority, orderNum, fixTask])
    else: # add with old tID(taskID) 
        cur.execute("""INSERT INTO OpenTasks (tID, publishTime, vID, tType, sID,bikeNum, completionTime, comment, dID1, dID2, priority, orderNum,pDL,fixTask) 
         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0,?)
            """,
          [tID, nowTime, vID, tType, sID, bikeNum, completionTime, comment, dID1, dID2, priority, orderNum, fixTask])

def assign_algo_tasks(cur, algo_tasks):
    """Add algorithm generated tasks to database"""
    for vID in algo_tasks:
        dIDs = execute_query(cur,"""SELECT dID1, dID2 FROM Vehicles Where vID = ?""",[vID])
        dID1 = dIDs[0][0]
        dID2 = dIDs[0][1]
        for task in algo_tasks[vID]:
            orderNum = getNextOrderNum(cur,vID) #get the order of the task
            fixTask = 0
            if orderNum == 1:
                fixTask = 1 #fix the task if it's the first task
            if isinstance(task, Task):
                assign_algo_regular_task(cur, task, vID, dID1, dID2, orderNum, fixTask) #assign a task
            if isinstance(task, Break):
                assign_algo_break(cur, task, vID, dID1, dID2, orderNum, fixTask) #assign a break

def complete_dic(trucks,route_dict):
    # better if don;t use this method, currently not used
    """if a vehicle is not in the dictionary, create v:[] in the dictionary"""
    for truck in trucks:
        try:
            route_dict[truck.id]
        except KeyError, e:
            route_dict[truck.id] = []

def run_daytime_algo(con, smap, look_ahead, runtime):
    trucks_dic = create_vehicle_dic(con,smap)
    trucks = trucks_dic.values() #list of trucks
    forbidden_stations = create_fbs(con,smap)
    solution_dic = create_previous_solutions(con,smap)
    shift_end = create_shift_ends(con)
    prefix_routes = solution_dic["prefix"]
    previous_solution = solution_dic["solution"]
    driverless_tasks = solution_dic["driverless"]

    # create pickle files to record input
    # with open("forbidden_stations0.pkl", 'w') as input:
    #     pickle.dump(forbidden_stations, input)
    # with open("prefix_routes0.pkl", 'w') as input:
    #     pickle.dump(prefix_routes, input)
    # with open("previous_solution0.pkl", 'w') as input:
    #     pickle.dump(previous_solution, input)
    # with open("driverless_tasks0.pkl", 'w') as input:
    #     pickle.dump(driverless_tasks, input)
    # with open("shift_end0.pkl", 'w') as input:
    #     pickle.dump(shift_end, input)
    # with open("trucks0.pkl", 'w') as input:
    #     pickle.dump(trucks, input)
    new_solutions = Algorithms.daytime_routing(forbidden_stations, prefix_routes, previous_solution, driverless_tasks, shift_end=shift_end,trucks=trucks, runtime=runtime, look_ahead=look_ahead)

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

def greedyalgo(con, look_ahead, runtime):   
    urlfix = "/var/www/html/citibikeapp/citibikeapp/Algo/Greedy3/"
    cur = con.cursor()
    smap = create_smap()
    # add_fbs(con,smap)

    new_solutions = run_daytime_algo(con, smap, look_ahead, runtime)
    assign_tasks(cur,new_solutions)


if __name__ == '__main__':

    # parse command line arguments
    parser = argparse.ArgumentParser()
    help_str = "first argument is how long in real time minutes does the algorithm predicts;" + "second argument is how many minutes does the algorithm itself runs"
    parser.add_argument("-n","--night", help=help_str, nargs='+', type=int, default=(120,45))
    args = parser.parse_args()
    look_ahead=int(args.night[0])
    runtime=int(args.night[1]) 

    con = sqlite3.connect(DATABASE)
    greedyalgo(con, look_ahead, runtime)
 
    con.commit()
    con.close()