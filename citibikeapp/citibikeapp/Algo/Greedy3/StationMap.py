import cPickle as pickle
import copy
import random
from bisect import bisect_right
from datetime import datetime, timedelta
from json import loads
from urllib import urlopen


class Station:
    """Specifies a bikeshare station with bikes and docks

    :ivar id: The ID number of the station. Defaults to -1
    :vartype id: int
    :ivar bikes: The number of bikes (including broken bikes) currently at this station. Defaults to 0
    :vartype bikes: int
    :ivar docks: The number of docks at this station that are empty and not broken. Defaults to 0
    :vartype docks: int
    :ivar rate: The amount of time in seconds it takes for a truck to park at this station. Defaults to 120
    :vartype rate: int

    """

    def __init__(self, index, iden=-1, bikes=0, docks=0, rate=120):
        # type: (int, int, int, int, int) -> Station
        self.index = index
        self.id = iden
        self.bikes = bikes
        self.docks = docks
        self.rate = rate

    def add_bikes(self, bikes):
        # type: (int) -> None
        """Adds bikes to this Station

        :param bikes: The number of bikes to be added
        :type bikes: int

        """
        self.bikes = self.bikes + bikes
        self.docks = self.docks - bikes

    def remove_bikes(self, bikes):
        # type: (int) -> None
        """Removes bikes from this Station

        :param bikes: The number of bikes to be removed
        :type bikes: int

        """
        self.bikes = self.bikes - bikes
        self.docks = self.docks + bikes

    def __str__(self):
        return "Station " + str(self.id) + " with " + str(self.bikes) + " bikes and " + str(self.docks) + " docks"


class Break:
    """Specifies a break period for a truck to take

    :ivar start_time: The date and time of when the break starts
    :vartype start_time: datetime
    :ivar duration: The length of the break in seconds
    :vartype duration: int
    :ivar end_time: The date and time of when the break ends. Calculated in initialization with start_time and duration
    :vartype end_time: datetime

    """
    def __init__(self, start_time, duration):
        # type: (datetime, int) -> Break
        self.start_time = start_time
        self.duration = timedelta(minutes=duration)
        self.end_time = self.start_time + self.duration


