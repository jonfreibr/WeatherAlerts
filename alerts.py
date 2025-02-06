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
# import json

progver = '0.1'

zone = "VAC125"

response = requests.get(f'https://api.weather.gov/alerts/active/zone/{zone}').json()

#print(response)

# response_pretty = json.dumps(response, indent=2)

# print(response_pretty)

for x in response['features']:
  print("\n\nALERT FOR: "+x['properties']['areaDesc']+"\n")
  print(x['properties']['headline'])
  print(x['properties']['description'])
  print(x['properties']['instruction'])
  print('\n******\n')





"""
Change log:

v 0.1       : 250205    : Initial version
"""