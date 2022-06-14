from infrastructure.infrastructure import Infrastructure
import networkx as nx

class PhysicalInfrastructure(Infrastructure) :
    original_graph : nx.Graph

    def __init__(self, nodes, graph, latencies, event_generators, services):
        self.nodes = nodes
        self.original_graph = graph
        self.graph = graph
        self.latencies = latencies
        self.event_generators = event_generators
        self.services = services


    def recalculate_routes(self) :
        # instance a copy of the original graph
        resulting_graph : nx.Graph = self.original_graph.copy()
        
        # remove crashed nodes
        resulting_graph.remove_nodes_from(self.crashed_nodes)
        # remove crashed direct links
        resulting_graph.remove_edges_from(self.crashed_links)

        # recalculate latencies
        self.latencies = dict(nx.all_pairs_dijkstra_path_length(resulting_graph))