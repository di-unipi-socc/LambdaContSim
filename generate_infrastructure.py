import sys
import random
import yaml
import networkx as nx
from infrastructure.event_generator import EventGenerator
from infrastructure.node import Node
from math import inf
import numpy
from infrastructure.physical_infrastructure import PhysicalInfrastructure
from infrastructure.service import Service
import os
from utils import take_decision


def print_usage():
    ''' Print application usage message'''
    print('Usage: %s [<options>]' % os.path.basename(sys.argv[0]))
    print('       %s [-h|--help] to show this help message' % os.path.basename(sys.argv[0]))
    print('\nOptions:')
    print('-c <config file> application config (default infrastructure_config.yaml)')
    print('-o <output file> desired output file (default inside test_set/infrastructures/infrastructure.pl)')


def get_config():
    
    with open("infrastructure_config.yaml", 'r') as f:
        
        # load config yaml file into a dictionary
        config = yaml.load(f, Loader=yaml.FullLoader)

        return config
    
    return None


def generate_infrastructure():

    # declare NetworkX graph
    graph = nx.Graph()

    num_of_nodes = {}

    config = get_config()
    
    # load from config
    for category in ['cloud', 'fog', 'edge']:
        num_of_nodes[category] = config['number_of_nodes'][category]
    
    config_nodes = config['nodes']

    nodes_by_category : dict[str, list[Node]] = {}

    # choice nodes

    for category in ['cloud', 'fog', 'edge']:
        category_nodes = config_nodes[category]
        population = [i for i in range(0, len(category_nodes))]
        weights = [node['probability'] for node in category_nodes]

        chosen_nodes_ids = random.choices(
            population = population,
            weights = weights,
            k = num_of_nodes[category]
        )

        nodes_by_category[category] = []

        index = 0
        for node_id in chosen_nodes_ids:
            index += 1
            node = category_nodes[node_id]
            node_id = category + str(index)
            
            # create Node object
            node_obj = Node (
                node_id = node_id,
                provider = node['provider'],
                sec_caps = node['security_caps'],
                sw_caps = node['software_caps'],
                memory = inf if node['hardware_caps']['memory'] == 'inf' else int(node['hardware_caps']['memory']),
                v_cpu = inf if node['hardware_caps']['v_cpu'] == 'inf' else int(node['hardware_caps']['v_cpu']),
                mhz = inf if node['hardware_caps']['mhz'] == 'inf' else int(node['hardware_caps']['mhz'])
            )
            nodes_by_category[category].append(node_obj)

            # add the node to the graph
            graph.add_node(node_id, available = True)

    # connect all nodes of same category
    edges = []
    for category in ['cloud', 'fog', 'edge']:

        lower_latency = config['latencies'][category][category]['lower']
        upper_latency = config['latencies'][category][category]['upper']
        
        category_nodes = nodes_by_category[category]
        for index in range(0, len(category_nodes) - 1):
            first = category_nodes[index].id
            for index2 in range(index+1, len(category_nodes)):
                second = category_nodes[index2].id
                distance = random.randint(lower_latency, upper_latency)
                edge = (first, second, distance)
                edges.append(edge)
    
    # connect cloud with fog and edge nodes
    cloud_nodes : list[Node] = nodes_by_category['cloud']

    for category in ['fog', 'edge']:

        category_nodes : list[Node] = nodes_by_category[category]

        latencies = config['latencies']['cloud'][category]
        edge_probability = latencies['edge_probability']
        lower_latency = latencies['lower']
        upper_latency = latencies['upper']
        

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
    fog_nodes : list[Node] = nodes_by_category['fog']

    for category in ['edge']:

        category_nodes : list[Node] = nodes_by_category[category]

        latencies = config['latencies']['fog'][category]
        edge_probability = latencies['edge_probability']
        lower_latency = latencies['lower']
        upper_latency = latencies['upper']
        

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
    graph.add_weighted_edges_from(edges, available = True)
    
    # find shortest path lengths between nodes
    network_latencies = dict(nx.all_pairs_dijkstra_path_length(graph))
    
    graph_nodes : list[str] = list(graph)

    # event generators
    
    event_generators : list[EventGenerator] = []
    
    min_num_generators = config['event_generators']['generators']['min_quantity']
    max_num_generators = config['event_generators']['generators']['max_quantity']
    num_of_generators = random.randint(min_num_generators, max_num_generators)
    
    event_on_edge_probability = config['event_generators']['on_edge_probability']
    
    list_of_events = config['event_generators']['events']
    generator_basename = config['event_generators']['generator_base_name']
    
    for index in range(1, num_of_generators + 1):
        
        min_num_events = config['event_generators']['events_per_generator']['min_quantity']
        max_num_events = config['event_generators']['events_per_generator']['max_quantity']
        num_of_events = random.randint(min_num_events, max_num_events)
        
        # select the list of events
        chosen_events = random.sample(
            population = list_of_events,
            k = num_of_events,
        )
        
        # choose the node
        generator_on_edge = take_decision(event_on_edge_probability)
        generator_node_category = 'edge' if generator_on_edge else 'fog'
        chosen_node = random.choice(nodes_by_category[generator_node_category])
        chosen_node_id = chosen_node.id
        
        # create the generator
        generator_name = generator_basename + str(index)
        event_generator = EventGenerator(generator_name, chosen_events, chosen_node_id)
        event_generators.append(event_generator)

    # services
    services : list[Service] = []
    config_services = config['services']
    index = 0

    # TODO limita numero di servizi
    for node_id in graph_nodes:
        if index > 10:
            break
        # TODO remove category part
        category = "edge"
        if node_id.startswith("cloud"):
            category = "cloud"
        elif node_id.startswith("fog"):
            category = "fog"
        
        services_by_category = config_services[category]

        for service in services_by_category:
            index += 1
            service_id = service['base_name'] + str(index)
            service = Service(service_id, service['provider'], service['type'], node_id)
            services.append(service)
    
    for node_id in graph_nodes:
        if index > 15:
            break
        # TODO remove category part
        category = "edge"
        if node_id.startswith("cloud"):
            category = "cloud"
        elif node_id.startswith("fog"):
            category = "fog"
        
        if category != 'edge':
            continue
        
        services_by_category = config_services[category]

        for service in services_by_category:
            index += 1
            service_id = service['base_name'] + str(index)
            service = Service(service_id, service['provider'], service['type'], node_id)
            services.append(service)


    # plot the graph
    '''
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
    '''

    nodes_dict : dict[str, Node] = {}

    for category in ['edge', 'fog', 'cloud']:
        nodes_by_cat = nodes_by_category[category]
        for node in nodes_by_cat:
            nodes_dict[node.id] = node

    infrastructure = PhysicalInfrastructure(nodes_dict, graph, network_latencies, event_generators, services)

    return infrastructure


if __name__ == "__main__":
    generate_infrastructure(sys.argv[1:])