import random
import yaml
import networkx as nx
from infrastructure.event_generator import EventGenerator
from infrastructure.node import Node
from math import inf
from infrastructure.infrastructure import Infrastructure, LinkInfo
from infrastructure.physical_infrastructure import PhysicalInfrastructure
from infrastructure.logical_infrastructure import LogicalInfrastructure
from infrastructure.service import Service
from utils import take_decision
from matplotlib import pyplot
import config as general_config


def generate_infrastructure(config_filename: str) -> PhysicalInfrastructure:
    """Generate a Physical infrastructure"""

    # declare NetworkX graph
    graph = nx.Graph()

    num_of_nodes = {}

    config: dict

    with open(config_filename, "r") as file:

        # load config yaml file into a dictionary
        config = yaml.load(file, Loader=yaml.FullLoader)

    # load from config
    for category in ["cloud", "fog", "edge"]:
        num_of_nodes[category] = config["number_of_nodes"][category]

    config_nodes = config["nodes"]

    nodes_by_category: dict[str, list[Node]] = {}

    # choice nodes

    for category in ["cloud", "fog", "edge"]:
        category_nodes = config_nodes[category]
        population = [i for i in range(0, len(category_nodes))]
        weights = [node["probability"] for node in category_nodes]

        chosen_nodes_ids = random.choices(
            population=population, weights=weights, k=num_of_nodes[category]
        )

        nodes_by_category[category] = []

        index = 0
        for node_id in chosen_nodes_ids:
            index += 1
            node = category_nodes[node_id]
            node_id = category + str(index)

            # create Node object
            node_obj = Node(
                node_id=node_id,
                provider=node["provider"],
                sec_caps=node["security_caps"],
                sw_caps=node["software_caps"],
                memory=inf
                if node["hardware_caps"]["memory"] == "inf"
                else int(node["hardware_caps"]["memory"]),
                v_cpu=inf
                if node["hardware_caps"]["v_cpu"] == "inf"
                else int(node["hardware_caps"]["v_cpu"]),
                mhz=inf
                if node["hardware_caps"]["mhz"] == "inf"
                else int(node["hardware_caps"]["mhz"]),
            )
            nodes_by_category[category].append(node_obj)

            # add the node to the graph
            graph.add_node(node_id)

    # connect all nodes of same category
    edges = []
    for category in ["cloud", "fog", "edge"]:

        lower_latency = config["latencies"][category][category]["lower"]
        upper_latency = config["latencies"][category][category]["upper"]

        category_nodes = nodes_by_category[category]
        for index in range(0, len(category_nodes) - 1):
            first = category_nodes[index].id
            for index2 in range(index + 1, len(category_nodes)):
                second = category_nodes[index2].id
                distance = random.randint(lower_latency, upper_latency)
                edge = (first, second, distance)
                edges.append(edge)

    # connect cloud with fog and edge nodes
    cloud_nodes: list[Node] = nodes_by_category["cloud"]

    for category in ["fog", "edge"]:

        category_nodes: list[Node] = nodes_by_category[category]

        latencies = config["latencies"]["cloud"][category]
        edge_probability = latencies["edge_probability"]
        lower_latency = latencies["lower"]
        upper_latency = latencies["upper"]

        for cloud_node in cloud_nodes:
            almost_one_connected = False
            for category_node in category_nodes:
                are_connected = random.random() < edge_probability
                if are_connected:
                    almost_one_connected = True
                    distance = random.randint(lower_latency, upper_latency)
                    edge = (cloud_node.id, category_node.id, distance)
                    edges.append(edge)

            if not almost_one_connected:
                # choose one node to be connected
                chosed_node = random.choice(category_nodes)
                distance = random.randint(lower_latency, upper_latency)
                edge = (cloud_node.id, chosed_node.id, distance)
                edges.append(edge)

    # connect fog with edge nodes
    fog_nodes: list[Node] = nodes_by_category["fog"]

    for category in ["edge"]:

        category_nodes: list[Node] = nodes_by_category[category]

        latencies = config["latencies"]["fog"][category]
        edge_probability = latencies["edge_probability"]
        lower_latency = latencies["lower"]
        upper_latency = latencies["upper"]

        for fog_node in fog_nodes:
            almost_one_connected = False
            for category_node in category_nodes:
                are_connected = random.random() < edge_probability
                if are_connected:
                    almost_one_connected = True
                    distance = random.randint(lower_latency, upper_latency)
                    edge = (fog_node.id, category_node.id, distance)
                    edges.append(edge)

            if not almost_one_connected:
                # choose one node to be connected
                chosed_node = random.choice(category_nodes)
                distance = random.randint(lower_latency, upper_latency)
                edge = (fog_node.id, chosed_node.id, distance)
                edges.append(edge)

    # add edges to the graph
    graph.add_weighted_edges_from(edges)

    # find shortest path lengths between nodes

    network_links = dict(nx.all_pairs_dijkstra(graph))

    # event generators

    event_generators: list[EventGenerator] = []

    min_num_generators = config["event_generators"]["generators"]["min_quantity"]
    max_num_generators = config["event_generators"]["generators"]["max_quantity"]
    num_of_generators = random.randint(min_num_generators, max_num_generators)

    event_on_edge_probability = config["event_generators"]["on_edge_probability"]

    list_of_events = config["event_generators"]["events"]
    generator_basename = config["event_generators"]["generator_base_name"]

    for index in range(1, num_of_generators + 1):

        min_num_events = config["event_generators"]["events_per_generator"][
            "min_quantity"
        ]
        max_num_events = config["event_generators"]["events_per_generator"][
            "max_quantity"
        ]
        num_of_events = random.randint(min_num_events, max_num_events)

        # select the list of events
        chosen_events = random.sample(
            population=list_of_events,
            k=num_of_events,
        )

        # define a probability that each event will be triggered by that device
        events_with_probability = []
        for event in chosen_events:
            event_probability = random.uniform(
                general_config.event_min_probability,
                general_config.event_max_probability,
            )
            events_with_probability.append((event, event_probability))

        # choose the node
        generator_on_edge = take_decision(event_on_edge_probability)
        generator_node_category = "edge" if generator_on_edge else "fog"
        chosen_node = random.choice(nodes_by_category[generator_node_category])
        chosen_node_id = chosen_node.id

        # create the generator
        generator_name = generator_basename + str(index)
        event_generator = EventGenerator(
            generator_name, events_with_probability, chosen_node_id
        )
        event_generators.append(event_generator)

    # services
    services: list[Service] = []
    config_services = config["services"]
    index = 0

    for category in ["cloud", "fog", "edge"]:
        services_by_category = config_services[category]

        for service in services_by_category:
            min_num_service = service["min_quantity"]
            max_num_service = service["max_quantity"]
            quantity = random.randint(min_num_service, max_num_service)
            chosen_nodes = random.sample(
                population=nodes_by_category[category],
                k=quantity,
            )
            for node in chosen_nodes:
                index += 1
                node_id = node.id
                service_id = service["base_name"] + str(index)
                servicex = Service(
                    service_id, service["provider"], service["type"], node_id
                )
                services.append(servicex)

    """
    # plot the graph
    color_map = []
    for node in graph:
        node_str = str(node)
        if node_str.startswith('cloud'):
            color_map.append('orange')
        elif node_str.startswith('fog'):
            color_map.append('yellow')
        else:
            color_map.append('purple')

    pos = nx.spring_layout(graph, scale=20, k=3/numpy.sqrt(graph.order()))
    nx.draw(graph, pos = pos, font_size = 10, node_color = color_map, with_labels = True, node_size=1100)
    pyplot.show()
    """

    nodes_dict: dict[str, Node] = {}

    for category in ["edge", "fog", "cloud"]:
        nodes_by_cat = nodes_by_category[category]
        for node in nodes_by_cat:
            nodes_dict[node.id] = node

    infrastructure = PhysicalInfrastructure(
        nodes_dict, graph, network_links, event_generators, services
    )

    return infrastructure


