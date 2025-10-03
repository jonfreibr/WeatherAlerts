#!/usr/bin/env python3
"""
Program : Weather Widget
Author  : Jon Freivald <jfreivald@brmedical.com>
        : Copyright © Blue Ridge Medical Center, 2025. All Rights Reserved
        : License: GNU GPL Version 3
Date    : 2025-02-05
Purpose : To poll the National Weather Service for location specific alerts
        : Pull daily/hourly forecast on demand.
        : Version change log at EoF.
"""

import atexit
import json
import os
import psutil
import pytz
import requests
import subprocess
import sys
import time

if sys.platform == "win32":
    import winsound
    import pygetwindow as gw

from datetime import datetime

from PySide6.QtGui import (
    QIcon,
)

from PySide6 import (
    QtCore,
)

from PySide6.QtCore import (
    QTimer,
    QSettings,
    QPoint,
    QSize,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QDialog,
    QTextEdit,
    QApplication,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QDialogButtonBox,
)

progver = '3.02d'

tz_NY = pytz.timezone('America/New_York')
brmc_dark_blue = '#00446a'
brmc_medium_blue = '#73afb6'
brmc_gold = '#ffcf01'
brmc_rust = '#ce7067'
brmc_warm_grey = '#9a8b7d'

# in case we are running under pythonw.exe
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")

#--------------------------------------------------------------------------------------------------------------------------------

# Configuration Information

num_cols = 10
loc_config = 'walerts.cfg' # If you change this, update your update_script!
default_locations = {"Nelson County, VA":"37.7066, -78.9340, VAC125",
                "Amherst County, VA":"37.5655, -79.0637, VAC009",
                "Appomattox County, VA":"37.3673, -78.8267, VAC011"}
update_source = 'H:/_BRMCApps/WeatherAlerts/walerts.py'
update_script = 'H:/_BRMCApps/WeatherAlerts/install.bat'

#--------------------------------------------------------------------------------------------------------------------------------

try:
    with open(loc_config, "r") as file:
        locations = json.load(file)
except:
    locations = default_locations
    
buttons = []


#--------------------------------------------------------------------------------------------------------------------------------

class UpdateDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet(f'background-color: {brmc_medium_blue}')
        self.setWindowTitle("Update Available!")
        layout = QVBoxLayout()
        self.label = QLabel("There is an update available for the Weather Widget application.")
        self.label2 = QLabel("Automatic updates are only available for Windows at this time.")
        self.label3 = QLabel("Other platforms please check with your systems administrator.")
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(self.label)
        layout.addWidget(self.label2)
        layout.addWidget(self.label3)
        layout.addWidget(button_box)
        self.setLayout(layout)

#--------------------------------------------------------------------------------------------------------------------------------

def is_running(script):
    for q in psutil.process_iter():
        if q.name().startswith('python'):
            if len(q.cmdline())>1 and script in q.cmdline()[1] and q.pid !=os.getpid():
                # print(f"'{script}' Process is already running")
                return True
            
    return False

#--------------------------------------------------------------------------------------------------------------------------------

def update_app():
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", update_script, "/min"], stdout=None, stderr=None)

#--------------------------------------------------------------------------------------------------------------------------------

class Timer:
    def __init__(self):
        self.then = time.time()

    def reset(self):
        self.then = time.time()

    def check(self):
        return time.time() - self.then
    
#--------------------------------------------------------------------------------------------------------------------------------