class Task:
    """Specifies a rebalencing task for a driver to perform

    :ivar station: The station where bikes should be moved.
    :vartype station: Station
    :ivar bikes: The number of bikes to be moved. Defaults to 0.
    :vartype bikes: int
    :ivar pickup: Is true if bikes are to be picked up into the truck; is false if bikes are to be dropped off.
        Defaults to True
    :vartype pickup: bool
    :ivar broken: Is true if moving broken bikes; if false if moving regular bikes. Defaults to False.
    :vartype broken: bool

    """

    def __init__(self, station, bikes=0, pickup=True, broken=False):
        # type: (Station, int, bool, bool) -> Task
        self.station = station
        self.bikes = bikes
        self.pickup = pickup
        self.broken = broken

    def time(self, truck, smap):
        """Finds how long it takes for this task to be completed

        :param truck: The truck that is performing this task
        :type truck: Truck
        :param smap: The StationMap that this task's station is on
        :type smap: StationMap
        :returns: The time in seconds it takes for this truck to complete this task
        :rtype: int

        """
        # type: (Truck, StationMap) -> int
        to_loc = smap.paths[truck.location.id][self.station.id] + self.station.rate
        to_pick_up = truck.rate * self.bikes

        return to_loc + to_pick_up

    def feasible(self, truck, smap, needs_exit=True):
        """Figures out where this task can be completed

        :param truck: The truck that is performing this task
        :type truck: Truck
        :param smap: The StationMap that this task's station is on
        :type smap: StationMap
        :param needs_exit: Specifies whether time must be allotted for the truck to return to its destination. Returns
            True if it needs to return, and False if it doesn't. Defaults to True.
        :type needs_exit: bool
        :returns: True if this task can be completed, and False if it cannot.
        :rtype: bool

        """
        # type: (Truck, StationMap, bool) -> bool
        if self.pickup:
            if self.bikes > self.station.bikes or self.bikes > truck.capacity - truck.fill:
                return False
        else:
            if self.broken:
                if self.bikes > truck.broken_bikes or self.bikes > self.station.docks:
                    return False
            else:
                if self.bikes > truck.fill - truck.broken_bikes or self.bikes > self.station.docks:
                    return False

        time = self.time(truck, smap)

        if needs_exit:
            to_exit = smap.paths[self.station.id][truck.destination.id]
        else:
            to_exit = 0

        if truck.time + timedelta(seconds=time + to_exit) > truck.end:
            return False
        else:
            return True

    def fix(self, truck, smap, needs_exit=True):
        """Fixes changes the number of bikes so that it improves the Station Map and is feasible

        :param truck: The truck that is performing this task
        :type truck: Truck
        :param smap: The StationMap that this task's station is on
        :type smap: StationMap
        :param needs_exit: Specifies whether time must be allotted for the truck to return to its destination. Returns
            True if it needs to return, and False if it doesn't. Defaults to True.
        :type needs_exit: bool
        :returns: A new task that improves (or maintains) the StationMap and is feasible
        :rtype: Task

        """
        # type: (Truck, StationMap, bool) -> Task
        new_bikes = self.bikes

        if self.pickup:
            if new_bikes > truck.capacity - truck.fill:
                new_bikes = truck.capacity - truck.fill
            if new_bikes > self.station.bikes:
                new_bikes = self.station.bikes
        else:
            if new_bikes > truck.fill - truck.broken_bikes:
                new_bikes = truck.fill - truck.broken_bikes
            if new_bikes > self.station.docks:
                new_bikes = self.station.docks

        to_loc = smap.paths[truck.location.id][self.station.id] + self.station.rate
        to_pick_up = truck.rate * new_bikes

        if needs_exit:
            to_exit = smap.paths[self.station.id][truck.destination.id]
        else:
            to_exit = 0

        tot_time = to_loc + to_pick_up + to_exit

        if timedelta(seconds=tot_time) > truck.end - truck.time:
            excess_bikes = ((timedelta(seconds=tot_time) - (truck.end - truck.time)).seconds / truck.rate) + 1
            new_bikes = new_bikes - excess_bikes

        if new_bikes < 0:
            new_bikes = 0

        return Task(self.station, new_bikes, self.pickup)

    def improvement(self, truck, smap):
        # type: (Truck, StationMap) -> float
        """Calculates by how much the number of disappointed customers is reduced through this task

        :param truck: The truck that is performing this task
        :type truck: Truck
        :param smap: The StationMap that this task's station is on
        :type smap: StationMap
        :returns: The change in disappointed customers. Positive if the StationMap has less expected, disappointed
            customers, negative if it has more expected, disappointed customers
        :rtype: float

        """
        # Returns 0 improvement if dropping off broken bikes
        if self.broken and not self.pickup:
            return 0

        time = truck.time + timedelta(seconds=self.time(truck, smap))
        original = smap.stations[self.station.id].bikes

        if self.pickup:
            new = original - self.bikes
        else:
            new = original + self.bikes

        original_cost = smap.compute_disappointed_customers(time, self.station, original)
        new_cost = smap.compute_disappointed_customers(time, self.station, new)
        cost_change = original_cost - new_cost

        return cost_change

    def __str__(self):
        if self.pickup:
            s = 'from'
        else:
            s = 'to'
        return 'Move ' + str(self.bikes) + ' bikes ' + s + ' station ' + str(self.station.id)


