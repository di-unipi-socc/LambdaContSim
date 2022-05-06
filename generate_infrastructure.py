import sys
import random
import yaml
import networkx as nx
import matplotlib.pyplot as pyplot
from infrastructure.node import Node
from math import inf
import numpy
from logs import init_logger
import os


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


def generate_infrastructure(argv):

    # init the logger
    logger = init_logger()

    # if the user use ask for help, print application usage message
    if ('-h' in argv or '--help' in argv):
        print_usage()
        return 0

    # we should have 0 or at most 4 command line arguments (-c config)
    if len(argv) not in [0, 2, 4]:
        print_usage()
        return 1

    default_config_path = os.path.join(os.curdir, 'infrastructure_config.yaml')
    config_path = default_config_path
    default_output_path = os.path.join(os.curdir, 'test_set', 'infrastructures', 'infrastructure.pl')
    output_path = default_output_path

    # parse command line arguments
    for i in range(0, len(argv) - 1, 2):
        
        option = argv[i]
        option_value = argv[i + 1]
        
        if (option == '-c'):
            # save into config_path variable
            config_path = option_value
        elif (option == '-o'):
            # save into output_path variable
            output_path = option_value
        else:
            # unknown option
            logger.info("Unknown %s option", option)
    
    # check if the config path is a file
    if not os.path.exists(config_path) or not os.path.isfile(config_path):
        logger.error("Config path '%s' not exists or is not a file" % config_path)
        logger.info("Fallback to default config file %s" % default_config_path)
        config_path = default_config_path
        # check that the default config exists
        if not os.path.exists(config_path) or not os.path.isfile(config_path):
            logger.critical("Default config path '%s' not exists or is not a file, exit..." % config_path)
            print_usage()
            return 1
    
    # check if the output path is not a directory
    if not os.path.exists(output_path) or os.path.isdir(output_path):
        logger.error("Output path '%s' not exists or is not a file" % output_path)
        logger.info("Fallback to default output path %s" % default_output_path)
        output_path = default_output_path
    

    num_of_nodes = {}

    config = get_config()

    if config is None:
        # TODO log
        return 1
    
    # load from config
    for category in ['cloud', 'fog', 'edge']:
        num_of_nodes[category] = config['number_of_nodes'][category]
    
    config_nodes = config['nodes']

    nodes : dict[str, list[Node]] = {}

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

        #print(chosen_nodes_ids)

        nodes[category] = []

        index = 0
        for node_id in chosen_nodes_ids:
            index += 1
            node = category_nodes[node_id]
            
            node_obj = Node (
                node_id = category + str(index),
                provider = node['provider'],
                sec_caps = node['security_caps'],
                sw_caps = node['software_caps'],
                memory = inf if node['hardware_caps']['memory'] == 'inf' else int(node['hardware_caps']['memory']),
                v_cpu = inf if node['hardware_caps']['v_cpu'] == 'inf' else int(node['hardware_caps']['v_cpu']),
                mhz = inf if node['hardware_caps']['mhz'] == 'inf' else int(node['hardware_caps']['mhz'])
            )
            nodes[category].append(node_obj)

    graph = nx.Graph()

    # connect all nodes of same category
    edges = []
    for category in ['cloud', 'fog', 'edge']:

        lower_latency = config['latencies'][category][category]['lower']
        upper_latency = config['latencies'][category][category]['upper']
        
        category_nodes = nodes[category]
        for index in range(0, len(category_nodes) - 1):
            first = category_nodes[index].id
            for index2 in range(index+1, len(category_nodes)):
                second = category_nodes[index2].id
                distance = random.randint(lower_latency, upper_latency)
                edge = (first, second, distance)
                edges.append(edge)
    
    # connect cloud with fog and edge nodes
    cloud_nodes : list[Node] = nodes['cloud']

    for category in ['fog', 'edge']:

        category_nodes : list[Node] = nodes[category]

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
    fog_nodes : list[Node] = nodes['fog']

    for category in ['edge']:

        category_nodes : list[Node] = nodes[category]

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
    

    graph.add_weighted_edges_from(edges)
    graph_nodes = list(graph)

    # populate Prolog file
    lines = []

    for category in nodes:
        category_nodes = nodes[category]
        for node in category_nodes:
            
            node_string = f"node({node.id}, {node.provider}, ["
            for sec_cap in node.security_capabilites:
                node_string += sec_cap + ","
            node_string = node_string.removesuffix(",")
            node_string += "], ["
            for sw_cap in node.software_capabilites:
                node_string += sw_cap + ","
            node_string = node_string.removesuffix(",")
            node_string += f"], ({str(node.memory)}, {str(node.v_cpu)}, {str(node.mhz)}))."
            lines.append(node_string)
    
    # event generator TODO sistema
    for node in graph_nodes:
        node = str(node)
        if node.startswith('fog'):
            if random.random() < 0.5:
                lines.append(f'eventGenerator(userDevice, {node}).')

    # offer services
    for node in graph_nodes:
        node = str(node)
        if node.startswith('cloud'):
            if random.random() < 0.5:
                lines.append(f'service(cMaps, cloudProvider, maps, {node}).')
        if node.startswith('fog'):
            if random.random() < 0.5:
                lines.append(f'service(myUserDb, appOp, userDB, {node}).')
            if random.random() < 0.5:
                lines.append(f'service(gp, pa, checkGp, {node}).')
            if random.random() < 0.5:
                lines.append(f'service(rules, pa, checkRules, {node}).')
        if node.startswith('edge'):
            if random.random() < 0.5:
                lines.append(f'service(openM, openS, maps, {node}).')

    lines.append('link(X,X,0).')
    lines.append('link(X,Y,L) :- dif(X,Y), (latency(X,Y,L);latency(Y,X,L)).')

    # latencies
    results = dict(nx.all_pairs_dijkstra_path_length(graph))
    for index in range(0, len(graph_nodes) - 1):
        node1 = graph_nodes[index]
        for index2 in range(index + 1, len(graph_nodes)):
            node2 = graph_nodes[index2]
            string = f'latency({node1}, {node2}, {results[node1][node2]}).'
            lines.append(string)
    

    # overwrite file
    with open(output_path, 'w') as f:
        for line in lines:
            f.write(line+'\n')

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


if __name__ == "__main__":
    generate_infrastructure(sys.argv[1:])