class Location:

    headers = {
        "User-Agent": "BRMC Weather Alert Monitor, jfreivald@brmedical.com"
    }

    def __init__(self, name, lat, lon, zone):
        self.name = name
        self.lat = lat.strip()
        self.lon = lon.strip()
        self.zone = zone.strip()
        self.asterisk = False
        self.response = None
        self.timer = Timer()
        self.button = QPushButton(self.name, flat=False)
        self.button.clicked.connect(self.display)
        self.button_normal()
        self.msgBox = NonBlockingDialog()
        try:
            self.response = requests.get(f'https://api.weather.gov/alerts/active/zone/{self.zone}').json()
            self.response.update({'Retrieved':datetime.now(tz_NY).strftime("%m/%d/%y @ %H:%M")})
            self.point_data = requests.get(f'https://api.weather.gov/points/{self.lat},{self.lon}').json()
            self.forecast_url = self.point_data['properties']['forecast']
            self.hourly_url = self.point_data['properties']['forecastHourly']
        except:
            self.response = {'title': 'API Not Available!', 'updated': 'Not updated!', 'Retrieved': 'Not Retrieved'}
        self.last_response = self.response

        self.update()   # get everything right on startup

    def __str__(self):
        return f"{self.zone} {self.name}"
    
    def name(self):
        return f"{self.name}"
    
    def update(self):
        self.button_grey()
        self.button.setText("Updating")
        self.get_data()
        self.button_normal()
        self.button.setText(f"{self.name}")
        self.alerts = self.num_alerts()
        if self.alerts == 0:
            self.asterisk = False
        if self.alerts > 0:
            self.button_red()
            if self.asterisk:
                self.button.setText(f"* {self.name} ({self.alerts})")
            else:
                self.button.setText(f"{self.name} ({self.alerts})")
        
    def get_data(self):
        if self.timer.check() > 300: # Time (in seconds) minimum between refreshes
            self.timer.reset()
            self.last_response = self.response
            try:
                self.response = requests.get(f'https://api.weather.gov/alerts/active/zone/{self.zone}').json()
                self.response.update({'Retrieved':datetime.now(tz_NY).strftime("%m/%d/%y @ %H:%M")})
                
            except:
                return self.response # the old response
            return self.response # the new response
        else:
            self.button_normal()
            self.button.setText(f"{self.name}")
            return self.response # the last response retrieved
        
    def get_daily(self):
        try:
            self.d_forecast = requests.get(f'{self.forecast_url}').json()
        except:
            pass
        return self.d_forecast
        
    def get_hourly(self):
        try:
            self.h_forecast = requests.get(f'{self.hourly_url}').json()
        except:
            pass
        return self.h_forecast

    def is_new(self):
        if 'updated' in self.last_response.keys() and 'updated' in self.response.keys() and self.alerts > 0:
            if self.last_response['updated'] == self.response['updated']:
                return False
            else:
                self.last_response = self.response # so we don't have repeated alerts
                self.asterisk = True
                self.button.setText(f"* {self.name} ({self.alerts})")
                return True
        
    def num_alerts(self):
        self.alerts = 0
        if 'features' in self.response.keys():
            for i in self.response['features']:
                self.alerts += 1
        return self.alerts
    
    def display(self):
        self.asterisk = False
        self.msgBox.show()
        self.msgBox.setText(f"Updating {self.name} alerts")
        self.update()
        self.msgBox.setText(f"Updating {self.name} daily forecast")
        self.get_daily()
        self.msgBox.setText(f"Updating {self.name} hourly forecast")
        self.get_hourly()
        self.out = DataWindow(self.response, self.name, self.alerts, self.d_forecast, self.h_forecast)
        self.msgBox.close()
        self.out.show()

    def get_button(self):
        return self.button

    def button_grey(self):
        self.button.setStyleSheet(f'background-color: {brmc_warm_grey}; color: {brmc_gold}')

    def button_normal(self):
        self.button.setStyleSheet(f'background-color: {brmc_dark_blue}; color: {brmc_gold}')

    def button_red(self):
        self.button.setStyleSheet('background-color: red; color: black')

#--------------------------------------------------------------------------------------------------------------------------------

class NonBlockingDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('weather-lightning.png'))
        self.setWindowTitle("Initializing")
        self.resize(QSize(500,10))
        layout = QVBoxLayout()
        self.setLayout(layout)

    def setText(self, msg):
        self.setWindowTitle(f"{msg}")

