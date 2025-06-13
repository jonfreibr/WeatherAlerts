#!/usr/bin/env python3
"""
Program : Weather Alerts
Author  : Jon Freivald <jfreivald@brmedical.com>
        : Copyright © Blue Ridge Medical Center, 2025. All Rights Reserved
        : License: GNU GPL Version 3
Date    : 2025-02-05
Purpose : To poll the National Weather Service for location specific alerts
        : Version change log at EoF.
"""

import atexit
import os
import psutil
import pytz
import requests
import subprocess
import sys
import time

if sys.platform == "win32":
    import winsound

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
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QDialogButtonBox,
)

progver = '2.01'

tz_NY = pytz.timezone('America/New_York')
brmc_dark_blue = '#00446a'
brmc_medium_blue = '#73afb6'
brmc_gold = '#ffcf01'
brmc_rust = '#ce7067'
brmc_warm_grey = '#9a8b7d'

#--------------------------------------------------------------------------------------------------------------------------------

class UpdateDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet(f'background-color: {brmc_medium_blue}')
        self.setWindowTitle("Update Available!")
        layout = QVBoxLayout()
        self.label = QLabel("There is an update available for the Weather Alert application.")
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
        subprocess.Popen(["cmd", "/c", "H:/_BRMCApps/WeatherAlerts/install.bat", "/min"], stdout=None, stderr=None)

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

    def __init__(self, zone, name):
        self.zone = zone
        self.name = name
        self.response = None
        self.timer = Timer()
        self.button = QPushButton(self.name)
        self.button.clicked.connect(self.display)
        self.button_normal()
        try:
            self.response = requests.get(f'https://api.weather.gov/alerts/active/zone/{self.zone}').json()
            self.response.update({'Retrieved':datetime.now(tz_NY).strftime("%m/%d/%y @ %H:%M")})
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
        if self.alerts > 0:
            self.button_red()
            self.button.setText(f"{self.name} ({self.alerts})")
            if self.is_new():
                self.bring_forward()
        
        
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
        
    def is_new(self):
        if self.last_response['updated'] == self.response['updated']:
            return False
        else:
            self.last_response = self.response # so we don't have repeated alerts
            return True
        
    def num_alerts(self):
        self.alerts = 0
        if 'features' in self.response.keys():
            for i in self.response['features']:
                self.alerts += 1
        return self.alerts
    
    def display(self):
        self.out = DataWindow(self.response, self.name)
        self.out.show()

    def get_button(self):
        return self.button

    def button_grey(self):
        self.button.setStyleSheet(f'background-color: {brmc_warm_grey}; color: {brmc_gold}')

    def button_normal(self):
        self.button.setStyleSheet(f'background-color: {brmc_dark_blue}; color: {brmc_gold}')

    def button_red(self):
        self.button.setStyleSheet('background-color: red; color: black')

    def bring_forward(self):
        self.raise_()
        self.activateWindow()
        if sys.platform == "win32":
            frequency = 2500
            duration = 250
            winsound.Beep(frequency, duration)

#--------------------------------------------------------------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("Blue Ridge Medical Center", "Weather Alert Widget")
        self.resize(self.settings.value('MainWindowSize', QSize(450, 50)))
        self.move(self.settings.value('MainWindowPos', QPoint(50, 50)))

        self.setStyleSheet(f'background-color: {brmc_medium_blue}')
        
        self.setWindowTitle(f'Weather Alerts version {progver}')
        self.setWindowIcon(QIcon('weather-lightning.png'))
        container = QWidget()
        layout = QHBoxLayout()

        # Create location object

        self.cville = Location("VAC540", "Charlottesville")
        self.nelson = Location("VAC125", "Nelson")
        self.amherst = Location("VAC009", "Amherst")
        self.lburg = Location("VAC680", "Lynchburg")
        self.appomattox = Location("VAC011", "Appomattox")

        # Add location object to layout

        layout.addWidget(self.cville.get_button())
        layout.addWidget(self.nelson.get_button())
        layout.addWidget(self.amherst.get_button())
        layout.addWidget(self.lburg.get_button())
        layout.addWidget(self.appomattox.get_button())

        container.setLayout(layout)
        self.setCentralWidget(container)

        timer = QTimer(self)
        timer.timeout.connect(self.do_update)
        timer.start(60000)  # milliseconds

    def do_update(self):    # Update all location objects
        self.cville.update()
        self.nelson.update()
        self.amherst.update()
        self.lburg.update()
        self.appomattox.update()
        

    def closeEvent(self, a0):
        self.settings.setValue('MainWindowSize', self.size())
        self.settings.setValue('MainWindowPos', self.pos())
        return super().closeEvent(a0)

#--------------------------------------------------------------------------------------------------------------------------------

class DataWindow(QWidget):
    def __init__(self, response, which):
        super().__init__()
        self.response = response
        self.which = which
        self.whichPos = which+'pos'
        self.whichSize = which+'size'
        self.setWindowTitle("Current Alerts")
        self.setWindowIcon(QIcon('exclamation-diamond-frame.png'))
        self.setContentsMargins(10, 10, 10, 10)
        self.settings = QSettings( "Blue Ridge Medical Center", 'Weather Alert Widget')
        self.resize(self.settings.value(self.whichSize, QSize(655, 600)))
        self.move(self.settings.value(self.whichPos, QPoint(50, 150)))
        self.setStyleSheet(f'background-color: {brmc_medium_blue}; color: black')
        layout = QHBoxLayout()

        divLine = "\n|-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|\n"

        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet(f'background-color: {brmc_gold}; color: black')
        if 'title' in self.response.keys(): self.text_edit.insertPlainText(self.response['title']+'\n')
        if 'updated' in self.response.keys(): self.text_edit.insertPlainText("Last NWS Update: " + datetime.fromisoformat(self.response['updated']).astimezone(tz_NY).strftime("%m/%d/%y @ %H:%M") + '\n')
        self.text_edit.insertPlainText("Content refreshed: " + self.response['Retrieved']+'\n')
        self.text_edit.insertPlainText(divLine+'\n')
        if 'features' in self.response.keys():
                for x in self.response['features']:
                    self.text_edit.insertPlainText(str(x['properties']['areaDesc']) + '\n\n')
                    self.text_edit.insertPlainText(str(x['properties']['headline']) + '\n\n')
                    self.text_edit.insertPlainText(str(x['properties']['description']) + '\n')
                    self.text_edit.insertPlainText(str(x['properties']['instruction']) + '\n')
                    self.text_edit.insertPlainText(divLine + '\n')
        self.text_edit.insertPlainText('End of Alerts')
                        
        self.cursor = self.text_edit.textCursor()
        self.cursor.setPosition(0)
        self.text_edit.setTextCursor(self.cursor)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

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
                if datetime.fromtimestamp(os.path.getmtime(__file__)).strftime("%m/%d/%y @ %H:%M:%S") < datetime.fromtimestamp(os.path.getmtime('H:/_BRMCApps/WeatherAlerts/walerts.py')).strftime("%m/%d/%y @ %H:%M:%S"):
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
"""
