import cPickle as pickle
        #from Algo.Greedy2 import Main, StationMap
from StationMap import Task, Station, Truck, StationMap
from Main import Routes
x = StationMap()
with open('/var/www/html/flaskapp/Algo/Greedy2/Data/StationMap.txt', 'w') as output:
    pickle.dump(x, output, pickle.HIGHEST_PROTOCOL)