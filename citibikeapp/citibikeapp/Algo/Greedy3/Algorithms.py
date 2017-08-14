from StationMap import StationMap, Break
from copy import copy
import time
from datetime import datetime, timedelta
from operator import attrgetter, itemgetter


def greedy_finish(trucks=None, smap=StationMap(), needs_exit=None):
    if trucks is None:
        trucks = []
    if needs_exit is None:
        needs_exit = dict.fromkeys([truck.id for truck in trucks], True)
    else:
        for truck in trucks:
            if needs_exit.get(truck.id) is None:
                needs_exit[truck.id] = True

    routes = {}
    temp_trucks = []
    score = 0
    for j in xrange(len(trucks)):
        temp_trucks.append(copy(trucks[j]))
        temp_trucks[j].visited = []
        temp_trucks[j].route = []

    while len(temp_trucks) > 0:
        i = min(temp_trucks, key=attrgetter('time'))
        if i.breaks and i.time >= i.breaks[0].start_time:
            i.take_break()
        else:
            t = i.greedy_move(smap, needs_exit[i.id])
            if t is not None:
                i.move(t, smap)
            else:
                routes[i.id] = i.route
                score = score + i.improvement
                temp_trucks.remove(i)

    return routes, score


def greedy_iterative(trucks=None, smap=StationMap(), needs_exit=None):
    if trucks is None:
        trucks = []
    if needs_exit is None:
        needs_exit = dict.fromkeys([truck.id for truck in trucks], True)
    else:
        for truck in trucks:
            if needs_exit.get(truck.id) is None:
                needs_exit[truck.id] = True

    routes = {}
    temp_trucks = []
    score = 0
    for j in xrange(len(trucks)):
        temp_trucks.append(copy(trucks[j]))
        temp_trucks[j].visited = []
        temp_trucks[j].route = []

    for i in temp_trucks:
        t = i.greedy_move(smap, needs_exit[i.id])
        while t is not None:
            if i.breaks and i.time >= i.breaks[0].start_time:
                i.take_break()
            else:
                i.move(t, smap)
            t = i.greedy_move(smap, needs_exit[i.id])
        routes[i.id] = i.route
        score = score + i.improvement

    return routes, score


def greedy_best(trucks=None, smap=StationMap(), needs_exit=None):
    if trucks is None:
        trucks = []
    if needs_exit is None:
        needs_exit = dict.fromkeys([truck.id for truck in trucks], True)
    else:
        for truck in trucks:
            if needs_exit.get(truck.id) is None:
                needs_exit[truck.id] = True

    score = 0
    temp_trucks = []
    for j in xrange(len(trucks)):
        temp_trucks.append(copy(trucks[j]))
        temp_trucks[j].visited = []
        temp_trucks[j].route = []
    routes = {}
    tasks = dict.fromkeys([truck.id for truck in trucks])

    for i in temp_trucks:
        t = i.greedy_move(smap, needs_exit[i.id])
        if t is not None:
            tasks[i.id] = (i, t, t.improvement(i, smap) / t.time(i, smap))
        else:
            routes[i.id] = i.route
            score = score + i.improvement
            temp_trucks.remove(i)
            tasks[i.id] = (i, None, -1)

    while len(temp_trucks) > 0:
        next_truck = max(tasks.values(), key=itemgetter(2))[0]
        next_task = tasks[next_truck.id][1]

        if next_task is not None:
            if next_truck.breaks and next_truck.time >= next_truck.breaks[0].start_time:
                next_truck.take_break()
            else:
                next_truck.move(next_task, smap)

            for i in temp_trucks:
                if tasks[i.id][1].station == next_task.station:
                    t = i.greedy_move(smap, needs_exit[i.id])
                    if t is not None:
                        tasks[i.id] = (i, t, t.improvement(i, smap) / t.time(i, smap))
                    else:
                        routes[i.id] = i.route
                        score = score + i.improvement
                        temp_trucks.remove(i)
                        tasks[i.id] = (i, None, -1)

    return routes, score