class Truck:
    """Specifies a Rebalencing Truck

    :ivar id: The ID number of the truck. Defaults to -1.
    :vartype id: int
    :ivar capacity: The number of bikes that can fit on the truck. Defaults to 42.
    :vartype capacity: int
    :ivar fill: The number of total bikes (including broken bikes) loaded onto the truck. Defaults to 0.
    :vartype fill: int
    :ivar broken_bikes: The number of broken bikes loaded onto this truck. Defaults to 0
    :vartype broken_bikes: int
    :ivar breaks: List of Breaks scheduled for this truck. Defaults to empty list.
    :vartype breaks: list[Break]
    :ivar rate: The amount of time in seconds it takes the driver on this truck to move one bike. Defaults to 30 sec.
    :vartype rate: int
    :ivar origin: The Station that this truck started its shift at
    :vartype origin: Station
    :ivar location: The Station where this truck finished its last Task
    :vartype location: Station
    :ivar destination: The Station where this truck will return to at the end of its shift
    :vartype destination: Station
    :ivar start: The starting time of this truck's shift
    :vartype start: datetime
    :ivar end: The ending time of this truck's shift
    :vartype start: datetime

    """
    def __init__(self, origin, location, destination, start=datetime.min, end=datetime.min,
                 iden=-1, capacity=42, fill=0, broken_bikes=0, breaks=None, rate=30):
        # type: (Station, Station, Station, datetime, datetime, int, int, int, int, list, int) -> Truck
        self.id = iden  # Truck ID #

        # Truck dimensions
        self.capacity = capacity
        self.broken_bikes = broken_bikes
        self.fill = fill
        if self.fill < self.broken_bikes:
            self.fill = self.broken_bikes

        # Time it takes for driver to move 1 bike
        self.rate = rate

        # Locational information
        self.origin = origin
        self.location = location
        self.destination = destination

        # Shift period information
        self.start = start
        self.time = start
        self.end = end

        # Tasks completed by truck, and stations visited by truck
        self.route = []
        self.visited = []

        # Total improvement truck has performed
        self.improvement = 0

        # Break periods for truck
        if breaks is None:
            breaks = []
        breaks.sort(key=lambda x: x.start_time)
        self.breaks = breaks

    def add_bikes(self, station, bikes, broken):
        # type: (Station, int, bool) -> None
        """Adds bikes to this truck and removes bikes from the station this truck is taking from

        :param station: The station is truck is taking bikes from
        :type station: Station
        :param bikes: The number of bikes to be added to this truck
        :type bikes: int
        :param broken: True if the bikes being moved are broken, False if they are normal
        :type broken: bool

        """
        self.fill = self.fill + bikes
        if broken:
            self.broken_bikes = self.broken_bikes + bikes
        station.remove_bikes(bikes)

    def remove_bikes(self, station, bikes, broken):
        # type: (Station, int, bool) -> None
        """Removes bikes to this truck and adds bikes to the station this truck adding to

        :param station: The station is truck adding bikes to
        :type station: Station
        :param bikes: The number of bikes to be removed from this truck
        :type bikes: int
        :param broken: True if the bikes being moved are broken, False if they are normal
        :type broken: bool

        """
        self.fill = self.fill - bikes
        if broken:
            self.broken_bikes = self.broken_bikes - bikes
        station.add_bikes(bikes)

    def move(self, task, smap):
        # type: (Task, StationMap) -> None
        """ Makes this truck perform a task

        :param task: The task this truck is performing
        :type task: Task
        :param smap: The StationMap this truck is on
        :type smap: StationMap

        """
        self.improvement = self.improvement + task.improvement(self, smap)
        time = task.time(self, smap)
        self.time = self.time + timedelta(seconds=time)
        self.location = task.station
        self.visited.append(task.station)

        if task.pickup:
            self.add_bikes(task.station, task.bikes, task.broken)
        else:
            self.remove_bikes(task.station, task.bikes, task.broken)

        self.route.append(task)

    def take_break(self):
        """Lets this truck take its' next break"""
        next_break = self.breaks.pop(0)
        self.route.append(next_break)
        self.time = self.time + next_break.duration

    def greedy_move(self, smap, needs_exit=True):
        # type: (StationMap, bool) -> Task or None
        """Greedily finds the task with the highest (change in disappointed customers)/(time to perform task) ratio for
        this truck

        :param smap: The StationMap this truck is on
        :type smap: StationMap
        :param needs_exit: Specifies whether time must be allotted for the truck to return to its destination. Returns
            True if it needs to return, and False if it doesn't. Defaults to True.
        :type needs_exit: bool

        :returns: The task with the highest score. Returns None if there are no feasible tasks
        :rtype: Task, None
        """
        max_ratio = -1
        greedy_task = None
        # Return none if no time remaining
        if self.time >= self.end:
            return greedy_task

        # Check truck for extreme states
        pos = True
        neg = True
        if self.fill - self.broken_bikes == 0:
            neg = False
        if self.capacity == self.fill:
            pos = False

        # Find best task
        for i in set(smap.stations.values()).difference(set(self.visited)):
            to_loc = smap.paths[self.location.id][i.id] + i.rate
            arrival_time = self.time + timedelta(seconds=to_loc)

            # Check if station is forbidden upon arrival
            if i.id in smap.forbidden and smap.forbidden[i.id][0] <= arrival_time <= smap.forbidden[i.id][1]:
                pass
            else:
                o = smap.find_optimal_number_of_bikes(arrival_time, i)
                c = i.bikes
                if o < c and pos:
                    move = min(self.capacity - self.fill, c - o)
                    t = Task(i, move, True)

                elif o > c and neg:
                    move = min(self.fill - self.broken_bikes, o - c, i.docks)
                    t = Task(i, move, False)

                else:
                    t = None

                if t is not None:
                    if not t.feasible(self, smap, needs_exit):
                        t = t.fix(self, smap, needs_exit)

                    if t.bikes > 0:  # check if move is feasible
                        to_pick_up = self.rate * t.bikes
                        task_length = to_loc + to_pick_up
                        customers = t.improvement(self, smap)
                        r = customers / task_length
                        if max_ratio < r:
                            greedy_task = t
                            max_ratio = r

        return greedy_task

    def greedy_random_move(self, smap, k=5, needs_exit=True):
        # type: (StationMap, int, bool) -> Task or None
        """Select a task from the top k tasks with the highest (change in disappointed customers)/(time to perform task)
         ratio for this truck, where each task has a probability in proportion to 2 to the power of its score.

        :param smap: The StationMap this truck is on
        :type smap: StationMap
        :param k: Specifies how many tasks should be on the top k list
        :type k: int
        :param needs_exit: Specifies whether time must be allotted for the truck to return to its destination. Returns
            True if it needs to return, and False if it doesn't. Defaults to True.
        :type needs_exit: bool

        :returns: The task with the highest score. Returns None if there are no feasible tasks
        :rtype: Task, None
        """
        k_set = []
        ratio_set = []
        weight_set = []
        grasp_task = None
        # Return none if no time remaining
        if self.time >= self.end:
            return grasp_task

        # Check truck for extreme states
        pos = True
        neg = True
        if self.fill - self.broken_bikes == 0:
            neg = False
        if self.capacity == self.fill:
            pos = False

        # Find top k tasks
        for i in set(smap.stations.values()).difference(set(self.visited)):
            to_loc = smap.paths[self.location.id][i.id] + i.rate
            arrival_time = self.time + timedelta(seconds=to_loc)

            # Check if station is forbidden upon arrival
            if i.id in smap.forbidden and smap.forbidden[i.id][0] <= arrival_time <= smap.forbidden[i.id][1]:
                pass
            else:
                o = smap.find_optimal_number_of_bikes(arrival_time, i)
                c = i.bikes
                if o < c and pos:
                    move = min(self.capacity - self.fill, c - o)
                    t = Task(i, move, True)

                elif o > c and neg:
                    move = min(self.fill - self.broken_bikes, o - c, i.docks)
                    t = Task(i, move, False)

                else:
                    t = None

                if t is not None:
                    if not t.feasible(self, smap, needs_exit):
                        t = t.fix(self, smap, needs_exit)

                    if t.bikes > 0:  # check if move is feasible
                        to_pick_up = self.rate * t.bikes
                        task_length = to_loc + to_pick_up
                        customers = t.improvement(self, smap)
                        r = customers / task_length

                        if len(k_set) == 0:
                            k_set.append(t)
                            ratio_set.append(r)
                            weight_set.append(2 ** r)

                        else:
                            lo = 0
                            hi = len(ratio_set)
                            while lo < hi:
                                mid = (lo + hi) // 2
                                if r > ratio_set[mid]:
                                    hi = mid
                                else:
                                    lo = mid + 1
                            k_set.insert(lo, t)
                            ratio_set.insert(lo, r)
                            weight_set.insert(lo, 2 ** r)
                            k_set = k_set[0:k]
                            ratio_set = ratio_set[0:k]
                            weight_set = weight_set[0:k]

        # Pick a weighted-random task
        if len(k_set) > 0:
            totals = []
            running_total = 0

            w = len(k_set)
            for r in xrange(0, w):
                running_total += weight_set[r]
                totals.append(running_total)

            rand = random.random() * running_total
            grasp_task = k_set[bisect_right(totals, rand)]

        return grasp_task

    def __str__(self):
        return 'Truck #', self.id, ' with capacity ', self.capacity, ', and ', self.fill, ' bikes'


