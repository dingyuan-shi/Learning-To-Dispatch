from typing import Any, List, Dict
from matcher import Matcher
from scheduler import Scheduler
from global_var import alpha, gamma1, gamma2
from recorder import Recorder


class Agent(Recorder):
    def __init__(self):
        super().__init__()
        self.matcher = Matcher(alpha, gamma1)
        self.scheduler = Scheduler(gamma2)

    def dispatch(self, dispatch_observ: List[Dict[str, Any]], index2hash=None) -> List[Dict[str, str]]:
        return self.matcher.dispatch(dispatch_observ, index2hash)

    def reposition(self, repo_observ: Dict[str, Any]) -> List[Dict[str, str]]:
        return self.scheduler.reposition(self.matcher, repo_observ)
        # return []
