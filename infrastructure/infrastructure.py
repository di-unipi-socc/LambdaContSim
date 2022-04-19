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

    def simulate_node_crash(self):
        keys = self.nodes.keys()
        active_nodes = []
        for key in keys:
            if self.nodes.get(key).available:
                active_nodes.append(key)
        # choice a random node to kill
        node_to_kill = random.choice(active_nodes)
        self.nodes.get(node_to_kill).available = False
        # save into the list of crashed nodes
        self.crashed_nodes.append(node_to_kill)
        print("Node %s crashed" % node_to_kill)
    
    def simulate_link_crash(self):
        keys = self.nodes.keys()
        active_nodes = []
        for key in keys:
            if self.nodes.get(key).available:
                active_nodes.append(key)
        if len(active_nodes) == 0:
            return
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
                break
            second_node = random.choice(second_active_nodes)
            self.latencies.get(first_node).get(second_node)['available'] = False
            # save into the list of crashed links
            self.crashed_links.append({'first' : first_node, 'second' : second_node})
            print("Link %s <-> %s crashed" % (first_node, second_node))
            break

    def simulate_node_resurrection(self):
        if len(self.crashed_nodes) == 0:
            print("No node to resurrect")
            return

        choice = random.choice(self.crashed_nodes)
        self.nodes.get(choice).available = True
        # remove from the list of crashed nodes
        self.crashed_nodes.remove(choice)
        print("Node %s resurrect" % choice)

    def simulate_link_resurrection(self):
        if len(self.crashed_links) == 0:
            print("No links to resurrect")
            return
        
        dictionary = random.choice(self.crashed_links)
        self.latencies.get(dictionary['first']).get(dictionary['second'])['available'] = True
        # remove from the list of crashed nodes
        self.crashed_links.remove(dictionary)
        print("Link %s <-> %s resurrect" % (dictionary['first'], dictionary['second']))
        