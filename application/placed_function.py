from enum import Enum

# class which design a single function of an application

# Possible states of a function
class FunctionState(Enum):
    WAITING = 0
    RUNNING = 1
    COMPLETED = 2
    CANCELED = 3


class PlacedFunction:
    id = "" # function unique identifier
    node_id = "" # node where the function has been deployed
    software_requirements: list[str] = []  # list of software reqs
    # hardware reqs
    memory : int = 0
    v_cpu : int = 0
    mhz : int = 0
    # is a guard of a conditional state?
    is_guard : bool = False
    # state of the function
    state : FunctionState = FunctionState.WAITING

    def __init__(self, function_id: str, node_id : str, sw_reqs: list[str], memory: int, v_cpu: int, mhz: int, is_guard : bool):
        self.id = function_id
        self.node_id = node_id
        self.software_requirements = sw_reqs
        self.memory = memory
        self.v_cpu = v_cpu
        self.mhz = mhz
        self.is_guard = is_guard
