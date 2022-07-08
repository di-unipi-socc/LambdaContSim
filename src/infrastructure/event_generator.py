class EventGenerator:
    generator_id: str
    events: list[(str, float)]
    source_node: str

    def __init__(self, id : str, events : list[(str, float)], source_node : str):
        self.generator_id = id
        self.events = events
        self.source_node = source_node
