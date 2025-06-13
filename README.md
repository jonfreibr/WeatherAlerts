# WeatherAlerts
## Monitor Weather Alerts for predefined locations

### Desktop widget that monitors the National Weather Service REST API for weather bulletins, alerts and warnings.

### Currently monitors City of Charlottesville, Nelson County, Amherst County, City of Lynchburg, and Appomattox County in Virginia.

* Buttons turn red when alerts are present
* Buttons show the number of alerts per location.
* Each location's alerts open to their own window.
* All windows remember their size and location.
* Version 2.0 simplified adding and removing locations

### Data

Zones are maintained at https://api.weather.gov/zones

zoneparse.py will convert the JSON file to a CSV file.

Zones.xlsx updates from zones.csv

### Customization

In the Class MainWIndow, create your locations, add them to the layout with their .get_button() method, and then add their .update() method to the do_update() subroutine.

