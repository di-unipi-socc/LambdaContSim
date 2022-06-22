from enum import IntEnum
import itertools
import copy

from application.placed_function import PlacedFunction


class ApplicationState(IntEnum):
    PLACED = 0
    RUNNING = 1
    COMPLETED = 2
    CANCELED = 3

    def __str__(self):
        return self.name


class Application:

    # unique id iterator variable
    id_iterator = itertools.count()

    id: str
    name: str
    filename: str
    orchestration_id: str
    state: ApplicationState
    placement_epoch: int
    original_chain: dict[str, list]
    chain: dict[str, list]
    placement: dict[str, PlacedFunction]
    infrastructure_nodes: dict
    function_processes: dict

    def __init__(
        self,
        app_name: str,
        filename: str,
        orchestration_id: str,
        placement_epoch: int,
        chain: dict,
        placement: dict,
        infrastructure: dict,
    ):
        self.id = app_name + "-" + str(next(Application.id_iterator))
        self.name = app_name
        self.filename = filename
        self.orchestration_id = orchestration_id
        self.state = ApplicationState.PLACED
        self.placement_epoch = placement_epoch
        self.original_chain = copy.deepcopy(chain)
        self.chain = copy.deepcopy(chain)
        self.placement = placement
        self.infrastructure_nodes = infrastructure
        self.function_processes = {}