def grasp_finish(trucks=None, smap=StationMap(), iterations=1, k=5, needs_exit=None):
    if trucks is None:
        trucks = []
    if needs_exit is None:
        needs_exit = dict.fromkeys([truck.id for truck in trucks], True)
    else:
        for truck in trucks:
            if needs_exit.get(truck.id) is None:
                needs_exit[truck.id] = True

    best_score = 0
    best_route = {}
    for truck in trucks:
        best_route[truck.id] = []

    for i in xrange(iterations):
        smap.restore()
        temp_trucks = []
        for j in xrange(len(trucks)):
            temp_trucks.append(copy(trucks[j]))
            temp_trucks[j].visited = []
            temp_trucks[j].route = []
        temp_route = {}
        temp_score = 0

        while len(temp_trucks) > 0:
            i = min(temp_trucks, key=attrgetter('time'))
            if i.breaks and i.time >= i.breaks[0].start_time:
                i.take_break()
            else:
                t = i.greedy_random_move(smap, k, needs_exit[i.id])
                if t is not None:
                    i.move(t, smap)
                else:
                    temp_score = temp_score + i.improvement
                    temp_route[i.id] = i.route
                    temp_trucks.remove(i)

        if temp_score > best_score:
            best_score = temp_score
            best_route = temp_route

    return best_route, best_score


def grasp_iterative(trucks=None, smap=StationMap(), iterations=1, k=5, needs_exit=None):
    if trucks is None:
        trucks = []
    if needs_exit is None:
        needs_exit = dict.fromkeys([truck.id for truck in trucks], True)
    else:
        for truck in trucks:
            if needs_exit.get(truck.id) is None:
                needs_exit[truck.id] = True

    best_score = 0
    best_route = {}
    for truck in trucks:
        best_route[truck.id] = []

    for i in xrange(iterations):
        smap.restore()
        temp_trucks = []
        for j in xrange(len(trucks)):
            temp_trucks.append(copy(trucks[j]))
            temp_trucks[j].visited = []
            temp_trucks[j].route = []

        for j in temp_trucks:
            t = j.greedy_random_move(smap, k, needs_exit[j.id])
            while t is not None:
                if j.breaks and j.time >= j.breaks[0].start_time:
                    j.take_break()
                else:
                    j.move(t, smap)
                t = j.greedy_random_move(smap, needs_exit[j.id])

        delta = 0
        for j in temp_trucks:
            delta = delta + j.improvement

        if delta > best_score:
            best_score = delta
            for t in temp_trucks:
                best_route[t.id] = t.route

    return best_route, best_score


def grasp_best(trucks=None, smap=StationMap(), iterations=1, k=5, needs_exit=None):
    if trucks is None:
        trucks = []
    if needs_exit is None:
        needs_exit = dict.fromkeys([truck.id for truck in trucks], True)
    else:
        for truck in trucks:
            if needs_exit.get(truck.id) is None:
                needs_exit[truck.id] = True

    best_score = 0
    best_route = {}
    for truck in trucks:
        best_route[truck.id] = []

    for i in xrange(iterations):
        smap.restore()
        temp_trucks = []
        for j in xrange(len(trucks)):
            temp_trucks.append(copy(trucks[j]))
            temp_trucks[j].visited = []
            temp_trucks[j].route = []
        incompleted = copy(temp_trucks)
        temp_route = {}
        temp_score = 0
        tasks = dict.fromkeys([truck.id for truck in trucks])

        for truck in temp_trucks:
            t = truck.greedy_random_move(smap, k, needs_exit[truck.id])
            if t is not None:
                tasks[truck.id] = (truck, t, t.improvement(truck, smap) / t.time(truck, smap))
            else:
                temp_score = temp_score + truck.improvement
                temp_route[truck.id] = truck.route
                incompleted.remove(truck)
                tasks[truck.id] = (truck, None, -1)

        while len(incompleted) > 0:
            next_truck = max(tasks.values(), key=itemgetter(2))[0]
            next_task = tasks[next_truck.id][1]

            if next_task is not None:
                if next_truck.breaks and next_truck.time >= next_truck.breaks[0].start_time:
                    next_truck.take_break()
                else:
                    next_truck.move(next_task, smap)

                for truck in temp_trucks:
                    if tasks[truck.id][1] is not None and tasks[truck.id][1].station == next_task.station:
                        t = truck.greedy_random_move(smap, k, needs_exit[truck.id])

                        if t is not None:
                            tasks[truck.id] = (truck, t, t.improvement(truck, smap) / t.time(truck, smap))
                        else:
                            temp_score = temp_score + truck.improvement
                            temp_route[truck.id] = truck.route
                            incompleted.remove(truck)
                            tasks[truck.id] = (truck, None, -1)

        if temp_score > best_score:
            best_score = temp_score
            best_route = temp_route

    return best_route, best_score


