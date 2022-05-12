from re import S


class Service:
    id : str
    provider : str
    type : str
    deployed_node : str

    def __init__(self, id, provider, type, deployed_node) :
        self.id = id
        self.provider = provider
        self.type = type
        self.deployed_node = deployed_node