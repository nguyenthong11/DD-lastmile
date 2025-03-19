"""
Created on Wed Jan 12 11:30:34 2022
@author: quoc-thongnguyen
"""

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


def send_request(list_coordinates: list, V: int, API: str): # response from open_route_service
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
    try:
        call = requests.post(url, json=body, headers=headers)
        response = json.loads(call.text)
    except Exception as e:
        print('Error in sending request: {}'.format(e))
        response = None
    return response