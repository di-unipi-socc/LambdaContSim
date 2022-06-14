from abc import ABC
from infrastructure.node import Node, NodeCategory
from infrastructure.event_generator import EventGenerator
from infrastructure.service import Service
import networkx as nx
import random

class Infrastructure(ABC):
    nodes : dict[str, Node]
    graph : nx.Graph
    latencies : dict[str, dict[str, int]]
    event_generators : list[EventGenerator]
    services : list[Service]

    # crashed nodes
    crashed_nodes = []

    # link crashed
    crashed_links = []

    def simulate_node_crash(self, category : NodeCategory) :
        
        # get the list of active nodes
        graph_nodes = self.graph.nodes()
        active_nodes = []
        for node_id in graph_nodes:
            node_obj = self.nodes[node_id]
            if node_obj.category == category and node_id not in self.crashed_nodes:
                active_nodes.append(node_id)
        
        # if there is no active nodes, then no one can crash
        if len(active_nodes) == 0:
            return None
        
        # choice a random node to kill
        node_to_kill = random.choice(active_nodes)
        
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

        # re-insert the excluded node
        if node_to_exclude is not None:
            self.crashed_nodes.append(node_to_exclude)

        # if there is no crashed nodes, then no one can resurrect
        if len(category_crashed_nodes) == 0:   
            return None

        # choose a node to resurrect
        node_to_resurrect = random.choice(category_crashed_nodes)
        
        # remove from the list of crashed nodes
        self.crashed_nodes.remove(node_to_resurrect)
        
        return node_to_resurrect


    def simulate_link_crash(self):

        # get the list of active links
        active_links = [(node1, node2) for node1, node2 in self.graph.edges() if (node1, node2) not in self.crashed_links]

        # if there aren't then we can't make no one link crash
        if len(active_links) == 0:
            return None, None

        # randomly choice a link to kill
        node1, node2 = random.choice(active_links)
        
        # save into the list of crashed links
        self.crashed_links.append((node1, node2))
        
        return node1, node2


    def simulate_link_resurrection(self, link_to_exclude : tuple = None):

        # remove the link so it can't be chosen for resurrection
        if link_to_exclude is not None:
            self.crashed_links.remove(link_to_exclude)

        # if there are no crashed links, then we can't resurrect one
        if len(self.crashed_links) == 0:
            # re-insert the excluded link
            if link_to_exclude is not None:
                self.crashed_links.append(link_to_exclude)
            return None, None
        
        # choice the link to resurrect
        node1, node2 = random.choice(self.crashed_links)
        
        # remove from the list of crashed links
        self.crashed_links.remove((node1, node2))

        # re-insert the excluded link
        if link_to_exclude is not None:
            self.crashed_links.append(link_to_exclude)
        

        return node1, node2
    
