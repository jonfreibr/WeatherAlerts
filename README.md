# WeatherAlerts
## Monitor Weather Alerts for predefined locations

### Desktop widget that monitors the National Weather Service REST API for weather bulletins, alerts and warnings.

### Currently monitors City of Charlottesville, Nelson County, Amherst County, City of Lynchburg, and Appomattox County in Virginia by default. Easily customized to monitor your locations of interest.

* Buttons turn red when alerts are present
* Buttons show the number of alerts per location.
* Each location's alerts open to their own window.
* All windows remember their size and location.
* Version 2.0 simplified adding and removing locations
* Version 2.4(a) will support unlimited (except by screen real estate) locations in a 10 column grid.

### Data

Zones are maintained at https://api.weather.gov/zones

zoneparse.py will convert the JSON file to a CSV file.

Zones.xlsx updates from zones.csv

### Customization

Update the dictionary in walerts.json to include the locations you want to monitor. They will be displayed in the order entered.

