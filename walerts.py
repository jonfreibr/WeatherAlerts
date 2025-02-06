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

# Distribution license for PiSimpleGUI v5
PySimpleGUI_License = 'enyNJQMSa3WaNFlJbBnxNllyVCHZlZwlZeSWIZ6FIPkDRSpocD3dRJyGa4W1Jh1udeGElsvHb2ipI9sOIWkjxuprYP2dVZu6cd2jVzJyReCuI16oMrTicuy7OZT0EE5KMLDkAP1tNsyjwQi7T9GZlpjPZuWi5gzWZKUcRxlAcsGHxjvpeEWq1xlXbLnrRYWjZyXiJKzPaQWa9cuUIgjToHiuNcSq4TwfIii4wEiaTYmJF4ttZMUZZgpDcynUN10HIPjDoIisSWmE9vukIYiww3iITqmEFktUZCU3xch7cs35QWiYOri5JvGic4m2VtpmddmIFCsHZICyIFs0IJkiNcvcbjXXB3hjbLnbkUinODiDJGCEb2HHV2lGIWFgJEpHZrG1dglrIrE619l2ZUGKlWjnYQWqwKgYQK2oVduQdIG5VXyqIni0w3idQl3oV0zidvG59pt2ZnXuJ7JlRCCxIf6VILjpkT3vNpTCEyi1LQCjJXEUYzXrRbloSwXEN0z7deWyVLkEIcjSoEipMgjVAAycNCCT03x0MRCk0RxgNkyfIcsJIzkbRThqduG1VJFBeLHNBKphcQmwVBzaI8jVoliJMfjPARyhNKSU0UwkM7yA0FxVOySeI7sgIAk9VotPYaWrlEsZQ3W6Rlk8cbm3VAzRcoyEIm6FIdmdpkm8cEmQVppbdqmaFfsPZdECBAijc1mH1wlMZwGVlhjDYQWuwauDYm2R9btGIci9wKixSEVJBBBvZKGfRtyyZcXpNhz7ImjIoJiIMPjcAJ1sLQjpIbyBMoCe4PyjMhz5MhuMMXTUEX2AIwnU0U=X3a60231e14c78915c4c7f16a8925b0fe8c44ec35a9ad759538d4d50c50c4d68b80ebf8e9ca576663b9d20176d071ab1d4d9ae2c40f56d8312423e2f966f1752319f88884d9aa823a5cf9a072e1da083313a6575b08c06ff09d6fccf012615fb26c28687d459aa0e5f4b73e1ca6b26f1b5254f275ba362656629ca0895749d37b8b79049dd79a425a683147d90db9604d10a1a8c4f00853d0f5e872357118797a8cc56179f500d67b59b96cefa92235ba3f69fe2f26cbd81e432eb601d5afb1ff5d0d6d7c0ec6b0e4423198c4b5bfa04df5c716a80edcbccfb43d384833f4983e81ebb69558d4f2fce376c39b6033356c9f58c891bce9f9d7803f8500932bd7345eb4dc68dfda56d2561017d9ae289ea664e75efe083f4a8ea71371d8695163586b271df3fbe20f5355d53ce20ef18652247c231cebf7ed0522eb37de95a4003330f0a45534995cb1b6d29adb7b484afabea551d861670f282e6cca724ad2d82f33ea6576aecea2bed372cd81cb408ad01704902dfe4d88471ca986132c87b8afb7ff8ad3c5ccfa1c3fe4724aab7271c0a7b0a3777836452e4259a558807c41572abffa69100429a9b8e166bf944169165c6e5af5b020a39be5ed685c952128831849945a7ebd96ee9c62dfd38aff2ce348b2f01f4297d59e0d643f1aa529b48674d926c6d845901a8d718d8cad459f7d13c2d7b7471aa0ee81e37e37557608b0'

import requests
import PySimpleGUI as sg
import os
import pickle

progver = '0.1'

BRMC = {'BACKGROUND': '#73afb6',
                 'TEXT': '#00446a',
                 'INPUT': '#ffcf01',
                 'TEXT_INPUT': '#00446a',
                 'SCROLL': '#ce7067',
                 'BUTTON': ('#ffcf01', '#00446a'),
                 'PROGRESS': ('#ffcf01', '#00446a'),
                 'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
                 }
