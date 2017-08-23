Welcome to the Citibikeapp wiki!

# Citibikeapp
Web app and iOS app

The Web app is in the citibike folder, the iOS app is in the Citibike-app-ios folder.

# Web App

***When making changes, try not to change the name of the two folders citibikeapp and citibikeapp/citibikeapp. Otherwise a lot of the changes need to be made to accomodate the change of the file paths due to the folder name changes. 

## Inside the first citibikeapp folder: 

citibike.wsgi  - contains configuration for the apache server. 

000-default.conf - configuration for the apache server. It is in /etc/apache2/sites-enabled/ in AWS. Note that uploading this file might fail and it has to be edited using nano from terminal. 

Key1.pem  - the RSA key to access the AWS. 


## Inside the second citibikeapp folder:

### Database

citibike_change.db : the database. A specification of the database can be found here http://ec2-54-196-202-203.compute-1.amazonaws.com/static/documentation/doc_db.html.

### config files
setup.py - the file to setup the flask app

__init_\_.py	- initialize and configure flask app, contain login features and error handler, import modules

### module files
addEntryPy.py - Add Forbidden Station, Add Vehicle,  Add Driver, Add Task Type

assignTaskPy.py	- Assign task

breakPy.py - schedule and update defaut breaks, delay breaks  
  /breaks.json

dashboardPy.py	- dashboard

globalfunc.py - some common functions used, for the web app

globalfunc2.py - some common functions used, for the cron job scripts (updatepriority.py and greedyalgp.py)

greedyPy.py    - old version of greedyalgo, not used

iosresponsePy.py - ios actions: update vehcile info, accept/complete/request reject task, arrive, (self assign breaks are in this file but commented out)  
     routes are not login required to access  
        /getVehicles.json  
        /vID/<vID\>  
        /getTasks.json  
        /getTaskTypes.json  
        /getStations.json  
        /reasonCode.json  

manageTablePy.py - Delete Entry, display manage tables (except breaks and shifts), Order tasks, Update entries, Reject Open Tasks, Update Open Tasks, Assign Closed Tasks  
         /manageTabelJson/<table\>.json  
         /searchByCol/<table\>/<col\>=<id\>.json  

mapPy.py - generate geojson for map pages  
        /stationgeojson  
        /vehiclegeojson  
        /taskgeojson  
        
searchTaskPy.py	- search task

shiftPy.py	- iOS: start/end driver/vehicle shift; Web: approve ending shift  
        /getShifts.json


### Cron scripts:

greedyalgo.py	- run greedy algo and update database

updatepriority.py - find deadline violating tasks and increase their priority
