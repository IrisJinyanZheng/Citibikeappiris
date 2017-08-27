import time
from copy import copy
from datetime import datetime, timedelta
from operator import attrgetter, itemgetter

from StationMap import StationMap, Break


def greedy_finish(trucks=None, smap=StationMap(), needs_exit=None):
    """A greedy algorithm that chooses the next best greedy task based for the truck that finished its last task the
    earliest.

    :param trucks: A list of active trucks
    :type trucks: List[Truck]
    :param smap: The StationMap the algorithm is working on
    :type smap: StationMap
    :param needs_exit: A dictionary that describes which trucks in the truck list must return to their destination by
        the end of their shift. Defaults to True for all trucks.
    :type needs_exit: Dict[bool]

    """
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
        while i.breaks and i.time >= i.breaks[0].start_time  - timedelta(minutes=20):
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
    """A greedy algorithm that calculates a complete route, consisting of the best greedy moves, for each truck
    one-by-one.

    :param trucks: A list of active trucks
    :type trucks: List[Truck]
    :param smap: The StationMap the algorithm is working on
    :type smap: StationMap
    :param needs_exit: A dictionary that describes which trucks in the truck list must return to their destination
        by the end of their shift. Defaults to True for all trucks.
    :type needs_exit: Dict[bool]

    """
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
            while i.breaks and i.time >= i.breaks[0].start_time - timedelta(minutes=20):
                i.take_break()
            else:
                i.move(t, smap)
            t = i.greedy_move(smap, needs_exit[i.id])
        routes[i.id] = i.route
        score = score + i.improvement

    return routes, score


def greedy_best(trucks=None, smap=StationMap(), needs_exit=None):
    """A greedy algorithm that calculates the next best greedy move for every truck and appends the best move that is in
    that sets of moves, iterating until each truck has a complete route. Defaults to True for all trucks.

    :param trucks: A list of active trucks
    :type trucks: List[Truck]
    :param smap: The StationMap the algorithm is working on
    :type smap: StationMap
    :param needs_exit: A dictionary that describes which trucks in the truck list must return to their destination
        by the end of their shift
    :type needs_exit: Dict[bool]

    """
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
    incomplete = copy(temp_trucks)
    routes = {}
    tasks = dict.fromkeys([truck.id for truck in trucks])

    for i in temp_trucks:
        while i.breaks and i.time >= i.breaks[0].start_time - timedelta(minutes=20):
            i.take_break()
        t = i.greedy_move(smap, needs_exit[i.id])
        if t is not None:
            tasks[i.id] = (i, t, t.improvement(i, smap) / t.time(i, smap))
        else:
            routes[i.id] = i.route
            score = score + i.improvement
            incomplete.remove(i)
            tasks[i.id] = (i, None, -1)

    while len(incomplete) > 0:
        next_truck = max(tasks.values(), key=itemgetter(2))[0]
        next_task = tasks[next_truck.id][1]

        if next_task is not None:
            next_truck.move(next_task, smap)
            while next_truck.breaks and next_truck.time >= next_truck.breaks[0].start_time - timedelta(minutes=20):
                next_truck.take_break()

            for i in temp_trucks:
                if tasks[i.id][1] is not None and tasks[i.id][1].station == next_task.station:
                    t = i.greedy_move(smap, needs_exit[i.id])
                    if t is not None:
                        tasks[i.id] = (i, t, t.improvement(i, smap) / t.time(i, smap))
                    else:
                        routes[i.id] = i.route
                        score = score + i.improvement
                        incomplete.remove(i)
                        tasks[i.id] = (i, None, -1)

    return routes, score


def grasp_finish(trucks=None, smap=StationMap(), iterations=1, k=5, needs_exit=None):
    """A GRASP algorithm that chooses the next GRASP-selected task based for the truck that finished its last task the
    earliest.

    :param trucks: A list of active trucks
    :type trucks: List[Truck]
    :param smap: The StationMap the algorithm is working on
    :type smap: StationMap
    :param iterations: The number of GRASP iterations to run before picking the best solution
    :type iterations: int
    :param k: The length of the k list of tasks the GRASP will choose from
    :type k: int
    :param needs_exit: A dictionary that describes which trucks in the truck list must return to their destination by
        the end of their shift. Defaults to all trucks needing to return to their final destination.
    :type needs_exit: Dict[bool]

    """
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
            while i.breaks and i.time >= i.breaks[0].start_time - timedelta(minutes=20):
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
    """A GRASP algorithm that calculates a complete route, consisting of the selected GRASP moves, for each truck
    one-by-one.

    :param trucks: A list of active trucks
    :type trucks: List[Truck]
    :param smap: The StationMap the algorithm is working on
    :type smap: StationMap
    :param iterations: The number of GRASP iterations to run before picking the best solution
    :type iterations: int
    :param k: The length of the k list of tasks the GRASP will choose from
    :type k: int
    :param needs_exit: A dictionary that describes which trucks in the truck list must return to their destination by
        the end of their shift. Defaults to all trucks needing to return to their final destination.
    :type needs_exit: Dict[bool]

    """
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
                while j.breaks and j.time >= j.breaks[0].start_time - timedelta(minutes=20):
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
    """A GRASP algorithm that calculates the next GRASP-selected task for every truck and appends the best move that is
    in that sets of moves, iterating until each truck has a complete route.

    :param trucks: A list of active trucks
    :type trucks: List[Truck]
    :param smap: The StationMap the algorithm is working on
    :type smap: StationMap
    :param iterations: The number of GRASP iterations to run before picking the best solution
    :type iterations: int
    :param k: The length of the k list of tasks the GRASP will choose from
    :type k: int
    :param needs_exit: A dictionary that describes which trucks in the truck list must return to their destination by
        the end of their shift. Defaults to all trucks needing to return to their final destination.
    :type needs_exit: Dict[bool]

    """
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
            while truck.breaks and truck.time >= truck.breaks[0].start_time - timedelta(minutes=20):
                truck.take_break()
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
                next_truck.move(next_task, smap)
                while next_truck.breaks and next_truck.time >= next_truck.breaks[0].start_time - timedelta(minutes=20):
                    next_truck.take_break()

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
    """ Schedules a given task for one of the trucks operating in a StationMap. Out of all the trucks that can feasibly
    complete the task, it selects the truck that can complete it by the earliest time. If no trucks can feasibly
    complete the task finds the maximum number of bikes each truck can move while still finishing the task before the
    end of its shift. Out of all the trucks that can feasibly move bikes that are above a threshold value, it selects
    the truck that can complete it by the earliest time. Does nothing if this is impossible for all trucks.

    :param trucks: A list of active trucks
    :type trucks: List[Truck]
    :param smap: The StationMap the algorithm is working on
    :type smap: StationMap
    :param task: The task to be assigned to a truck
    :type task: Task
    :param thresh: The threshold value from 0 to 1. 0 means that the task will be assigned if any truck can go to the
        task's station and move any number of bikes. 1 means the task will only be assigned if a truck can go to the
        station and move exactly the number of bikes the task originally had. Defaults to 50%.
    :type thresh: float
    :param needs_exit: A dictionary that describes which trucks in the truck list must return to their destination by
        the end of their shift. Defaults to all trucks not needing to return to their final destination.
    :type needs_exit: Dict[bool]

    """
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