#--------------------------------------------------------------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("Blue Ridge Medical Center", "Weather Alert Widget")
        self.resize(self.settings.value('MainWindowSize', QSize(450, 50)))
        self.move(self.settings.value('MainWindowPos', QPoint(50, 50)))

        self.setStyleSheet(f'background-color: {brmc_medium_blue}')
        
        self.setWindowTitle(f'Weather Widget version {progver}')
        self.setWindowIcon(QIcon('weather-lightning.png'))

        self.msgBox = NonBlockingDialog()
        container = QWidget()
        layout = QGridLayout()

        # Create location object
        
        self.msgBox.show()
        for i in locations.keys():
            lat, lon, zone = locations[i].split(',')
            self.msgBox.setText(f"Retrieving {i}")
            buttons.append(Location(i, lat, lon, zone))
        self.msgBox.close()

        # Add location object to layout
        x = 0
        y = 0
        for j in buttons:
            layout.addWidget(j.get_button(), y, x)
            x += 1
            if x >= num_cols:
                x = 0
                y += 1

        container.setLayout(layout)
        self.setCentralWidget(container)

        timer = QTimer(self)
        timer.timeout.connect(self.do_update)
        timer.start(60000)  # milliseconds

    def do_update(self):    # Update all location objects
        for k in buttons:
            k.update()
            if k.is_new():
                if sys.platform == "win32":
                    widget_window = gw.getWindowsWithTitle('Weather Widget')[0]
                    try:
                        widget_window.restore()
                        widget_window.activate()
                    except:
                        pass
                    frequency = 2500
                    duration = 250
                    winsound.Beep(frequency, duration)
                else:
                    self.raise_()
                    self.activateWindow()
                    self.showNormal()
        

    def closeEvent(self, a0):
        self.settings.setValue('MainWindowSize', self.size())
        self.settings.setValue('MainWindowPos', self.pos())
        return super().closeEvent(a0)

#--------------------------------------------------------------------------------------------------------------------------------