class StationMap:
    """Specifies a map of rebalencing stations

    :ivar stations: A dictionary that maps the ID of a station in this map to its Station object
    :vartype stations: Dict[int, Station]
    :ivar original: A deepcopy of stations when this StationMap was initialized
    :vartype original: Dict[int,Station]
    :ivar forbidden: A dictionary that maps a Station ID to a tuple of the start/end datetime for when this station
        is forbidden
    :vartype forbidden: Dict[int, Tuple[datetime, datetime]"""
    url = 'https://feeds.citibikenyc.com/stations/stations.json'  # URL of the Citi Bike JSON feed
    absolute_url = "./Algo/Greedy3/"  # Absolute URL of this source directory
#    "/home/ubuntu/citibikeapp/citibikeapp/Algo/Greedy3/"

    def __init__(self):
        # Declare Stations
        x = {}
        response = urlopen(self.url)
        data = loads(response.read())
        bean_list = data['stationBeanList']

        for i in xrange(0, len(bean_list)):
            x[bean_list[i]['id']] = Station(i, bean_list[i]['id'],
                                            bean_list[i]['availableBikes'], bean_list[i]['availableDocks'])
        self.stations = x
        self.original = copy.deepcopy(x)

        # Declare Forbidden Stations
        self.forbidden = {}

        # Declare Cost Curves
        with open(self.absolute_url + 'Data/PickledCurves.txt', 'r') as input:
            self.curves = pickle.load(input)

        # Declare Map
        f = open(self.absolute_url + 'Data/SecondsPaths.txt', 'r')
        self.paths = pickle.load(f)
        f.close()

    def clean(self):
        f = open(self.absolute_url + 'Data/Island-Jersey Stations.txt', 'r')
        island_jersey_station = pickle.load(f)
        f.close()

        response = urlopen(self.url)
        data = loads(response.read())
        a = data['stationBeanList']

        for i in list(self.stations):
            if i in island_jersey_station:
                del self.stations[i]
            elif a[self.stations[i].index]['statusValue'] == 'Not In Service':
                del self.stations[i]
            elif i not in self.curves[0]:  # Stations w/ no cost curve
                del self.stations[i]
            elif len(self.curves[0][i]) < self.stations[i].bikes + self.stations[i].docks + 1:  # Incorrect cost curve
                del self.stations[i]
            elif i == 3466 or i == 3469 or i == 3472:  # TEMPORARILY REMOVE UNTIL GRAPH IS UPDATED
                del self.stations[i]

        self.original = copy.deepcopy(self.stations)

    def restore(self):
        """Reverts this StationMap back to its original state"""
        self.stations = copy.deepcopy(self.original)

    def create_checkpoint(self):
        """Makes a checkpoint at this StationMap's current state. If restore is called after this, the StationMap will
        revert to the state where this checkpoint was made"""
        self.original = copy.deepcopy(self.stations)

    def update_json(self):
        """Updates the StationMap information from the Citi Bike json feed, then sets its checkpoint at the updated
        state."""
        response = urlopen(self.url)
        data = loads(response.read())
        bean_list = data['stationBeanList']

        for i in self.stations.values():
            i.bikes = bean_list[i.index]['availableBikes']
            i.docks = bean_list[i.index]['availableDocks']

        self.create_checkpoint()

    def add_forbidden_station(self, station, start, end):
        # type: (Station, datetime, datetime) -> None
        """Makes a station in this list forbidden for a period of time

        :param station: The station that should be forbidden
        :type station: Station
        :param start: The starting time of when this station is forbidden
        :type start: datetime
        :param end: The ending time of when this station is forbidden
        :type end: datetime
        """
        self.forbidden[station.id] = (start, end)

    def compute_disappointed_customers(self, time, station, bikes):
        # type: (datetime, Station, int) -> float
        """Finds the number of disappointed customers expected at a certain station with a specified number of bikes

        :param time: The time to check expected number of disappointed customers
        :type time: timedelta
        :param station: The station that customers are being disappointed by
        :type station: Station
        :param bikes: The number of bikes at this station to examine the effects of
        :type bikes: int

        :returns: The number of disappointed customers caused by having this many bikes at this station at this time.
        :rtype: float"""
        if time.minute < 30:
            ctime = time.hour * 2 + 1
        else:
            ctime = time.hour * 2 + 2

        if ctime == 48:
            ctime = 0

        return self.curves[ctime][station.id][bikes]

    def find_optimal_number_of_bikes(self, time, station):
        # type: (datetime, Station) -> int
        """Finds the optimal number of bikes that should be at a certain station at a specified time

        :param time: The time to check for the number of optimal bikes
        :type time: timedelta
        :param station: The station to check for the number of optimal bikes
        :type station: Station

        :returns: The number of bikes at this station that will minimize the number of disappointed customers
        :rtype: int"""
        if time.minute < 30:
            ctime = time.hour * 2 + 1
        else:
            ctime = time.hour * 2 + 2

        if ctime == 48:
            ctime = 0

        return self.curves[ctime][station.id].index(min(self.curves[ctime][station.id]))

    def opt_task(self, truck, station=None):
        # type: (Truck, Station) -> Task
        """Finds the optimal task to perform at this station

        :param truck: The truck that will perform the returned task
        :type truck: Truck
        :param station: The station to perform the returned task at
        :type station: Station

        :returns: The task at this station that will minimize the number of disappointed customers
        :rtype: Task"""
        bikes = 0
        pickup = True

        if station is None:
            station = self.stations[72]
        elif station.id != self.stations[station.id]:
            station = self.stations[station.id]

        current = station.bikes
        optimal = self.find_optimal_number_of_bikes(truck.time, station)

        # Check how many bikes should be moved
        if truck.fill - truck.broken_bikes > 0 and optimal > current:
            bikes = min(optimal - current, truck.fill - truck.broken_bikes, station.docks)
            pickup = False

        elif truck.fill < truck.capacity and current > optimal:
            bikes = min(current - optimal, truck.capacity - truck.fill)
            pickup = True

        return Task(station, bikes, pickup)
