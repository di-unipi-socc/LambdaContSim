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


    def update(self) :
        filtered_nodes = [node for node, node_data in self.graph.nodes(data=True)
                   if node_data['available'] == True]
        
        resulting_graph : nx.Graph = self.original_graph.subgraph(filtered_nodes)
        print(resulting_graph)

        self.latencies = dict(nx.all_pairs_dijkstra_path_length(resulting_graph))