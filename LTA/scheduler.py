import math
from typing import Dict, List, Any, Tuple
from grid import Grid
from matcher import Matcher
from global_var import SPEED
import time


class Scheduler:
    def __init__(self, gamma: float):
        self.gamma = gamma
        self.grid_ids = Grid.get_grid_ids()

    def reposition(self, matcher, repo_observ) -> List[Dict[str, str]]:
        if len(repo_observ['driver_info']) == 0:
            return []
        timestamp, day_of_week, drivers = Scheduler.parse_repo(repo_observ)
        grid_ids = self.grid_ids
        reposition = []  # type: List[Dict[str, str]]
        for driver_id, current_grid_id in drivers:
            best_grid_id, best_value = current_grid_id, -100
            current_value = matcher.get_grid_value(current_grid_id)
            for grid_id in grid_ids:
                duration = Grid.mahattan_distance(current_grid_id, grid_id) / SPEED
                discount = math.pow(0.999, duration)
                proposed_value = matcher.get_grid_value(grid_id)
                incremental_value = discount * proposed_value - current_value
                if incremental_value > best_value:
                    best_grid_id, best_value = grid_id, incremental_value
            reposition.append(dict(driver_id=driver_id, destination=best_grid_id))
        return reposition

    @staticmethod
    def parse_repo(repo_observ):
        timestamp = repo_observ['timestamp']  # type: int
        cur_local = time.localtime(timestamp)
        cur_time = cur_local.tm_hour * 3600 + cur_local.tm_min * 60 + cur_local.tm_sec - 4 * 3600
        day_of_week = repo_observ['day_of_week']  # type: int
        drivers = [(driver['driver_id'], driver['grid_id'])
                    for driver in repo_observ['driver_info']]
        return cur_time, day_of_week, drivers