def schedule_task(trucks=None, smap=StationMap(), task=None, thresh=0.5, needs_exit=None):
    if trucks is None:
        trucks = []
    if needs_exit is None:
        needs_exit = dict.fromkeys([truck.id for truck in trucks], False)
    else:
        for truck in trucks:
            if needs_exit.get(truck.id) is None:
                needs_exit[truck.id] = False

    scheduled_truck = None
    scheduled_task = None

    if thresh < 0:
        thresh = 0

    if task is not None:
        feasible = {}
        min_time = datetime.max

        # Check if task if feasible for any trucks
        for i in trucks:
            if task.feasible(i, smap, needs_exit[i.id]):
                feasible[i] = task

        # If task is not feasible for any trucks, check if partial task is feasible
        if not feasible:
            threshold = task.bikes * thresh
            for i in trucks:
                temp_task = task.fix(i, smap, needs_exit[i.id])

                if temp_task.bikes >= threshold and temp_task.feasible(i, smap, needs_exit[i.id]):
                    feasible[i] = temp_task

        # Find truck that can finish the task the fastest
        for i in feasible:
            total_time = i.time + timedelta(seconds=task.time(i, smap))
            if total_time < min_time:
                scheduled_truck = i
                scheduled_task = feasible[i]
                min_time = total_time

    return scheduled_truck, scheduled_task


def grasp_time_best(trucks=None, smap=StationMap(), seconds=1, k=5, needs_exit=None, start_score=0):
    start = time.time()

    if trucks is None:
        trucks = []
    if needs_exit is None:
        needs_exit = dict.fromkeys([truck.id for truck in trucks], True)
    else:
        for truck in trucks:
            if needs_exit.get(truck.id) is None:
                needs_exit[truck.id] = True

    best_score = start_score
    best_route = {}
    for truck in trucks:
        best_route[truck.id] = []

    while time.time() - start < seconds - 2:
        smap.restore()
        temp_trucks = []
        for j in xrange(len(trucks)):
            temp_trucks.append(copy(trucks[j]))
            temp_trucks[j].visited = []
            temp_trucks[j].route = []
        incomplete = copy(temp_trucks)
        temp_route = {}
        temp_score = 0
        tasks = dict.fromkeys([truck.id for truck in trucks])

        for truck in temp_trucks:
            t = truck.greedy_random_move(smap, k, needs_exit[truck.id])
            if t is not None:
                tasks[truck.id] = (truck, t, t.improvement(truck, smap) / t.time(truck, smap))
            else:
                temp_score = temp_score + truck.improvement
                temp_route[truck.id] = truck.route
                incomplete.remove(truck)
                tasks[truck.id] = (truck, None, -1)

        while len(incomplete) > 0:
            next_truck = max(tasks.values(), key=itemgetter(2))[0]
            next_task = tasks[next_truck.id][1]

            if next_task is not None:
                if next_truck.breaks and next_truck.time >= next_truck.breaks[0].start_time:
                    next_truck.take_break()
                else:
                    next_truck.move(next_task, smap)

                for truck in temp_trucks:
                    if tasks[truck.id][1] is not None and tasks[truck.id][1].station == next_task.station:
                        t = truck.greedy_random_move(smap, k, needs_exit[truck.id])

                        if t is not None:
                            tasks[truck.id] = (truck, t, t.improvement(truck, smap) / t.time(truck, smap))
                        else:
                            temp_score = temp_score + truck.improvement
                            temp_route[truck.id] = truck.route
                            incomplete.remove(truck)
                            tasks[truck.id] = (truck, None, -1)

        if temp_score > best_score:
            best_score = temp_score
            best_route = temp_route

    return best_route, best_score


