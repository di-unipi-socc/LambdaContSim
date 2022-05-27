from math import isinf
from enum import Enum

# class which represents an infrastracture node

# a node can be edge, fog or cloud
class NodeCategory(Enum):
    EDGE = "edge"
    FOG = "fog"
    CLOUD = "cloud"

    @staticmethod
    def from_string(category_str : str):
        
        match category_str:
            case 'cloud':
                return NodeCategory.CLOUD
            case 'fog':
                return NodeCategory.FOG
            case 'edge':
                return NodeCategory.EDGE
            case _:
                return None
    
    @staticmethod
    def to_string(category_str : str):
        
        match category_str:
            case 'cloud':
                return NodeCategory.CLOUD
            case 'fog':
                return NodeCategory.FOG
            case 'edge':
                return NodeCategory.EDGE
            case _:
                return None


class Node :
    id : str = '' # node unique identifier e.g. IP address
    category : NodeCategory # node category (edge, fog, cloud)
    provider : str = '' # node's owner
    security_capabilites : list[str] = [] # list of security caps
    software_capabilites : list[str] = [] # list of software caps
    # hardware capabities
    max_memory : int = 0
    memory: int = 0
    max_v_cpu : int = 0
    v_cpu: int = 0
    mhz: int = 0

    def __init__(
        self, node_id : str,
        provider : str,
        sec_caps : list[str],
        sw_caps : list[str],
        memory: int,
        v_cpu : int,
        mhz : int,
        category : NodeCategory = None
    ):
        self.id = node_id
        # if not given, determine ourselves the node category
        self.category = category if category is not None else self._get_node_category()
        self.provider = provider
        self.security_capabilites = sec_caps
        self.software_capabilites = sw_caps
        self.memory = memory
        self.max_memory = memory
        self.v_cpu = v_cpu
        self.max_v_cpu = v_cpu
        self.mhz = mhz


    def take_resources(self, memory : int, v_cpu : int) :
        if not isinf(self.memory):
            self.memory -= memory
        if not isinf(self.v_cpu):
            self.v_cpu -= v_cpu


    def release_resources(self, memory: int, v_cpu: int):
        if not isinf(self.memory):
            self.memory += memory
        if not isinf(self.v_cpu):
            self.v_cpu += v_cpu
    

    def get_load(self):
        '''
        Returns the percentage load of the node.
        It is a value between 0 and 1
        '''
        memory_percentage = 1 if isinf(self.memory) else 1 - self.memory/self.max_memory
        v_cpu_percentage = 1 if isinf(self.v_cpu) else 1 - self.v_cpu/self.max_v_cpu
        
        # cpus has the major role in load calculation
        return v_cpu_percentage * 0.7 + memory_percentage * 0.3
    

    def get_energy(self):
        '''
        Returns the node's consuption at that time.
        Value is expressed in KWh
        '''
        load = self.get_load()
        # load is under 50%
        if load < 0.5:
            return 0.2
        # load over 50%
        return 0.4
        
    

    # internal function to determine the node category
    def _get_node_category(self) -> NodeCategory:
        # actually, we determine the node category by viewing its name
        # a cloud node contains 'cloud' into its name, and so on...
        
        if self.id.find("cloud") != -1:
            return NodeCategory.CLOUD
        
        elif self.id.find("fog") != -1:
            return NodeCategory.FOG
        
        # fallback is EDGE
        return NodeCategory.EDGE