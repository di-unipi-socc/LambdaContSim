from infrastructure.infrastructure import Infrastructure, LinkInfo
import networkx as nx

class PhysicalInfrastructure(Infrastructure) :
    original_graph : nx.Graph

    def __init__(self, nodes, graph, links, event_generators, services):
        self.nodes = nodes
        self.original_graph = graph
        self.graph = graph
        self.links = links
        self.event_generators = event_generators
        self.services = services

    def recalculate_routes_after_crash(self, crashed_nodes : list, crashed_link : list) :
        # instance a copy of the original graph
        resulting_graph : nx.Graph = self.original_graph.copy()
        
        # remove crashed nodes
        resulting_graph.remove_nodes_from(self.crashed_nodes)
        # remove crashed direct links
        resulting_graph.remove_edges_from(self.crashed_links)

        # get nodes as list
        nodes_list : list[str] = list(resulting_graph.nodes)

        check_link = False

        if len(crashed_link) > 0:
            first_node = crashed_link[0]
            second_node = crashed_link[1]
            check_link = True

        links_to_recalc = set()

        for index1 in range(0, len(nodes_list)):
            # get first node id
            node1 = nodes_list[index1]

            for index2 in range(index1 + 1, len(nodes_list)):
                # get second node id
                node2 = nodes_list[index2]

                # if there is no possibility to connect node1 and node2, then we don't have the link latency
                if node2 not in self.links[node1][LinkInfo.PATH].keys():
                    continue

                path = self.links[node1][LinkInfo.PATH][node2]

                # re-calculate paths which includes the link
                if check_link:
                    for index in range(0, len(path) - 1):
                        if first_node == path[index] and second_node == path[index+1]:
                            # this link should be re-calculated
                            links_to_recalc.add((node1, node2))
                
                # re-calculate paths which includes crashed node
                for crashed_node in crashed_nodes:
                    if crashed_node in path:
                        # this link should be re-calculated
                        links_to_recalc.add((node1, node2))
        
        # recalculate links' latency and path
        for (source, target) in links_to_recalc:
            new_latency, new_path = nx.single_source_dijkstra(resulting_graph, source, target)
            # update links structure from source to target and vice-versa
            self.links[source][LinkInfo.LATENCY][target] = new_latency
            self.links[source][LinkInfo.PATH][target] = new_path
            self.links[target][LinkInfo.LATENCY][source] = new_latency
            self.links[target][LinkInfo.PATH][source] = new_path[::-1]
    
    def recalculate_routes_after_resurrection(self) :
        # instance a copy of the original graph
        resulting_graph : nx.Graph = self.original_graph.copy()
        
        # remove crashed nodes
        resulting_graph.remove_nodes_from(self.crashed_nodes)
        # remove crashed direct links
        resulting_graph.remove_edges_from(self.crashed_links)

        # recalculate latencies
        self.links = dict(nx.all_pairs_dijkstra(resulting_graph))