def dump_infrastructure(infrastructure: Infrastructure, output_filename: str):
    """Dump infrastructure on a given file"""

    lines = []

    nodes_dict: dict = infrastructure.nodes

    # get crashed nodes
    crashed_nodes = infrastructure.crashed_nodes
    # get crashed links
    crashed_links = infrastructure.crashed_links
    # get graph nodes
    graph_nodes = infrastructure.graph.nodes()

    for node_id in graph_nodes:
        node_obj = nodes_dict[node_id]
        # if the node is not available, don't write it
        if node_id not in crashed_nodes:
            node_string = (
                f"node({node_obj.id}, {node_obj.category.value}, {node_obj.provider}, ["
            )
            for sec_cap in node_obj.security_capabilites:
                node_string += sec_cap + ", "
            node_string = node_string.removesuffix(", ")
            node_string += "], ["
            for sw_cap in node_obj.software_capabilites:
                node_string += sw_cap + ", "
            node_string = node_string.removesuffix(", ")
            node_string += f"], ({str(node_obj.memory)}, {str(node_obj.v_cpu)}, {str(node_obj.mhz)}))."
            lines.append(node_string)

    # event generators
    for event_gen in infrastructure.event_generators:
        # if the node where the event generator is placed is not available, don't write it
        if event_gen.source_node not in crashed_nodes:
            string = f"eventGenerator({event_gen.generator_id}, ["
            for event, _ in event_gen.events:
                string += event + ", "
            string = string.removesuffix(", ")
            string += f"], {event_gen.source_node})."
            lines.append(string)

    # services
    for service in infrastructure.services:
        # if the node where the service is deployed is not available, don't write it
        if service.deployed_node not in crashed_nodes:
            string = f"service({service.id}, {service.provider}, {service.type}, {service.deployed_node})."
            lines.append(string)

    # we need these lines in order to declare links as unidirectionals
    lines.append("link(X,X,0).")
    lines.append("link(X,Y,L) :- dif(X,Y), (latency(X,Y,L);latency(Y,X,L)).")

    # latencies

    # get latencies informations
    links = infrastructure.links

    # get nodes as list
    nodes_list: list[str] = list(graph_nodes)

    for index1 in range(0, len(nodes_list)):

        # get first node id
        node1 = nodes_list[index1]

        # don't write a link with a crashed node
        if node1 in crashed_nodes:
            continue

        for index2 in range(index1, len(nodes_list)):

            # get second node id
            node2 = nodes_list[index2]

            # don't write a link with a crashed node
            if node2 in crashed_nodes:
                continue

            # if there is no possibility to connect node1 and node2 latency is inf
            if links[node1][LinkInfo.LATENCY][node2] is inf:
                continue

            # logical crashed links are unreachable (latency is infinity)
            if isinstance(infrastructure, LogicalInfrastructure) and (
                (node1, node2) in crashed_links or (node2, node1) in crashed_links
            ):
                string = f"latency({node1}, {node2}, inf)."
            else:
                # physical links still exist because another path has been found
                string = f"latency({node1}, {node2}, {links[node1][LinkInfo.LATENCY][node2]})."

            lines.append(string)

    # overwrite file
    with open(output_filename, "w") as file:
        for line in lines:
            file.write(line + "\n")