class DataWindow(QWidget):
    def __init__(self, response, which, alerts, d_forecast, h_forecast):
        super().__init__()
        self.response = response
        self.which = which
        self.whichPos = which+'pos'
        self.whichSize = which+'size'
        self.alerts = alerts
        self.d_forecast = d_forecast
        self.h_forecast = h_forecast
        self.setContentsMargins(10, 10, 10, 10)
        self.settings = QSettings( "Blue Ridge Medical Center", 'Weather Alert Widget')
        self.resize(self.settings.value(self.whichSize, QSize(655, 600)))
        self.move(self.settings.value(self.whichPos, QPoint(50, 150)))
        self.setStyleSheet(f'background-color: {brmc_medium_blue}; color: black')
        if self.alerts > 0:
            self.alert_button = QPushButton(f"Alerts ({self.alerts})")
        else:
            self.alert_button = QPushButton("Alerts")
        self.alert_button.clicked.connect(self.show_alerts)
        self.alert_icon = QIcon('exclamation-diamond-frame.png')
        self.alert_button.setIcon(self.alert_icon)
        self.alert_button.setStyleSheet(f'background-color: {brmc_dark_blue}; color: {brmc_gold}')
        self.daily_button = QPushButton("Daily Forecast")
        self.daily_button.clicked.connect(self.show_daily)
        self.daily_icon = QIcon('report--pencil.png')
        self.daily_button.setIcon(self.daily_icon)
        self.daily_button.setStyleSheet(f'background-color: {brmc_dark_blue}; color: {brmc_gold}')
        self.hourly_button = QPushButton("Hourly Forecast")
        self.hourly_button.clicked.connect(self.show_hourly)
        self.hourly_icon = QIcon('alarm-clock.png')
        self.hourly_button.setIcon(self.hourly_icon)
        self.hourly_button.setStyleSheet(f'background-color: {brmc_dark_blue}; color: {brmc_gold}')
        layout = QVBoxLayout()
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.alert_button)
        hbox_layout.addWidget(self.daily_button)
        hbox_layout.addWidget(self.hourly_button)

        self.divLine = "\n|-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|\n"

        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet(f'background-color: {brmc_gold}; color: black')

        if self.alerts > 0:
            self.show_alerts()
        else:
            self.show_daily()
                        
        self.cursor = self.text_edit.textCursor()
        self.cursor.setPosition(0)
        self.text_edit.setTextCursor(self.cursor)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        layout.addLayout(hbox_layout)
        self.setLayout(layout)

    def show_alerts(self):
        self.setWindowTitle(f"Current Alerts for {self.which} ({self.alerts})")
        self.setWindowIcon(QIcon('exclamation-diamond-frame.png'))
        self.text_edit.clear()
        if 'title' in self.response.keys(): self.text_edit.insertPlainText(self.response['title']+'\n')
        if 'updated' in self.response.keys(): self.text_edit.insertPlainText("Last NWS Update: " + datetime.fromisoformat(self.response['updated']).astimezone(tz_NY).strftime("%m/%d/%y @ %H:%M") + '\n')
        self.text_edit.insertPlainText("Content refreshed: " + self.response['Retrieved']+'\n')
        self.text_edit.insertPlainText(self.divLine+'\n')
        if 'features' in self.response.keys():
                for x in self.response['features']:
                    self.text_edit.insertPlainText(str(x['properties']['areaDesc']) + '\n\n')
                    self.text_edit.insertPlainText(str(x['properties']['headline']) + '\n\n')
                    self.text_edit.insertPlainText(str(x['properties']['description']) + '\n')
                    self.text_edit.insertPlainText(str(x['properties']['instruction']) + '\n')
                    self.text_edit.insertPlainText(self.divLine + '\n')
        self.text_edit.insertPlainText('End of Alerts')
    
    def show_daily(self):
        self.setWindowTitle(f"Daily Forecast for {self.which}")
        self.setWindowIcon(QIcon('report--pencil.png'))
        self.text_edit.clear()
        for period in self.d_forecast['properties']['periods']:
            self.text_edit.insertPlainText(str(period['name']+': '+period['shortForecast']+'\n'))
            self.text_edit.insertPlainText(str('Temperature: '+str(period['temperature'])+' '+period['temperatureUnit']+'\n'))
            self.text_edit.insertPlainText(str('Wind: '+str(period['windSpeed'])+' '+period['windDirection']+'\n'))
            self.text_edit.insertPlainText(str('Chance of Precipitation: '+str(period['probabilityOfPrecipitation']['value'])+'%\n'))
            if period['detailedForecast']:
                self.text_edit.insertPlainText(str('Detailed Forecast: '+period['detailedForecast']+'\n'))
            self.text_edit.insertPlainText(self.divLine)
        self.text_edit.insertPlainText('End of Forecast')

    def show_hourly(self):
        self.setWindowTitle(f"Hourly Forecast for {self.which}")
        self.setWindowIcon(QIcon('alarm-clock.png'))
        self.text_edit.clear()
        for period in self.h_forecast['properties']['periods']:
            self.text_edit.insertPlainText(str(period['name'] + ' ' + datetime.fromisoformat(period['startTime']).astimezone(tz_NY).strftime("%B %d, %Y @ %H:%M") + ': ' + period['shortForecast'] + ', ' + str(period['temperature']) + ' ' + period['temperatureUnit'] + ', ' + str(period['relativeHumidity']['value']) + '% humidity\n'))
            self.text_edit.insertPlainText(str('Wind: ' + str(period['windSpeed']) + ' ' + period['windDirection'] + ', ' + 'Chance of Precipitation: ' + str(period['probabilityOfPrecipitation']['value']) + '%\n'))
            if period['detailedForecast']:
                self.text_edit.insertPlainText(str(period['detailedForecast']+'\n'))
            self.text_edit.insertPlainText(self.divLine)
        self.text_edit.insertPlainText('End of Forecast')

    def closeEvent(self, a0):
        self.settings.setValue(self.whichSize, self.size())
        self.settings.setValue(self.whichPos, self.pos())
        return super().closeEvent(a0)

