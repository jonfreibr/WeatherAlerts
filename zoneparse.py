"""
Parse alert zones out of https://api.weather.gov/zones
saved to local directory as "zones"
"""

import json

with open('zones', 'r') as file:
    data = json.load(file)

for i in data['features']:
    print(i['properties']['state'], "|", i['properties']['name'], "|", i['properties']['type'], "|", i['properties']['id'])