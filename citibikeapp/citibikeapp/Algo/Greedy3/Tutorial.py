import Algorithms
from StationMap import StationMap, Truck, Break
from datetime import datetime, timedelta

'''Declare, clean, and update StationMap Object example'''
smap = StationMap()
smap.clean()
smap.update_json()


'''Add a set of forbidden stations to StationMap example'''
# Change forbidden stations to declared dictionary:
forbidden_stations = {}
# Forbid station to ID 247 from 6:30AM today to 7:00AM today
forbidden_stations[247] = (datetime.today().replace(hour=6, minute=30, second=0, microsecond=0),
                           datetime.today().replace(hour=7, minute=0, second=0, microsecond=0))
# Forbid station to ID 3389 from 12:000PM today to 8:00PM today
forbidden_stations[443] = (datetime.today().replace(hour=12, minute=0, second=0, microsecond=0),
                           datetime.today().replace(hour=20, minute=0, second=0, microsecond=0))
smap.forbidden = forbidden_stations

# Add a single forbidden station to existing dictionary:
# Forbid station to ID 3389 from 1:30PM today to 2:30PM today
station = smap.stations[3389]
start = datetime.today().replace(hour=13, minute=30, second=0, microsecond=0)
end = datetime.today().replace(hour=14, minute=30, second=0, microsecond=0)
# Add forbidden station to map
smap.add_forbidden_station(station, start, end)


'''Declare an list of trucks example'''
trucks = []
for i in xrange(4):
    start_time = datetime.today().replace(second=0, microsecond=0)  # Create datetime obj at current time for beginning of truck's shift
    finish_time = start_time + timedelta(hours=6)  # Create datetime obj 6 hours from now for end of truck's shift
    start_location = smap.stations[356]  # Get Station w/ ID 356 for truck's starting location
    end_location = smap.stations[72]  # Get Station w/ ID 72 for truck's ending location
    capacity = 48  # Set capacity of the truck to 48 bikes (defaults to 42)
    total_bikes = 5  # Set the total number of bikes, including broken bikes, to 5 (defaults to 0)
    broken_bikes = 2  # Set total number of broken bikes to 2 (defaults to 0)
    # If the number of broken bikes exceeds the number of total bikes, the number of total bikes is set to the number of broken bikes

    # Create list of breaks
    breaks = []
    breaks.append(Break(start_time+timedelta(hours=2), 30))  # Add a 30 minute break, 2 hours from the start time
    breaks.append(Break(start_time+timedelta(hours=4), 60))  # Add a 60 minute break, 4 hours from start time

    trucks.append(
        # Create truck object with parameters created above, with IDs of i in range 0 to 4
        Truck(iden=i, capacity=capacity, fill=total_bikes, broken_bikes=broken_bikes, breaks=breaks,
              origin=start_location, location=start_location, destination=end_location,
              start=start_time, end=finish_time)
    )


'''Call Algorithms Example'''
# Create needs_exit list for trucks list:
needs_exit = dict.fromkeys([truck.id for truck in trucks])
needs_exit[0] = True  # Truck w/ ID 1 must return to its destination by its shift end time
needs_exit[1] = False  # Truck w/ ID 2 does not have to return to its destination by its shift end time
# Trucks w/ ID 3,4 will default to True, so they must return to their destination by the shift end times

# Calls Greedy-Best algorithm where trucks with needs_exit dict above
greedy_best_solution = Algorithms.greedy_best(trucks, smap, needs_exit)
# Calls Greedy-Iterative algorithm with needs_exit dict above
greedy_iterative_solution = Algorithms.greedy_iterative(trucks, smap, needs_exit)

# Runs GRASP-Finish algorithm for 50 iterations, with a restricted neighbor set of the top 5 best solutions, and
# where all trucks have to make it back to their destination by the shift end time
needs_exit = dict.fromkeys([truck.id for truck in trucks], True)
grasp_finish_solution = Algorithms.grasp_finish(trucks, smap, 50, 5, needs_exit)
# Runs GRASP-Iterative algorithm for 100 iterations, with a restricted neighbor set of the top 3 best solutions, and
# where trucks do not have to make it back to their destination by the shift end time
needs_exit = dict.fromkeys([truck.id for truck in trucks], False)
grasp_iterative_solution = Algorithms.grasp_iterative(trucks, smap, 100, 3, needs_exit)
# Runs GRASP-Best algorithm for 2 minutes (120 seconds), with a restricted neighbor set of the top 4 best solutions, and
# where trucks have to make it back to their destination by the shift end time
needs_exit = dict.fromkeys([truck.id for truck in trucks])
grasp_best_solution = Algorithms.grasp_time_best(trucks, smap, 120, 4, True)

# Gets a dictionary of all the routes for all the trucks for greedy_best_solution
routes = greedy_best_solution[0]
# Gets the float object of the total decrease in disappointed customers caused by all trucks for greedy_best_solution
customers = greedy_best_solution[1]


