from recorder import Recorder
from typing import List, Dict, Any
from ortools.graph import pywrapgraph


class Agent(Recorder):
    """ Agent for dispatching and reposition """

    def __init__(self, **kwargs):
        """ Load your trained model and initialize the parameters """
        super().__init__()

    def dispatch(self, dispatch_observ: List[Dict[str, Any]], index2hash=None) -> List[Dict[str, int]]:
        """ Compute the assignment between drivers and passengers at each time step
        :param dispatch_observ: a list of dict, the key in the dict includes:
                order_id, int
                driver_id, int
                order_driver_distance, float
                order_start_location, a list as [lng, lat], float
                order_finish_location, a list as [lng, lat], float
                driver_location, a list as [lng, lat], float
                timestamp, int
                order_finish_timestamp, int
                day_of_week, int
                reward_units, float
                pick_up_eta, float
        :param index2hash: driver_id to driver_hash
        :return: a list of dict, the key in the dict includes:
                order_id and driver_id, the pair indicating the assignment
        """
        dispatch = []
        global_num = 2
        order2idx = dict()
        idx2order = dict()
        driver2idx = dict()
        idx2driver = dict()
        for od in dispatch_observ:
            order_id = od['order_id']
            driver_id = od['driver_id']
            if order_id not in order2idx:
                order2idx[order_id] = global_num
                idx2order[global_num] = order_id
                global_num += 1
            if driver_id not in driver2idx:
                driver2idx[driver_id] = global_num
                idx2driver[global_num] = driver_id
                global_num += 1
        start_nodes = []
        end_nodes = []
        capacities = []
        unit_costs = []
        for od in dispatch_observ:
            order_idx = order2idx[od['order_id']]
            driver_idx = driver2idx[od['driver_id']]
            cost = int(od['order_driver_distance'])
            start_nodes.append(order_idx)
            end_nodes.append(driver_idx)
            unit_costs.append(cost)
            capacities.append(1)

        src = 0
        dst = 1
        for order_idx in idx2order:
            start_nodes.append(src)
            end_nodes.append(order_idx)
            unit_costs.append(0)
            capacities.append(1)

        for driver_idx in idx2driver:
            start_nodes.append(driver_idx)
            end_nodes.append(dst)
            unit_costs.append(0)
            capacities.append(1)
        min_cost_flow = pywrapgraph.SimpleMinCostFlow()
        for i in range(0, len(start_nodes)):
            min_cost_flow.AddArcWithCapacityAndUnitCost(start_nodes[i], end_nodes[i], capacities[i], unit_costs[i])
        min_cost_flow.SetNodeSupply(0, min(len(order2idx), len(driver2idx)))
        min_cost_flow.SetNodeSupply(1, -min(len(order2idx), len(driver2idx)))
        min_cost_flow.SolveMaxFlowWithMinCost()
        for i in range(min_cost_flow.NumArcs()):
            if min_cost_flow.Flow(i) > 0.1:
                if min_cost_flow.Tail(i) != 0 and min_cost_flow.Head(i) != 1:
                    dispatch.append(dict(order_id=idx2order[min_cost_flow.Tail(i)], driver_id=idx2driver[min_cost_flow.Head(i)]))
        return dispatch

    def reposition(self, repo_observ):
        """ Compute the reposition action for the given drivers
        :param repo_observ: a dict, the key in the dict includes:
                timestamp: int
                driver_info: a list of dict, the key in the dict includes:
                        driver_id: driver_id of the idle driver in the treatment group, int
                        grid_id: id of the grid the driver is located at, str
                day_of_week: int
        :return: a list of dict, the key in the dict includes:
                driver_id: corresponding to the driver_id in the od_list
                destination: id of the grid the driver is repositioned to, str
        """
        # repo_action = []
        # for driver in repo_observ['driver_info']:
        #     # the default reposition is to let drivers stay where they are
        #     repo_action.append({'driver_id': driver['driver_id'], 'destination': driver['grid_id']})
        # return repo_action
        return []
