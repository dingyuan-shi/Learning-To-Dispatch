import pickle
from collections import defaultdict
import math
from typing import Dict, List, Any, Set
import time


def acc_dist(lng1: float, lat1: float, lng2: float, lat2: float) -> float:
    delta_lat = (lat1 - lat2) / 2
    delta_lng = (lng1 - lng2) / 2
    arc_pi = 3.14159265359 / 180
    R = 6378137
    return 2 * R * math.asin(math.sqrt(
        math.sin(arc_pi * delta_lat) ** 2 + math.cos(arc_pi * lat1) * math.cos(arc_pi * lat2) * (
                math.sin(arc_pi * delta_lng) ** 2)))


class Recorder:

    def __init__(self):
        self.drivers_total_income = defaultdict(float)
        self.drivers_online_time = defaultdict(float)
        self.drivers_log_on_off = defaultdict(list)
        self.drivers_serving_order_info = defaultdict(list)
        self.drivers_income_per_hour = defaultdict(lambda: [0 for i in range(25)])
        self.active_drivers = set()
        self.median_ratio = 0.

    def __update_online_time(self, drivers_online_time: Dict[str, int]):
        """
        update the driver's online time
        :param drivers_online_time: a dict, with key is driver's id, value is online time (in seconds)
        :return: None
        """
        for driver_id in drivers_online_time:
            self.drivers_online_time[driver_id] = drivers_online_time[driver_id]

    def update_log_on(self, online_drivers_hash: Set[str], timestamp):
        """
        update the driver log_on time
        :param online_drivers_hash: online drivers' hashcode at this timestamp
        :param timestamp: current timestamp
        """
        self.active_drivers = self.active_drivers.union(online_drivers_hash)
        for driver_hash in online_drivers_hash:
            if len(self.drivers_log_on_off[driver_hash]) != 0:
                print("MULTIPLE LOG ON!!")
            self.drivers_log_on_off[driver_hash].append(timestamp)

    def update_log_off(self, offline_drivers_hash: Set[str], timestamp):
        """
        update the driver log_off time
        :param offline_drivers_hash: offline drivers' hashcode at this timestamp
        :param timestamp: current timestamp
        """
        self.active_drivers = self.active_drivers.difference(offline_drivers_hash)
        for driver_hash in offline_drivers_hash:
            if len(self.drivers_log_on_off[driver_hash]) != 1:
                print("LOG OFF BEFORE LOG ON!!")
            self.drivers_log_on_off[driver_hash].append(timestamp)
        ratios = [self.drivers_total_income[driver] / (0.1 + timestamp - self.drivers_log_on_off[driver][0])
                  for driver in self.active_drivers]
        ratios.sort()
        if len(ratios) > 0:
            self.median_ratio = ratios[len(ratios) // 2]

    def update_driver_income_after_rejection(self, assignment: List[Dict[str, Any]],
                                             dispatch_observ: List[Dict[str, Any]], index2hash: Dict[int, str]):
        """
        this function update the driver's income.
        Should be called after the rejection process.
        :param assignment: a list of dicts, one dict is <'order_id': xxx, 'driver_id':xxx>
        :param dispatch_observ: the same as agent.matching parameter.
        :param index2hash: driver_id to driver_hash
        :return: None
        """
        if len(dispatch_observ) == 0:
            return
        cur_hour = time.localtime(int(dispatch_observ[0]['timestamp'])).tm_hour
        order_price = {od['order_id']: od['reward_units'] for od in dispatch_observ}
        # for all recorders
        order_info = {od['order_id']: [od['reward_units'],
                                       od['order_driver_distance'],
                                       od['order_start_location'],
                                       od['order_finish_location'],
                                       od['timestamp'],
                                       od['order_finish_timestamp'],
                                       od['pick_up_eta']] for od in dispatch_observ}
        for pair in assignment:
            self.drivers_total_income[index2hash[pair['driver_id']]] += order_price[pair['order_id']]
            self.drivers_income_per_hour[index2hash[pair['driver_id']]][cur_hour] += order_price[pair['order_id']]
            self.drivers_serving_order_info[index2hash[pair['driver_id']]].append(order_info[pair['order_id']])
        return

    def save_logs(self, solpath: str, city: str, date: str, notes=""):
        """
        After one day simulation, output the driver's income and his/her online time into file
        :param solpath: str, the solution path
        :param date: str, the simulation date, eg. 20201129
        :param city: str, the city name, eg. chengdu
        :param notes: str, the parameter setting information
        :return: None
        """
        bad1 = 0
        bad2 = 0
        bad3 = 0
        for driver_hash in self.drivers_log_on_off:
            if len(self.drivers_log_on_off[driver_hash]) == 1:
                bad1 += 1
                continue
            if len(self.drivers_log_on_off[driver_hash]) == 2:
                bad2 += 1
                log_on, log_off = self.drivers_log_on_off[driver_hash]
                self.drivers_online_time[driver_hash] = log_off - log_on
                continue
            if len(self.drivers_log_on_off[driver_hash]) > 2:
                bad3 += 1
                continue
        print("collision:", bad1, bad2, bad3, len(self.drivers_log_on_off))
        driver_perhour_income = dict()
        for driver in self.drivers_income_per_hour:
            driver_perhour_income[driver] = self.drivers_income_per_hour[driver]
        solname = solpath.split('/')[-1]
        pickle.dump(self.drivers_log_on_off, open(solpath + "/" + solname + "_" + city + "_" + date + "logonoff" + notes, "wb"))
        pickle.dump(self.drivers_online_time, open(solpath + "/" + solname + "_" + city + "_" + date + "online_time" + notes, "wb"))
        pickle.dump(self.drivers_total_income, open(solpath + "/" + solname + "_" + city + "_" + date + "total_income" + notes, "wb"))
        pickle.dump(driver_perhour_income, open(solpath + "/" + solname + "_" + city + "_" + date + "perhourincome" + notes, "wb"))
        pickle.dump(self.drivers_serving_order_info, open(solpath + "/" + solname + "_" + city + "_" + date + "order_info" + notes, "wb"))

