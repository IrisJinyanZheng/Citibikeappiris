import json
import urllib
import copy
import pickle
import math

urlfix = "/var/www/html/flaskapp/Algo/Greedy2/"

class Station:
    def __init__(self, index=-1, iden=-1, bikes=0, docks=0, rate=0.07):
        self.index = index
        self.id = iden
        self.bikes = bikes
        self.docks = docks
        self.rate = rate

    def addBikes(self, bikes):
        self.bikes = self.bikes + bikes
        self.docks = self.docks - bikes

    def removeBikes(self, bikes):
        self.bikes = self.bikes - bikes
        self.docks = self.docks + bikes

    @property
    def __str__(self):
        return "Station " + str(self.id) + " with " + str(self.bikes) + " bikes and " + str(self.docks) + " docks"


class Task:
    def __init__(self, station=Station(), bikes=0, toTruck=True):
        self.station = station
        self.bikes = bikes
        self.toTruck = toTruck

    def time(self, truck, smap):
        toLoc = float(smap.paths[truck.location.id][self.station.id]) / 1800
        toPickUp = truck.rate * abs(self.bikes) + self.station.rate

        return toLoc + toPickUp

    def feasible(self, truck, smap):
        # Implement after testing
        # if self.toTruck = True
        # if bikes > self.station.bikes or bikes > truck.capacity - truck.fill: return False
        # if self.toTruck = False
        # if bikes > truck.bikes or bikes > self.station.docks: return False

        time = self.time(truck, smap)
        toExit = float(smap.paths[self.station.id][truck.destination.id]) / 1800
        if time + toExit > truck.end - truck.time:
            return False
        else:
            return True

    def improvement(self, truck, smap):

        time = truck.time + self.time(truck, smap)
        original = smap.stations[self.station.id].bikes

        if self.toTruck:
            new = original - self.bikes
        else:
            new = original + self.bikes
        oricost = smap.customers(time, self.station, original)
        newcost = smap.customers(time, self.station, new)
        change = oricost - newcost

        return change

    def __str__(self):
        if self.toTruck:
            s = 'from'
        else:
            s = 'to'
        return 'Move ' + str(self.bikes) + ' bikes ' + s + ' station ' + str(self.station.id)


class Truck:
    def __init__(self, iden=0, capacity=42, fill=0, rate=0.017, origin=356,
                 location=356, destination=356, start=0, end=12):
        self.id = iden
        self.capacity = capacity
        self.fill = fill
        self.rate = 0.017
        self.origin = origin
        self.location = location
        self.destination = destination
        self.route = []
        self.start = start
        self.time = copy.copy(start)
        self.end = end
        self.improvement = 0

        self.visited = []

    def addBikes(self, station, bikes):
        self.fill = self.fill + bikes
        station.removeBikes(bikes)

    def removeBikes(self, station, bikes):
        self.fill = self.fill - bikes
        station.addBikes(bikes)

    def move(self, task, smap):
        self.improvement = self.improvement + task.improvement(self, smap)
        time = task.time(self, smap)
        self.time = self.time + time
        self.location = task.station
        self.visited.append(task.station)

        if task.toTruck:
            self.addBikes(task.station, task.bikes)
        else:
            self.removeBikes(task.station, task.bikes)

        self.route.append(task)

    def GreedyMove(self, smap):
        p = []
        b = []
        n = []
        maxRatio = -1
        greedyTask = None
        for i in smap.stations.values():
            # Check if truck is in extreme state
            if i not in self.visited:
                pos = True
                neg = True
                if self.fill == 0:
                    neg = False
                elif self.capacity == self.fill:
                    pos = False

                toLoc = float(smap.paths[self.location.id][i.id]) / 1800 + i.rate
                o = smap.optBikes(self.time + toLoc, i)
                c = i.bikes
                if o < c and pos:
                    move = min(self.capacity - self.fill, c - o, c)
                    t = Task(i, move, True)

                    if t.feasible(self, smap):  # check if move is feasible
                        toPickUp = self.rate * t.bikes
                        taskLength = toLoc + toPickUp
                        customers = t.improvement(self, smap)
                        r = customers / taskLength

                        if maxRatio < r:
                            greedyTask = t
                            maxRatio = r

                elif o > c and neg:
                    move = min(self.fill, o - c, i.docks)
                    t = Task(i, move, False)

                    if t.feasible(self, smap):  # check if move is feasible
                        toPickUp = self.rate * t.bikes
                        taskLength = toLoc + toPickUp
                        customers = t.improvement(self, smap)
                        r = customers / taskLength
                        if maxRatio < r:
                            greedyTask = t
                            maxRatio = r

        return greedyTask


class StationMap:
    url = 'https://feeds.citibikenyc.com/stations/stations.json'


    def __init__(self):
        # Declare Stations
        x = {}
        response = urllib.urlopen(self.url)
        data = json.loads(response.read())
        BeanList = data['stationBeanList']

        for i in xrange(0, len(BeanList)):
            x[BeanList[i]['id']] = Station(i, BeanList[i]['id'],
                                           BeanList[i]['availableBikes'], BeanList[i]['availableDocks'])
        self.stations = x
        self.original = copy.deepcopy(x)

        # Declare Cost Curves
        allcosts = {}
        for i in xrange(48):
            allcosts[i] = eval(open(urlfix+'Data/CostCurves/PainTime_3_%d.txt' % i).read())
        self.curves = allcosts

        # Declare Map
        f = open(urlfix+'Data/Paths.txt', 'r')
        self.paths = pickle.load(f)
        f.close()

    def clean(self):
        f = open(urlfix+'Data/Island-Jersey Stations.txt', 'r')
        IJ = pickle.load(f)
        f.close()

        response = urllib.urlopen(self.url)
        data = json.loads(response.read())
        a = data['stationBeanList']
        for i in list(self.stations.keys()):
            if i in IJ:  # Island/NJ Stations
                del self.stations[i]
            elif a[self.stations[i].index]['statusValue'] == 'Not In Service':  # Not in Service Stations
                del self.stations[i]
            elif i not in self.curves[0]:  # Stations w/ no cost curve
                del self.stations[i]
            elif len(self.curves[0][i]) != a[self.stations[i].index][
                'totalDocks'] + 1:  # Station w/ incorrect cost curve
                del self.stations[i]

                ###TEMPORARILY REMOVE UNTIL GRPAH IS UPDATED###
        # 3466, 3469, 3472
        del self.stations[3466]
        del self.stations[3469]

        self.original = copy.deepcopy(self.stations)

    def restore(self):
        self.stations = copy.deepcopy(self.original)

    def updateJSON(self):
        response = urllib.urlopen(self.url)
        data = json.loads(response.read())
        BeanList = data['stationBeanList']

        for i in self.stations.values():
            i.bikes = BeanList[i.index]['availableBikes']
            i.docks = BeanList[i.index]['availableDocks']

        self.original = copy.deepcopy(self.stations)

    def optBikes(self, time, station):
        ctime = int(math.ceil(time))
        return self.curves[ctime][station.id].index(min(self.curves[ctime][station.id]))

    def customers(self, time, station, bikes):
        ctime = int(math.ceil(time))
        return self.curves[ctime][station.id][bikes]



