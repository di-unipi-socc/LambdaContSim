from infrastructure.infrastructure import Infrastructure
from infrastructure.node import Node, NodeCategory
from infrastructure.event_generator import EventGenerator
from infrastructure.service import Service
import re
from math import inf
import networkx as nx
import config
import random


class LogicalInfrastructure(Infrastructure):

    def __init__(self, nodes, graph, links, event_generators, services):
        self.nodes = nodes
        self.graph = graph
        self.links = links
        self.event_generators = event_generators
        self.services = services

    @staticmethod
    def loads(infrastructure_filename: str):
        """Load the infrastructure from a file"""

        # declare NetworkX graph
        graph = nx.Graph()

        nodes: dict[str, (Node, bool)] = {}
        edges = []
        event_generators: dict[str, EventGenerator] = {}
        services: list[Service] = []

        # Prolog lines pattern
        node_pattern = r"^node\(([^,]+),([^,]+),([^,]+),(\[.*?\]),(\[.*?\]),\(([^,]+),([^,]+),([^\)]+)\)\)\.*"
        latency_pattern = r"^latency\(([^,]+),([^,]+),([^,]+)\)\.*"
        event_pattern = r"^eventGenerator\(([^,]+),(\[.*?\]),([^,]+)\)\.*"
        service_pattern = r"^service\(([^,]+),([^,]+),([^,]+),([^,]+)\)\.*"

        with open(infrastructure_filename, "r") as file:

            lines = file.readlines()

            for line in lines:
                if line.startswith("node"):
                    line = line.replace(" ", "")
                    # print(line)
                    match = re.match(node_pattern, line).groups()

                    node_id = match[0]
                    category = NodeCategory.from_string(match[1])
                    provider = match[2]
                    security_caps = (
                        match[3].replace("[", "").replace("]", "").split(",")
                    )
                    software_caps = (
                        match[4].replace("[", "").replace("]", "").split(",")
                    )
                    memory = inf if match[5] == "inf" else int(match[5])
                    v_cpu = inf if match[6] == "inf" else int(match[6])
                    mhz = inf if match[7] == "inf" else int(match[7])

                    node_obj = Node(
                        node_id=node_id,
                        category=category,
                        provider=provider,
                        sec_caps=security_caps,
                        sw_caps=software_caps,
                        memory=memory,
                        v_cpu=v_cpu,
                        mhz=mhz,
                    )
                    # add the node to the dict
                    nodes[node_id] = node_obj

                    # add the node to the graph
                    graph.add_node(node_id)

                elif line.startswith("latency"):
                    line = line.replace(" ", "")
                    match = re.match(latency_pattern, line).groups()

                    first_node = match[0]
                    second_node = match[1]
                    distance = int(match[2])

                    # add the edge to the list
                    edge = (first_node, second_node, distance)
                    edges.append(edge)

                elif line.startswith("event"):
                    line = line.replace(" ", "")
                    match = re.match(event_pattern, line).groups()

                    generator_id = match[0]
                    events = match[1].replace("[", "").replace("]", "").split(",")

                    # define a probability that each event will be triggered by that device
                    events_with_probability = []
                    for event in events:
                        event_probability = random.uniform(
                            config.event_min_probability, config.event_max_probability
                        )
                        events_with_probability.append((event, event_probability))

                    node_id = match[2]

                    # instance object
                    event_gen = EventGenerator(
                        id=generator_id,
                        events=events_with_probability,
                        source_node=node_id,
                    )
                    # append to the list
                    event_generators[generator_id] = event_gen

                elif line.startswith("service"):
                    line = line.replace(" ", "")
                    match = re.match(service_pattern, line).groups()

                    service_id = match[0]
                    provider = match[1]
                    service_type = match[2]
                    deployed_node = match[3]

                    # instance object
                    service = Service(
                        id=service_id,
                        provider=provider,
                        type=service_type,
                        deployed_node=deployed_node,
                    )
                    # append to the list
                    services.append(service)

            # add edges to the graph
            graph.add_weighted_edges_from(edges)

            # find shortest path lengths between nodes
            links = dict(nx.all_pairs_dijkstra(graph))

            # instance logical infrastructure
            infrastructure = LogicalInfrastructure(
                nodes=nodes,
                graph=graph,
                links=links,
                event_generators=event_generators,
                services=services,
            )

            return infrastructure