def grasp_time_best(trucks=None, smap=StationMap(), seconds=10, k=5, needs_exit=None, start_score=0):
    """A version of :meth:`grasp_best` that iterates based on real-life runtime rather than number of iterations.

    :param trucks: A list of active trucks
    :type trucks: List[Truck]
    :param smap: The StationMap the algorithm is working on
    :type smap: StationMap
    :param seconds: The number of seconds the GRASP will run before picking the best solution. Defaults to 10
    :type seconds: int
    :param k: The length of the k list of tasks the GRASP will choose from. Defaults to 5
    :type k: int
    :param needs_exit: A dictionary that describes which trucks in the truck list must return to their destination by
        the end of their shift. Defaults to all trucks needing to return to their final destination.
    :type needs_exit: Dict[bool]
    :param start_score: The minimum score the algorithm should find if it returns a route. Defaults to 0
    :type start_score: float

    """
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
            while truck.breaks and truck.time >= truck.breaks[0].start_time - timedelta(minutes=20):
                truck.take_break()
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
                next_truck.move(next_task, smap)
                while next_truck.breaks and next_truck.time >= next_truck.breaks[0].start_time - timedelta(minutes=20):
                    next_truck.take_break()

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
    """An algorithm for moving-horizon routing during the day when many customers are engaging with the StationMap
    system

    :param forbidden_stations: A dictionary of forbidden stations from now until the end of the look ahead period.
    :type forbidden_stations: Dict[int, Tuple[datetime, datetime]
    :param prefix_routes: A dictionary of assigned tasks who's station and order cannot change
    :type prefix_routes: Dict[int, List[Task]]
    :param previous_solution: A dictionary of the previously found best solution.
    :type previous_solution: Dict[int, List[Task]]
    :param driverless_tasks: A list of driverless tasks to be assigned and their deadlines.
    :type driverless_tasks: List[Tuple[Task, datetime]]
    :param shift_end: A dictionary of the shift ending times for each truck. Defaults to each truck having no shift end
        time.
    :type shift_end: Dict[int, datetime]
    :param trucks: A list of active trucks
    :type trucks: List[Truck]
    :param runtime: The amount of time the algorithm should run in seconds. Defaults to 60.
    :type runtime: int
    :param look_ahead: The time period the algorithm will look ahead and calculate a route for in minutes. Defaults to
        120.
    :type look_ahead: int

    """
    start = time.time()

    fixed_tasks = {}  # Dict of the fixed tasks for each truck
    assigned_driverless_tasks = {}  # Dict of the assigned driverless tasks for each truck
    best_route = {}  # Dict of the best route found after performing fixed/driverless tasks for each truck
    best_score = 0

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

        # Clear route after truck performs fixed tasks
        fixed_tasks[truck.id] = truck.route
        truck.route = []

        # Take a break after prefix route if the truck is due for one
        while truck.breaks and truck.time >= truck.breaks[0].start_time - timedelta(minutes=20):
            truck.take_break()

    # Assign driverless tasks
    for task in driverless_tasks:
        assign_task = schedule_task(adapted_trucks, smap, task[0])
        if assign_task[1] is not None:
            assign_task[0].move(assign_task[1], smap)
            # Take a break after prefix route if the truck is due for one
            while truck.breaks and truck.time >= truck.breaks[0].start_time - timedelta(minutes=20):
                truck.take_break()

    for truck in adapted_trucks:
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
        # If there is a previous solution, evaluate it
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

    # Set best route to GRASP route, if the GRASP route is superior
    if algo_output[1] > best_score:
        best_route = algo_output[0]

    return fixed_tasks, assigned_driverless_tasks, best_route
