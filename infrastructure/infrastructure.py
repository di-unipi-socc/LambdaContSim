from infrastructure.event_generator import EventGenerator
from infrastructure.node import Node, NodeCategory
import random
import networkx as nx

from infrastructure.service import Service

class Infrastructure :
    nodes : dict[str, Node]
    original_graph : nx.Graph
    graph : nx.Graph
    latencies : dict[str, dict[str, int]]
    event_generators : list[EventGenerator]
    services : list[Service]

    # crashed nodes
    crashed_nodes = []

    # link crashed
    crashed_links = []

    def __init__(self, nodes, graph, latencies, event_generators, services):
        self.nodes = nodes
        self.original_graph = graph
        self.graph = graph
        self.latencies = latencies
        self.event_generators = event_generators
        self.services = services


    def simulate_node_crash(self, category : NodeCategory) :
        
        # get the list of active nodes
        graph_nodes = self.graph.nodes(data=True)
        active_nodes = []
        for (node_id, node_data) in graph_nodes:
            node_obj = self.nodes[node_id]
            if node_obj.category == category and node_data['available']:
                active_nodes.append(node_id)
        
        # if there is no active nodes, then no one can crash
        if len(active_nodes) == 0:
            return None
        
        # choice a random node to kill
        node_to_kill = random.choice(active_nodes)
        nx.set_node_attributes(self.graph, {node_id: { 'available' : False }})
        
        # save into the list of crashed nodes
        self.crashed_nodes.append(node_to_kill)
        
        return node_to_kill


    def simulate_node_resurrection(self, category : NodeCategory, node_to_exclude = None) :

        # remove the node so it can't be chosen for resurrection
        if node_to_exclude is not None:
            self.crashed_nodes.remove(node_to_exclude)
        
        # get only nodes with the defined category
        category_crashed_nodes = []
        for node_id in self.crashed_nodes:
            node_obj = self.nodes.get(node_id)
            if node_obj.category == category:
                category_crashed_nodes.append(node_id)

        # if there is no crashed nodes, then no one can resurrect
        if len(category_crashed_nodes) == 0:   
            return None

        # choose a node to resurrect
        node_to_resurrect = random.choice(category_crashed_nodes)
        nx.set_node_attributes(self.graph, {node_id: { 'available' : True }})
        
        # remove from the list of crashed nodes
        self.crashed_nodes.remove(node_to_resurrect)

        # re-insert the excluded node
        if node_to_exclude is not None:
            self.crashed_nodes.append(node_to_exclude)
        
        return node_to_resurrect


    def simulate_link_crash(self):

        # get the list of active links
        active_links = [(node1, node2) for node1, node2, data in self.graph.edges(data=True) if data['available'] == True]

        # if there aren't then we can't make no one link crash
        if len(active_links) == 0:
            return None, None

        # randomly choice a link to kill
        node1, node2 = random.choice(active_links)

        # make the link unavailable
        nx.set_edge_attributes(self.graph, { (node1, node2) : { 'available' : False }})
        
        # save into the list of crashed links
        self.crashed_links.append({'first' : node1, 'second' : node2})
        
        return node1, node2


    def simulate_link_resurrection(self, link_to_exclude = None):

        # remove the link so it can't be chosen for resurrection
        if link_to_exclude is not None:
            self.crashed_links.remove(link_to_exclude)

        # if there are no crashed links, then we can't resurrect one
        if len(self.crashed_links) == 0:
            return None, None
        
        # choice the link to resurrect
        link = random.choice(self.crashed_links)
        
        # make it available
        nx.set_edge_attributes(self.graph, { (link['first'], link['second']) : { 'available' : False }})
        
        # remove from the list of crashed links
        self.crashed_links.remove(link)

        # re-insert the excluded link
        if link_to_exclude is not None:
            self.crashed_links.append(link_to_exclude)
        
        
        return link['first'], link['second']
    

    def update(self) :
        filtered_nodes = [node for node, node_data in self.original_graph.nodes(data=True)
                   if node_data['available'] == True]
        
        new_graph : nx.Graph = self.original_graph.subgraph(filtered_nodes)
        print(new_graph)

        self.graph = new_graph
        self.latencies = dict(nx.all_pairs_dijkstra_path_length(self.graph))