sg.theme_add_new('BRMC', BRMC)

mainTheme = 'BRMC'
errorTheme = 'HotDogStand'
config_file = (f'{os.path.expanduser("~")}/w_alert.cfg')
winLoc = (50, 50)

# --------------------------------------------------
def get_user_settings():

	user_config = {}

	try:
		with open(config_file, 'rb') as fp:
			user_config = pickle.load(fp)
		fp.close()
	except:
		user_config['winLoc'] = winLoc

	return user_config

# --------------------------------------------------
def write_user_settings(user_config):

    try:
        with open(config_file, 'wb') as fp:
            pickle.dump(user_config, fp)
        fp.close()
    except:
	    errorWindow(f'File or data error: {config_file}. Updates NOT saved!', winLoc)

# --------------------------------------------------
def errorWindow(error, winLoc):

	sg.theme(errorTheme)
	layout = [ [sg.Text(f'Error: {error}')],
				[sg.Button('OK', bind_return_key=True)] ]
	window = sg.Window('Error Message', layout, location=winLoc, modal=True, finalize=True)
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'OK'): # if user closes window or clicks abort
			window.close()
			return True

# --------------------------------------------------
class Location:
        def __init__(self, zone, name):
                self.zone = zone
                self.name = name
                self.response = None

        headers = {
                "User-Agent": "BRMC Weather Alert Monitor, jfreivald@brmedical.com"
        }

        def __str__(self):
                return f"{self.zone}({self.name})"
        
        def update(self):
                self.response = requests.get(f'https://api.weather.gov/alerts/active/zone/{self.zone}').json()
                return self.response

# --------------------------------------------------
def main():
        user_config = get_user_settings()
        if 'winLoc' in user_config:
                winLoc = user_config['winLoc']
        else:
                winLoc = (50, 50)

        Nelson = Location("VAC125", "Nelson")
        Amherst = Location("VAC009", "Amherst")
        Appomattox = Location("VAC011", "Appomattox")

        sg.theme(mainTheme)
        layout = [ [sg.Button('Nelson', key='-NELSON-', button_color=None), sg.Button('Amherst', key='-AMHERST-', button_color=None),sg.Button('Appomattox', key='-APPOMATTOX-', button_color=None), sg.Button('Quit')] ]
        window = sg.Window(f'Weather Alerts {progver}', layout, location=winLoc, finalize=True)
        window.BringToFront()

        while True:
                nelson_response = Nelson.update()
                window['-NELSON-'].update(button_color = None)
                for x in nelson_response['features']:
                        window['-NELSON-'].update(button_color = ('red'))
                        
                amherst_response = Amherst.update()
                window['-AMHERST-'].update(button_color = None)
                for x in amherst_response['features']:
                        window['-AMHERST-'].update(button_color = ('red'))
                        
                appomattox_response = Appomattox.update()
                window['-APPOMATTOX-'].update(button_color = None)
                for x in appomattox_response['features']:
                        window['-APPOMATTOX-'].update(button_color = ('red'))
 
                event, values = window.read(timeout=60000) # Timeout and get new data
                winLoc = window.CurrentLocation()

                if event in (sg.WIN_CLOSED, 'Quit'):
                        if event == 'Quit':
                                user_config['winLoc'] = winLoc
                                write_user_settings(user_config)
                        break
                elif event == '-NELSON-':
                        showAlerts(nelson_response)
                elif event == '-AMHERST-':
                        showAlerts(amherst_response)
                elif event == '-APPOMATTOX-':
                        showAlerts(appomattox_response)

# --------------------------------------------------
def showAlerts(response):
        sg.theme(mainTheme)
        layout = [[sg.Output(size=(80,40), key='-OUTPUT-')]]
        window = sg.Window(title='Alert Details', layout=layout, finalize=True)
        window.BringToFront()
        
        print(response['title'])
        for x in response['features']:
                print(x['properties']['areaDesc'])
                print(x['properties']['headline'])
                print(x['properties']['description'])
                print(x['properties']['instruction'])
                print('\n******\n')

        while True:
                event, values = window.read()

                if event == sg.WIN_CLOSED:
                        break
                        


# --------------------------------------------------
if __name__ == '__main__':
        main()

"""
Change log:

v 0.1       : 250205    : Initial version
"""