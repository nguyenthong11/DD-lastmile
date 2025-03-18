#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 11:30:34 2022
@author: quoc-thongnguyen
"""

from __future__ import division
from __future__ import print_function
import json
import requests

# return route distance
def route_distance(route, Dist_matrix):
    """Returns the route distances."""
    # Convert from routing variable Index to distance matrix NodeIndex.
    D = 0
    Dtour = []
    for routei in route:
        routei.append(0)
        Dtouri = 0
        for i in range(len(routei)-1):
            D +=  Dist_matrix[routei[i]][routei[i+1]]
            Dtouri += Dist_matrix[routei[i]][routei[i+1]]
        Dtour.append(Dtouri)  
    return D, Dtour
# response from open_route_service
def send_request(list_coordinates, V, API):
    body = {"locations": None,
            "metrics": ["distance","duration"],
            "units": "m"}
    body["locations"] = list_coordinates
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': API,
        'Content-Type': 'application/json; charset=utf-8'
        }
    if V == 0: vehicle = 'driving-car'
    elif V == 1: vehicle = 'cycling-electric'
    else: vehicle = 'foot-hiking'
    url = 'https://api.openrouteservice.org/v2/matrix/'+ vehicle
    call = requests.post(url, json=body, headers=headers)
    response = json.loads(call.text)
    return response
# response distance 2 locations
def d2loc(pair_coors, V, API):
    body = {"coordinates":pair_coors}
    headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
    'Authorization': API,
    'Content-Type': 'application/json; charset=utf-8'
    }
    if V == 0: vehicle = 'driving-car'
    elif V == 1: vehicle = 'cycling-electric'
    else: vehicle = 'foot-hiking'
    api = 'https://api.openrouteservice.org/v2/directions/'+ vehicle
    call = requests.post(api, json=body, headers=headers)
    respone = json.loads(call.text)
    d = respone['routes'][0]['summary']
    return d['distance']