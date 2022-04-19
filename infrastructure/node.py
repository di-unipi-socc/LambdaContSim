from math import inf, isinf

# class which represents an infrastracture node

class Node :
    id : str = '' # node unique identifier e.g. IP address
    provider : str = '' # node's owner
    security_capabilites : list[str] = [] # list of security caps
    software_capabilites : list[str] = [] # list of software caps
    # hardware capabities
    memory: int = 0
    v_cpu: int = 0
    mhz: int = 0

    # runtime fields
    available: bool = True

    def __init__(
        self, node_id : str,
        provider : str,
        sec_caps : list[str],
        sw_caps : list[str],
        memory: int,
        v_cpu : int,
        mhz : int
    ):
        self.id = node_id
        self.provider = provider
        self.security_capabilites = sec_caps
        self.software_capabilites = sw_caps
        self.memory = memory
        self.v_cpu = v_cpu
        self.mhz = mhz

    def take_resources(self, memory : int, v_cpu : int) :
        if not isinf(self.memory):
            self.memory -= memory
        if not isinf(self.v_cpu):
            self.v_cpu -= v_cpu

    def give_back_resources(self, memory: int, v_cpu: int):
        if not isinf(self.memory):
            self.memory += memory
        if not isinf(self.v_cpu):
            self.v_cpu += v_cpu