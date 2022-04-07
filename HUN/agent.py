from recorder import Recorder
from typing import Dict, List, Set, Tuple, Any
import sys
if sys.platform == 'darwin':
    from model.KM import find_max_match
else:
    from KM import find_max_match


class Agent(Recorder):
    def __init__(self):
        super().__init__()

    def dispatch(self, dispatch_observ: List[Dict[str, Any]], index2hash) -> List[Dict[str, str]]:
        if len(dispatch_observ) == 0:
            return []
        values = [(each['driver_id'], each['order_id'], each['reward_units']) for each in dispatch_observ]
        val, dispatch_tuple = find_max_match(x_y_values=values, split=False, quick=False)
        return [dict(driver_id=each[0], order_id=each[1]) for each in dispatch_tuple]

    def reposition(self, repo_observ: Dict[str, Any]) -> List[Dict[str, str]]:
        return []