#--------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    if is_running(os.path.basename(__file__)):
        sys.exit()

    app = QApplication(sys.argv)
    if sys.platform == "win32":
        try:
            update = datetime.fromtimestamp(os.path.getmtime(__file__)).strftime("%m/%d/%y @ %H:%M:%S") < datetime.fromtimestamp(os.path.getmtime(update_source)).strftime("%m/%d/%y @ %H:%M:%S")
        except:
            update = False
        if update:
            atexit.register(update_app)
            dialog = UpdateDialog()
            if dialog.exec():
                sys.exit()
            else:
                atexit.unregister(update_app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

#--------------------------------------------------------------------------------------------------------------------------------

"""
Change log:

v 0.1       : 250205        : Initial version
v 0.2       : 250207        : Additional layout and display tweaks, including changing button colors and adding 
                            : number of alerts to buttons
v 0.3       : 250212        : Added tests to catch KeyError, updated refresh to 5 minutes
v 0.4       : 250217        : Added error checking on API availability
v 0.5       : 250221        : Buttons will go grey during data refresh to show when they will be unresponsive. This will only appear
                            :   if the API has a very slow response. (I thought this worked -- does it really?)
v 0.6       : 250224        : Implemented a timer to manage refresh interval so a refresh doesn't occur every button push.
v 0.7       : 250306        : Implemented non-blocking windows. Also automatic app updates.
v 0.8       : 250311-250318 : Complete re-write migrating from PySimpleGUI to PySide6
v 0.9       : 250318        : Added code to flash the tray icon when buttons turn red.
v 0.9(a)    : 250319        : Minor UI/display tweaks.
v 0.9(b)    : 250320        : More minor tweaks to how alerts display.
v 1.0       : 250320        : Added custom task bar icons.
v 1.01      : 250321        : Added check to prevent multiple copies from running.
v 1.02      : 250402        : Alert display windows now remember their location on exit.
v 1.03      : 250408        : Updated Location class to return the last retrieved response if the api request fails -- this way a failure won't
                            : clear any alerts.
v 1.04β     : 250411        : Updated Location class and added logic to button updates -- app should now only attempt to gain focus when there is 
                            : actually a new alert -- not every minute when an alert is active.
            : 250414        : Small tweak to v 1.04β update to eliminate errors.
v 1.05      : 250415        : Windows only - added a beep when window wants focus.
v 1.06      : 250513        : Updated display of NWS update to local time zone.
v 1.07      : 250515        : Network unavailable won't prevent launch checking for unreachable file for upgrade check
v 2.0       : 250613        : Major refactoring -- moved all functionality possible into the Location class to enable easier customization of
                            :   Locations. Updated to include Charlottesville & Lynchburg.
v 2.01      : 250613        : Minor tweak to automatic upgrade scheme.
v 2.1       : 250617        : Refactored to configure locations dynamically from a dictionary.
v 2.2       : 250618        : Reads location configuration from file: walerts.json. On failure will display default
                            :   locations (Charlottesville, Nelson, Amherst, Lynchburg, & Appomattox)
v 2.3       : 250618        : Fixed issue with raise_() and activateWindow() being in the wrong place
v 2.4       : 250618        : Changed from QHBoxLayout to QGridLayout, building rows of 12 buttons each.
v 2.4(a)    : 250619        : Changed button rows from 12 to 10.
v 2.4(b)    : 250619        : Another tweak to fix the automatic upgrade scheme. Added asterisk to button display when alert is new.
v 2.4(c)    : 250619        : Updated asterisk to be persistent until the alert is viewed or expires.
v 2.4(d)    : 250626        : Parameterized configurable items and moved them to the top of the file.
v 2.4(e)    : 250707        : Added check to eliminate key error in is_new()
v 2.4(f)    : 250709        : Added number of alerts to display window title (because I never remembered to scroll down!)
v 2.4(g)    : 250710        : Corrected a condition where an update with no alert would cause the interface to alert.
v 3.0       : 250721-250801 : Major rewrite to include daily and hourly forecasts as well as alerts.
v 3.01      : 250804        : Corrected issue parsing configuration file. Minor UI tweaks.
v 3.02      : 250826        : Added initialization progress display.
v 3.02a     : 250909        : Added progress display when updating forecasts (when button is pressed).
v 3.02b     : 250916        : Updated checks to eliminate asterisk/tone on change to no alert.
v 3.02c     : 251001        : Implemented PyGetWindow to bring window to the front/active when an alert occurs.
v 3.02d     : 251003        : PyGetWindow aparently only has the Windows portion implemented -- bringing back cross-platform function
"""
