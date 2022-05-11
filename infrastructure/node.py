from math import isinf
from enum import Enum

# class which represents an infrastracture node

# a node can be edge, fog or cloud
class NodeCategory(Enum):
    EDGE = 0
    FOG = 1
    CLOUD = 2

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


class Node :
    id : str = '' # node unique identifier e.g. IP address
    category : NodeCategory # node category (edge, fog, cloud)
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
        self.category = self._get_node_category() # determine ourselves the node category
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


    def release_resources(self, memory: int, v_cpu: int):
        if not isinf(self.memory):
            self.memory += memory
        if not isinf(self.v_cpu):
            self.v_cpu += v_cpu
    

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