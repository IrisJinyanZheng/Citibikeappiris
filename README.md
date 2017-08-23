# Citibikeapp
Web app and iOS app

The Web app is in the citibike folder, the iOS app is in the Citibike-app-ios folder.

Web App

***When making changes, try not to change the name of the two folders citibikeapp and citibikeapp/citibikeapp. Otherwise a lot of the changes need to be made to accomodate the change of the file paths due to the folder name changes. 

Inside the first level citibike folder: 

citibike.wsgi  - contains configuration for the apache server. 

000-default.conf - configuration for the apache server. It is in /etc/apache2/sites-enabled/ in AWS. Note that uploading this file might fail and it has to be edited using nano from terminal. 

Key1.pem  - the RSA key to access the AWS. 

