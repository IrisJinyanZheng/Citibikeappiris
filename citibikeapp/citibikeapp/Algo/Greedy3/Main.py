import Algorithms
from StationMap import Truck, StationMap, Task
import time
from copy import copy
from datetime import datetime, timedelta

def daytime_routing(forbidden_stations, prefix_routes, previous_solution, driverless_tasks, shift_end,
                    trucks=None, needs_exit=True, runtime=60, look_ahead=120):
    start = time.time()

    if prefix_routes is None:
        prefix_routes = dict.fromkeys(truck.id for truck in trucks)
    if driverless_tasks is None:
        driverless_tasks = []

    # Create Updated StationMap
    smap = StationMap()
    smap.clean()
    smap.forbidden = forbidden_stations  # Update forbidden stations set

    temp_trucks = []  # Copy truck array
    for j in xrange(len(trucks)):
        temp_trucks.append(copy(trucks[j]))
        temp_trucks[j].visited = []
        temp_trucks[j].route = []
        temp_trucks[j].start = datetime.today().replace(second=0, microsecond=0)
        temp_trucks[j].end = temp_trucks[j].start + timedelta(minutes=look_ahead)

    # Append prefix route to truck
    for truck in temp_trucks:
        route = prefix_routes[truck.id]
        for task in route:
            station = task.station
            current = station.bikes
            optimal = smap.opt_bikes(truck.time, station)

            # If the task is to move a broken bike, don't change the task
            if task.broken:
                opt_task = task

            # Otherwise, check how many bikes should be moved
            elif truck.fill - truck.broken_bikes > 0 and optimal > current:
                opt_task.bikes = min(optimal - current, truck.fill - truck.broken_bikes, station.docks)
                opt_task.to_truck = False

            elif truck.fill < truck.capacity and current > optimal:
                opt_task.bikes = min(current - optimal, truck.capacity - truck.fill)

            else:
                opt_task.bikes = 0

            truck.move(task, smap)

    # Assign driverless tasks
    for task in driverless_tasks:
        assign_task = Algorithms.schedule_task(temp_trucks, smap, task)
        assign_task[0].move(assign_task[1], smap)

    # Evaluate previous routes
    if previous_solution is None:
        best_route = dict.fromkeys(truck.id for truck in trucks)
        best_score = 0
    elif x == x:
        pass
    else:
        if temp_trucks[0].end >= shift_end:
            algo_output = Algorithms.greedy_best(temp_trucks, smap, True)
        else:
            algo_output = Algorithms.greedy_best(temp_trucks, smap, False)
        best_route = algo_output[0]
        best_score = algo_output[1]

    # Run greedy for remainder
    if temp_trucks[0].end >= shift_end:
        algo_output = Algorithms.grasp_time_best(trucks, smap, runtime - time.time() - start, 5, True, best_score)
    else:
        algo_output = Algorithms.grasp_time_best(trucks, smap, runtime - time.time() - start, 5, False, best_score)

    if algo_output[1] > best_score:
        best_route = algo_output[0]

    return best_route
