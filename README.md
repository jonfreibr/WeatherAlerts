# WeatherAlerts
## Monitor Weather Alerts and forecast for predefined locations

* Copyright © Blue Ridge Medical Center, 2025. All Rights Reserved
* License: GNU GPL Version 3

### Desktop widget that monitors the National Weather Service REST API for weather bulletins, alerts and warnings. Pulls daily and hourly forecasts on demand.

### Currently monitors Nelson County, Amherst County, and Appomattox County in Virginia by default. Easily customized to monitor your locations of interest.

* The National Weather Service is polled every five (5) minutes for each defined location.
* Buttons turn red when alerts are present
* Buttons show the number of alerts per location.
* Each location's alerts open to their own window.
* All windows remember their size and location.
* Version 2.0 simplified adding and removing locations
* Version 2.4(a) will support unlimited (except by screen real estate) locations in a 10 column grid.
* Version 3.0 incorporated daily and hourly forecasts on demand as well as polled alerts.

The National Weather Service API uses Zone Codes to serve alerts, and decimal lattidute/longitude points to deliver forecasts. 
To get everything in one widget, the configuration files require both the lattidude/longitude and the zone code.
The API does not seem to be picky about the number of decimal points in your lat/long, and a direct copy/paste from Google
maps (12 digits after the decimal point) works fine. I have also used as few as 4 digits after the decimal point with success.

Once you display an alert/forecast window, this data is static until you click the location button again. Switching between the 
alert, daily forecast, and hourly forecast does not refresh the data.

### Data sources

Lattitude and longitude are easily obtained from Google Maps or many other sources.

Zones are maintained at https://api.weather.gov/zones

zoneparse.py will convert the served JSON file to a CSV file.

Zones.xlsx updates from zones.csv

### Customization

Update the dictionary in walerts.cfg to include the locations you want to monitor. They will be displayed in the order entered.

The configuration is in a JSON file and takes the format "Name":"Lattitude, Longitude, Zone Code"

An example file:

----- start of file -----
{"Nelson County, VA":"37.7066, -78.9340, VAC125",
"Amherst County, VA":"37.5655, -79.0637, VAC009",
"Appomattox County, VA":"37.3673, -78.8267, VAC011"}
----- end of file -----

## Questions, Comments, Bug Reports

jfreivald@brmedical.com
