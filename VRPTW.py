"""Vehicles Routing Problem (VRP) with Time Windows."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pickle

def create_data_modelTW():
    """Stores the data for the problem."""
    data = {}
    data['time_matrix'] = []
    data['time_windows'] = []
    data['num_vehicles'] = 4
    data['depot'] = 0
    data['vehicle_capacities'] = []
    data['demands'] = []
    return data

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    #print(f'Objective: {solution.ObjectiveValue()}')
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    route = []
    TIME = []
    time_p_route = []
    Nvehicle = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        routeI = []
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            plan_output += '{0} Time({1},{2}) -> \n'.format(
                manager.IndexToNode(index), solution.Min(time_var),
                solution.Max(time_var))
            routeI.append(manager.IndexToNode(index))
            TIME.append((solution.Min(time_var),solution.Max(time_var)))
            index = solution.Value(routing.NextVar(index))
        time_var = time_dimension.CumulVar(index)
        plan_output += '{0} Time({1},{2})\n'.format(manager.IndexToNode(index),
                                                    solution.Min(time_var),
                                                    solution.Max(time_var))
        plan_output += 'Time of the route: {}min\n'.format(solution.Min(time_var))
        if solution.Min(time_var)>0:
            Nvehicle +=1
            time_p_route.append(solution.Min(time_var))
        # print(plan_output)
        route.append(routeI)
        total_time += solution.Min(time_var)
    # print('Total time of all routes: {}min'.format(total_time))
    return route, TIME, total_time, time_p_route, Nvehicle


def SolveProblemTW(data):
    """Solve the VRP with time windows."""
    # Instantiate the data problem.
    # data = create_data_modelTW()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint.
    time = 'Time'
    routing.AddDimension(
        transit_callback_index,
        90,  # allow waiting time
        600,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time)
    time_dimension = routing.GetDimensionOrDie(time)
    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == data['depot']:
            continue
        index = manager.NodeToIndex(location_idx)
        # print(f"adding disjunction for route node {location_idx} (index {index})")
        # routing.AddDisjunction([index], 3000)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # Add time window constraints for each vehicle start node.
    depot_idx = data['depot']
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][depot_idx][0],
            data['time_windows'][depot_idx][1])
    # Instantiate route start and end times to produce feasible times.
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))
# --------------------------------------------------------
    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
# --------------------------------------------------------
    # Setting first solution heuristic.
    # PATH_CHEAPEST_ARC, PATH_MOST_CONSTRAINED_ARC,EVALUATOR_STRATEGY,SAVINGS,SWEEP,
    # CHRISTOFIDES, ALL_UNPERFORMED, BEST_INSERTION, PARALLEL_CHEAPEST_INSERTION,
    # LOCAL_CHEAPEST_INSERTION, GLOBAL_CHEAPEST_ARC, LOCAL_CHEAPEST_ARC, FIRST_UNBOUND_MIN_VALUE

    # GUIDED_LOCAL_SEARCH, SIMULATED_ANNEALING, TABU_SEARCH, GENERIC_TABU_SEARCH
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)

    search_parameters.time_limit.FromSeconds(110)
    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    print("Solver status: ", routing.status())

    # Print solution on console.
    if solution:
        route, TIME, total_time, time_p_route, Nvehicle = print_solution(data, manager, routing, solution)
    else:
        print('No solution')

    return route, TIME, total_time, time_p_route, Nvehicle

def main():
    with open('data.pkl', 'rb') as f:
        data = pickle.load(f)
    route, TIME, total_time, time_p_route, Nveh = SolveProblemTW(data)
    print(route)
    print(f"Total Time of all routes: {total_time} minutes")

if __name__ == "__main__":
    main()
