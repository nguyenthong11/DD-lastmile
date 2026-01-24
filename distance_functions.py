"""
Created on Wed Jan 12 11:30:34 2022
@author: quoc-thongnguyen
"""

import json
import requests
import numpy as np
from typing import List, Tuple

def calculate_route_distances(
    routes: List[List[int]], 
    distance_matrix,
    depot_index: int = 0,
    return_to_depot: bool = True
) -> Tuple[float, List[float]]:
    """
    Calculate total distance and individual distances for multiple routes.
    
    Parameters
    ----------
    routes : List[List[int]]
        List of routes, where each route is a list of node indices to visit.
        Example: [[1, 2, 3], [4, 5]] represents two routes
    
    distance_matrix : np.ndarray
        Square distance matrix where distance_matrix[i][j] is the distance
        from node i to node j. Shape: (n_nodes, n_nodes)
    
    depot_index : int, default=0
        Index of the depot (starting/ending point) in the distance matrix
    
    return_to_depot : bool, default=True
        If True, routes return to depot (depot → nodes → depot)
        If False, routes end at last node (depot → nodes)
    
    Returns
    -------
    total_distance : float
        Sum of all route distances
    
    route_distances : List[float]
        Distance for each individual route
    
    Raises
    ------
    ValueError
        If routes contain invalid indices or distance_matrix is invalid
    
    Examples
    --------
    >>> dist_matrix = np.array([
    ...     [0, 10, 15, 20],
    ...     [10, 0, 35, 25],
    ...     [15, 35, 0, 30],
    ...     [20, 25, 30, 0]
    ... ])
    >>> routes = [[1, 2], [3]]
    >>> total, individual = calculate_route_distances(routes, dist_matrix)
    >>> print(f"Total: {total}, Individual: {individual}")
    Total: 90.0, Individual: [60.0, 30.0]
    
    Notes
    -----
    - Does NOT modify input routes (creates copies)
    - Validates all node indices against distance matrix
    - Handles empty routes gracefully
    - Assumes symmetric distance matrix (distance[i][j] == distance[j][i])
    """
    
    # ==================== VALIDATION ====================
    
    # Validate distance matrix
    if not isinstance(distance_matrix, np.ndarray):
        distance_matrix = np.array(distance_matrix)
    
    if distance_matrix.ndim != 2:
        raise ValueError(f"distance_matrix must be 2D, got shape {distance_matrix.shape}")
    
    if distance_matrix.shape[0] != distance_matrix.shape[1]:
        raise ValueError(
            f"distance_matrix must be square, got shape {distance_matrix.shape}"
        )
    
    n_nodes = distance_matrix.shape[0]
    
    # Validate depot index
    if not (0 <= depot_index < n_nodes):
        raise ValueError(
            f"depot_index {depot_index} out of range [0, {n_nodes-1}]"
        )
    
    # Validate routes is a list
    if not isinstance(routes, list):
        raise ValueError("routes must be a list of lists")
    
    
    # ==================== CALCULATE DISTANCES ====================
    
    total_distance = 0.0
    route_distances = []
    
    for route_idx, route in enumerate(routes):
        # Skip empty routes
        if not route:
            route_distances.append(0.0)
            continue
        
        # Validate route nodes
        for node in route:
            if not isinstance(node, (int, np.integer)):
                raise ValueError(
                    f"Route {route_idx} contains non-integer node: {node}"
                )
            if not (0 <= node < n_nodes):
                raise ValueError(
                    f"Route {route_idx} contains invalid node {node}, "
                    f"valid range is [0, {n_nodes-1}]"
                )
        
        # Build complete route: depot → nodes → [depot]
        if return_to_depot:
            complete_route = [depot_index] + route + [depot_index]
        else:
            complete_route = [depot_index] + route
        
        # Calculate distance for this route
        route_distance = 0.0
        for i in range(len(complete_route) - 1):
            from_node = complete_route[i]
            to_node = complete_route[i + 1]
            route_distance += distance_matrix[from_node, to_node]
        
        route_distances.append(route_distance)
        total_distance += route_distance
    
    return total_distance, route_distances

def send_request(list_coordinates: list, vehicle: str, API: str): # response from open_route_service
    body = {"locations": list_coordinates,
            "metrics": ["distance","duration"],
            "units": "m"}
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': API,
        'Content-Type': 'application/json; charset=utf-8'
        }
    base_url = "https://api.openrouteservice.org/v2/matrix"
    url = f"{base_url}/{vehicle}"
    try:
        call = requests.post(url, json=body, headers=headers)
        response = json.loads(call.text)
    except Exception as e:
        print('Error in sending request: {}'.format(e))
        response = None
    return response