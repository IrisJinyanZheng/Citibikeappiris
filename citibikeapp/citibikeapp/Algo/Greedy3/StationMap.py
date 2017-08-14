from json import loads
from urllib import urlopen
import copy
import cPickle as pickle
from bisect import bisect_right
import random
from datetime import datetime, timedelta

prefix_url = "./Algo/Greedy3/"
class Station:
    def __init__(self, index=-1, iden=-1, bikes=0, docks=0, rate=120):
        self.index = index
        self.id = iden
        self.bikes = bikes
        self.docks = docks
        self.rate = rate

    def add_bikes(self, bikes):
        # type: (int) -> None
        self.bikes = self.bikes + bikes
        self.docks = self.docks - bikes

    def remove_bikes(self, bikes):
        # type: (int) -> None
        self.bikes = self.bikes - bikes
        self.docks = self.docks + bikes

    def __str__(self):
        return "Station " + str(self.id) + " with " + str(self.bikes) + " bikes and " + str(self.docks) + " docks"


class Break:
    def __init__(self, start_time, duration):
        # type: (datetime, int) -> Break
        self.start_time = start_time
        self.duration = timedelta(minutes=duration)
        self.end_time = self.start_time + self.duration


class Task:
    def __init__(self, station, bikes=0, to_truck=True, broken=False):
        # type: (Station, int, bool, bool) -> Task
        self.station = station
        self.bikes = bikes
        self.to_truck = to_truck
        self.broken = broken

    def time(self, truck, smap):
        # type: (Truck, StationMap) -> int
        to_loc = smap.paths[truck.location.id][self.station.id] + self.station.rate
        to_pick_up = truck.rate * self.bikes

        return to_loc + to_pick_up

    def feasible(self, truck, smap, needs_exit=True):
        # type: (Truck, StationMap, bool) -> bool
        if self.to_truck:
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
        # type: (Truck, StationMap, bool) -> Task
        new_bikes = self.bikes

        if self.to_truck:
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

        return Task(self.station, new_bikes, self.to_truck)

    def improvement(self, truck, smap):
        # type: (Truck, StationMap) -> float
        # Returns 0 improvement if dropping off broken bikes
        if self.broken and not self.to_truck:
            return 0

        time = truck.time + timedelta(seconds=self.time(truck, smap))
        original = smap.stations[self.station.id].bikes

        if self.to_truck:
            new = original - self.bikes
        else:
            new = original + self.bikes

        original_cost = smap.customers(time, self.station, original)
        new_cost = smap.customers(time, self.station, new)
        cost_change = original_cost - new_cost

        return cost_change

    def __str__(self):
        if self.to_truck:
            s = 'from'
        else:
            s = 'to'
        return 'Move ' + str(self.bikes) + ' bikes ' + s + ' station ' + str(self.station.id)


class Truck:
    def __init__(self, iden=-1, capacity=42, fill=0, broken_bikes=0, breaks=None, rate=30, origin=Station(),
                 location=Station(), destination=Station(), start=datetime(2017, 1, 1), end=datetime(2017, 1, 1, 6)):
        # type: (int, int, int, int, list, int, Station, Station, Station, datetime, datetime) -> Truck
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
        self.fill = self.fill + bikes
        if broken:
            self.broken_bikes = self.broken_bikes + bikes
        station.remove_bikes(bikes)

    def remove_bikes(self, station, bikes, broken):
        # type: (Station, int, bool) -> None
        self.fill = self.fill - bikes
        if broken:
            self.broken_bikes = self.broken_bikes - bikes
        station.add_bikes(bikes)

    def move(self, task, smap):
        # type: (Task, StationMap) -> None
        self.improvement = self.improvement + task.improvement(self, smap)
        time = task.time(self, smap)
        self.time = self.time + timedelta(seconds=time)
        self.location = task.station
        self.visited.append(task.station)

        if task.to_truck:
            self.add_bikes(task.station, task.bikes, task.broken)
        else:
            self.remove_bikes(task.station, task.bikes, task.broken)

        self.route.append(task)

    def take_break(self):
        next_break = self.breaks.pop(0)
        self.route.append(next_break)
        self.time = self.time + next_break.duration

    def greedy_move(self, smap, needs_exit=True):
        # type: (StationMap, bool) -> Task or None
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
                o = smap.opt_bikes(arrival_time, i)
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
                o = smap.opt_bikes(arrival_time, i)
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
    url = 'https://feeds.citibikenyc.com/stations/stations.json'

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
        with open(prefix_url+'Data/PickledCurves.txt', 'r') as input:
            self.curves = pickle.load(input)

        # Declare Map
        f = open(prefix_url+'Data/SecondsPaths.txt', 'r')
        self.paths = pickle.load(f)
        f.close()

    def clean(self):
        f = open(prefix_url+'Data/Island-Jersey Stations.txt', 'r')
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
        self.stations = copy.deepcopy(self.original)

    def checkpoint(self):
        self.original = copy.deepcopy(self.stations)

    def update_json(self):
        response = urlopen(self.url)
        data = loads(response.read())
        bean_list = data['stationBeanList']

        for i in self.stations.values():
            i.bikes = bean_list[i.index]['availableBikes']
            i.docks = bean_list[i.index]['availableDocks']

        self.original = copy.deepcopy(self.stations)

    def add_forbidden_station(self, station, start, end):
        # type: (Station, datetime, datetime) -> None
        self.forbidden[station.id] = (start, end)

    def customers(self, time, station, bikes):
        # type: (datetime, Station, int) -> float
        if time.minute < 30:
            ctime = time.hour * 2 + 1
        else:
            ctime = time.hour * 2 + 2

        if ctime == 48:
            ctime = 0

        return self.curves[ctime][station.id][bikes]

    def opt_bikes(self, time, station):
        # type: (datetime, Station) -> int
        if time.minute < 30:
            ctime = time.hour * 2 + 1
        else:
            ctime = time.hour * 2 + 2

        if ctime == 48:
            ctime = 0

        return self.curves[ctime][station.id].index(min(self.curves[ctime][station.id]))

    def opt_task(self, truck=Truck(), station=None):
        # type: (Truck, Station) -> Task
        bikes = 0
        to_truck = True

        if station is None:
            station = self.stations[72]
        elif station.id != self.stations[station.id]:
            station = self.stations[station.id]

        current = station.bikes
        optimal = self.opt_bikes(truck.time, station)

        # Check how many bikes should be moved
        if truck.fill - truck.broken_bikes > 0 and optimal > current:
            bikes = min(optimal - current, truck.fill - truck.broken_bikes, station.docks)
            to_truck = False

        elif truck.fill < truck.capacity and current > optimal:
            bikes = min(current - optimal, truck.capacity - truck.fill)
            to_truck = True

        return Task(station, bikes, to_truck)
