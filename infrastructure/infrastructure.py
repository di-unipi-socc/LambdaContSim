from infrastructure.node import Node
import random

class Infrastructure :
    nodes : dict[str, Node]
    latencies : dict[str, dict[str, ( int, bool )]]
    other_data : list

    # crashed nodes
    crashed_nodes = []

    # link crashed
    crashed_links = []

    def __init__(self, nodes, latencies, other_data):
        self.nodes = nodes
        self.latencies = latencies
        self.other_data = other_data


    def simulate_node_crash(self) :
        keys = self.nodes.keys()
        
        # get the list of active nodes
        active_nodes = []
        for key in keys:
            if self.nodes.get(key).available:
                active_nodes.append(key)
        
        # if there is no active nodes, then no one can crash
        if len(active_nodes) == 0:
            return None
        
        # choice a random node to kill
        node_to_kill = random.choice(active_nodes)
        self.nodes.get(node_to_kill).available = False
        
        # save into the list of crashed nodes
        self.crashed_nodes.append(node_to_kill)
        
        return node_to_kill


    def simulate_node_resurrection(self, node_to_exclude = None) :

        # remove the node so it can't be chosen for resurrection
        if node_to_exclude is not None:
            self.crashed_nodes.remove(node_to_exclude)

        # if there is no crashed nodes, then no one can resurrect
        if len(self.crashed_nodes) == 0:   
            return None

        # choose a node to resurrect
        node_to_resurrect = random.choice(self.crashed_nodes)
        self.nodes.get(node_to_resurrect).available = True
        
        # remove from the list of crashed nodes
        self.crashed_nodes.remove(node_to_resurrect)

        # re-insert the excluded node
        if node_to_exclude is not None:
            self.crashed_nodes.append(node_to_exclude)
        
        return node_to_resurrect


    def simulate_link_crash(self):
        # get active nodes
        keys = self.nodes.keys()
        active_nodes = []
        for key in keys:
            if self.nodes.get(key).available:
                active_nodes.append(key)
        
        # if there aren't then we can't make a link crash
        if len(active_nodes) == 0:
            return None, None
        
        # until we found an active link
        while True:
            
            # choice a random node
            first_node = random.choice(active_nodes)
            second_keys = self.latencies.get(first_node).keys()
            second_active_nodes = []
            for key in second_keys:
                if self.nodes.get(key).available:
                    second_active_nodes.append(key)
            if len(second_active_nodes) == 0:
                return None, None
            
            second_node = random.choice(second_active_nodes)
            
            # make the link unavailable
            self.latencies.get(first_node).get(second_node)['available'] = False
            
            # save into the list of crashed links
            self.crashed_links.append({'first' : first_node, 'second' : second_node})
            
            return first_node, second_node


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
        self.latencies.get(link['first']).get(link['second'])['available'] = True
        
        # remove from the list of crashed links
        self.crashed_links.remove(link)

        # re-insert the excluded link
        if link_to_exclude is not None:
            self.crashed_links.append(link_to_exclude)
        
        
        return link['first'], link['second']
        