def daytime_routing(forbidden_stations, prefix_routes, previous_solution, driverless_tasks,
                    shift_end=None, trucks=None, runtime=60, look_ahead=120):
    start = time.time()

    if prefix_routes is None:
        prefix_routes = dict.fromkeys([truck.id for truck in trucks])
    if driverless_tasks is None:
        driverless_tasks = []
    if shift_end is None:
        shift_end = dict.fromkeys([truck.id for truck in trucks], datetime.max)

    # Create Updated StationMap
    smap = StationMap()
    smap.clean()
    smap.forbidden = forbidden_stations  # Update forbidden stations set

    # Copy truck array and see if you need to allocate time for exiting
    adapted_trucks = []
    needs_exit = dict.fromkeys([truck.id for truck in trucks])
    for j in xrange(len(trucks)):
        id_number = trucks[j].id
        adapted_trucks.append(copy(trucks[j]))
        adapted_trucks[j].visited = []
        adapted_trucks[j].route = []
        # Algorithm computes look_ahead minutes from now unless the shifts end before that
        look_ahead_end = datetime.today() + timedelta(minutes=look_ahead)
        if shift_end.get(id_number) is None:
            adapted_trucks[j].end = look_ahead_end
            needs_exit[id_number] = False
        elif shift_end[id_number] >= look_ahead_end:
            adapted_trucks[j].end = look_ahead_end
            needs_exit[id_number] = False
        else:
            adapted_trucks[j].end = shift_end[id_number]
            needs_exit[id_number] = True

    # Append prefix route to truck
    fixed_tasks = {}
    for truck in adapted_trucks:
        if prefix_routes.get(truck.id) is None:
            route = []
        else:
            route = prefix_routes[truck.id]
        for task in route:
            # If task is break, take a break
            if isinstance(task, Break):
                truck.time = truck.time + task.duration
            else:
                station = task.station
                # If the task is to move a broken bike, don't change the task
                if task.broken:
                    opt_task = task.fix(truck, smap, needs_exit[truck.id])
                # Otherwise, check how many bikes should be moved
                else:
                    opt_task = smap.opt_task(truck, station)
                    if not opt_task.feasible(truck, smap, needs_exit[truck.id]):
                        opt_task.fix(truck, smap, needs_exit[truck.id])

                truck.move(opt_task, smap)

        # Take a break after prefix route if the truck is due for one
        if truck.breaks and truck.time >= truck.breaks[0].start_time:
            truck.take_break()
        # Clear route after truck performs fixed tasks
        fixed_tasks[truck.id] = truck.route
        truck.route = []

    # Assign driverless tasks
    assigned_driverless_tasks = {}
    for task in driverless_tasks:
        assign_task = schedule_task(adapted_trucks, smap, task[0])
        if assign_task[1] is not None:
            assign_task[0].move(assign_task[1], smap)

    for truck in adapted_trucks:
        # Take a break after prefix route if the truck is due for one
        if truck.breaks and truck.time >= truck.breaks[0].start_time:
            truck.take_break()
        # Clear route after assigning driverless tasks
        assigned_driverless_tasks[truck.id] = truck.route
        truck.route = []

    # Copy trucks for algorithm
    temp_trucks = []
    for j in xrange(len(trucks)):
        temp_trucks.append(copy(adapted_trucks[j]))
        temp_trucks[j].improvement = 0

    # Evaluate previous routes
    if previous_solution is None:
        # If there is no previous solution, simply run the pure greedy algorithm
        algo_output = greedy_best(temp_trucks, smap, needs_exit)
        best_route = algo_output[0]
        best_score = algo_output[1]
    else:
        best_route = {}
        best_score = 0
        for truck in temp_trucks:
            if previous_solution.get(truck.id) is None or previous_solution[truck.id] == []:
                route = greedy_best([truck], smap, needs_exit)[0][truck.id]
            else:
                route = previous_solution[truck.id]
            for task in route:
                if isinstance(task, Break):
                    truck.time = truck.time + task.duration
                else:
                    if task.broken:
                        if truck.capacity - truck.fill < task.bikes:
                            task.bikes = truck.capacity-truck.fill
                        opt_task = task
                    else:
                        opt_task = smap.opt_task(truck, task.station)
                        if not opt_task.feasible(truck, smap, needs_exit[truck.id]):
                            opt_task = opt_task.fix(truck, smap, needs_exit[truck.id])

                    truck.move(opt_task, smap)

            best_route[truck.id] = truck.route
            best_score = best_score + truck.improvement

    # Copy trucks for algorithm
    temp_trucks = []
    for j in xrange(len(trucks)):
        temp_trucks.append(copy(adapted_trucks[j]))
        temp_trucks[j].improvement = 0

    # Run greedy for remainder
    algo_output = grasp_time_best(temp_trucks, smap, runtime - time.time() + start, 5, needs_exit, best_score)

    if algo_output[1] > best_score:
        best_route = algo_output[0]

    return fixed_tasks, assigned_driverless_tasks, best_route
