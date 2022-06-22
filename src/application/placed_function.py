from enum import IntEnum

# class which design a single function of an application

# Possible states of a function
class FunctionState(IntEnum):
    WAITING = 0             # function is waiting to be executed
    RUNNING = 1             # function is running
    COMPLETED = 2           # function finished its execution
    CANCELED = 3            # function has been canceled
    BRANCH_NOT_TAKEN = 4    # function has been canceled because it was part of a discarded if branch
    INTERRUPTED = 5         # function has been interrupted

    def __str__(self):
        return self.name


class PlacedFunction:
    id: str  # function unique identifier
    node_id: str  # node where the function has been deployed
    software_requirements: list[str]  # list of software reqs
    # hardware reqs
    memory: int = 0
    v_cpu: int = 0
    mhz: int = 0
    # list of linked services
    linked_services: list[str]
    # is a guard of a conditional state?
    is_guard: bool = False
    # state of the function
    state: FunctionState
    # list of node where are placed the functions which it is depending
    previous_nodes: list[str]

    def __init__(
        self,
        function_id: str,
        node_id: str,
        sw_reqs: list[str],
        memory: int,
        v_cpu: int,
        mhz: int,
        linked_services: list[str],
        is_guard: bool,
    ):
        self.id = function_id
        self.node_id = node_id
        self.software_requirements = sw_reqs
        self.memory = memory
        self.v_cpu = v_cpu
        self.mhz = mhz
        self.linked_services = linked_services
        self.is_guard = is_guard
        self.state = FunctionState.WAITING
        self.previous_nodes = []
