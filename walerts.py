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

import os
import sys
import time
import pytz
import psutil
import atexit
import requests
import subprocess
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
    QPushButton,
    QDialogButtonBox,
)

progver = '1.05'

tz_NY = pytz.timezone('America/New_York')
brmc_dark_blue = '#00446a'
brmc_medium_blue = '#73afb6'
brmc_gold = '#ffcf01'
brmc_rust = '#ce7067'
brmc_warm_grey = '#9a8b7d'

# --------------------------------------------------
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

# --------------------------------------------------
def is_running(script):
    for q in psutil.process_iter():
        if q.name().startswith('python'):
            if len(q.cmdline())>1 and script in q.cmdline()[1] and q.pid !=os.getpid():
                # print(f"'{script}' Process is already running")
                return True
            
    return False
            
# --------------------------------------------------
def update_app():
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", "H:/_BRMCApps/WeatherAlerts/install.bat", "/min"], stdout=None, stderr=None)
        
# --------------------------------------------------
class Timer:
    def __init__(self):
        self.then = time.time()

    def reset(self):
        self.then = time.time()

    def check(self):
        return time.time() - self.then
    
# --------------------------------------------------
class Location:

    headers = {
        "User-Agent": "BRMC Weather Alert Monitor, jfreivald@brmedical.com"
    }

    def __init__(self, zone, name):
        self.zone = zone
        self.name = name
        self.response = None
        self.timer = Timer()
        try:
            self.response = requests.get(f'https://api.weather.gov/alerts/active/zone/{self.zone}').json()
            self.response.update({'Retrieved':datetime.now(tz_NY).strftime("%m/%d/%y @ %H:%M")})
        except:
            self.response = {'title': 'API Not Available!', 'updated': 'Not updated!', 'Retrieved': 'Not Retrieved'}
        self.last_response = self.response

    def __str__(self):
        return f"{self.zone}({self.name})"
    
    def name(self):
        return f"{self.name}"
    
    def update(self):
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
            return self.response # the last response retrieved
        
    def is_new(self):
        if self.last_response['updated'] == self.response['updated']:
            return False
        else:
            return True
        
    def num_alerts(self):
        self.alerts = 0
        if 'features' in self.response.keys():
            for i in self.response['features']:
                self.alerts += 1
        return self.alerts


# --------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = QSettings( "Blue Ridge Medical Center", 'Weather Alert Widget')
        self.resize(self.settings.value('MainWindowSize', QSize(450, 50)))
        self.move(self.settings.value('MainWindowPos', QPoint(50, 50)))

        self.setStyleSheet(f'background-color: {brmc_medium_blue}')

        self.setWindowTitle(f"Weather Alerts version {progver}")
        self.setWindowIcon(QIcon('weather-lightning.png'))
        container = QWidget()
        layout = QHBoxLayout()

        self.Nelson = Location("VAC125", "Nelson")
        self.nelson_response = self.Nelson.update()
        self.n_button = QPushButton("Nelson")
        self.n_button.clicked.connect(self.pn)
        self.button_normal(self.n_button)
        layout.addWidget(self.n_button)

        self.Amherst = Location("VAC009", "Amherst")
        self.amherst_response = self.Amherst.update()
        self.am_button = QPushButton("Amherst")
        self.am_button.clicked.connect(self.pam)
        self.button_normal(self.am_button)
        layout.addWidget(self.am_button)

        self.Appomattox = Location("VAC011", "Appomattox")
        self.appomattox_response = self.Appomattox.update()
        self.ap_button = QPushButton("Appomattox")
        self.ap_button.clicked.connect(self.pap)
        self.button_normal(self.ap_button)
        layout.addWidget(self.ap_button)

        self.do_update() # Get the buttons right on startup
        
        n_timer = QTimer(self)
        n_timer.timeout.connect(self.do_update)
        n_timer.start(60000)
       
        container.setLayout(layout)

        self.setCentralWidget(container)

    def button_grey(self, button):
        button.setStyleSheet(f'background-color: {brmc_warm_grey}; color {brmc_gold}')

    def button_normal(self, button):
        button.setStyleSheet(f'background-color: {brmc_dark_blue}; color: {brmc_gold}')

    def button_red(self, button):
        button.setStyleSheet(f'background-color: red; color: black')

    def bring_forward(self):
        self.raise_()
        self.activateWindow()
        if sys.platform == "win32":
            frequency = 2500
            duration = 250
            winsound.Beep(frequency, duration)

    def pn(self):
        self.display_nelson(self.Nelson.update())

    def pam(self):
        self.display_amherst(self.Amherst.update())

    def pap(self):
        self.display_appomattox(self.Appomattox.update())

    def display_nelson(self, response):
        self.nout = DataWindow(response, "Nelson")
        self.nout.show()

    def display_amherst(self, response):
        self.amout = DataWindow(response, "Amherst")
        self.amout.show()

    def display_appomattox(self, response):
        self.apout = DataWindow(response, "Appomattox")
        self.apout.show()

    def do_update(self):
        # Update Nelson
        self.button_grey(self.n_button)
        self.n_button.setText("Updating")
        self.nelson_response = self.Nelson.update()
        self.button_normal(self.n_button)
        self.n_button.setText("Nelson")
        self.n_alerts = self.Nelson.num_alerts()
        if self.n_alerts > 0:
            self.button_red(self.n_button)
            self.n_button.setText(f"Nelson ({self.n_alerts})")
            if self.Nelson.is_new():
                self.bring_forward()
        # Update Amherst
        self.button_grey(self.am_button)
        self.am_button.setText("Updating")
        self.amherst_response = self.Amherst.update()
        self.button_normal(self.am_button)
        self.am_button.setText("Amherst")
        self.am_alerts = self.Amherst.num_alerts()
        if self.am_alerts > 0:
            self.button_red(self.am_button)
            self.am_button.setText(f"Amherst ({self.am_alerts})")
            if self.Amherst.is_new():
                self.bring_forward()
        # Update Appomattox
        self.button_grey(self.ap_button)
        self.ap_button.setText("Updating")
        self.appomattox_response = self.Appomattox.update()
        self.button_normal(self.ap_button)
        self.ap_button.setText("Appomattox")
        self.ap_alerts = self.Appomattox.num_alerts()
        if self.ap_alerts > 0:
            self.button_red(self.ap_button)
            self.ap_button.setText(f"Appomattox ({self.ap_alerts})")
            if self.Appomattox.is_new():
                self.bring_forward()
    
    def closeEvent(self, a0):
        self.settings.setValue('MainWindowSize', self.size())
        self.settings.setValue('MainWindowPos', self.pos())
        return super().closeEvent(a0)

# --------------------------------------------------
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
        if 'updated' in self.response.keys(): self.text_edit.insertPlainText("Last NWS Update: " + self.response['updated']+' (GMT)\n')
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

# --------------------------------------------------
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
"""
