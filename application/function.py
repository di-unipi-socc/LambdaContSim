# class which design a single function of an application

class PlacedFunction:
    id = "" # function unique identifier
    node_id = "" # node where the function has been deployed
    software_requirements: list[str] = []  # list of software reqs
    # hardware reqs
    memory: int = 0
    v_cpu: int = 0
    mhz: int = 0
    time_of_execution = 1 # number of epochs TODO parameterize
    # service_reqs

    def __init__(self, function_id: str, node_id : str, sw_reqs: list[str], memory: int, v_cpu: int, mhz: int):
        self.id = function_id
        self.node_id = node_id
        self.software_requirements = sw_reqs
        self.memory = memory
        self.v_cpu = v_cpu
        self.mhz = mhz
