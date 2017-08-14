from StationMap import Task, Station, Truck, StationMap

def Routes(trucks = [], smap = StationMap()):
    incompleted = trucks
    completed = []
    while len(set(incompleted)-set(completed)) > 0:
        for i in incompleted:
            t = i.GreedyMove(smap)
            if t is not None:
                i.move(t, smap)
            else:
                completed.append(i)
