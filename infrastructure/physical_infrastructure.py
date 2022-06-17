from math import inf
from infrastructure.infrastructure import Infrastructure, LinkInfo
import networkx as nx

from utils import is_edge_part


class PhysicalInfrastructure(Infrastructure):
    original_graph: nx.Graph
    links_affected_by_crashes: dict[(str | tuple), set]

    def __init__(
        self,
        nodes: dict,
        graph: nx.Graph,
        links: dict,
        event_generators: dict,
        services: dict,
    ):
        self.nodes = nodes
        self.original_graph = graph
        self.graph = graph
        self.links = links
        self.event_generators = event_generators
        self.services = services
        self.links_affected_by_crashes = {}

    def recalculate_routes_after_crash(self, crashed_nodes: list, crashed_link: tuple):
        # instance a copy of the original graph
        resulting_graph: nx.Graph = self.original_graph.copy()

        # remove crashed nodes
        resulting_graph.remove_nodes_from(self.crashed_nodes)
        # remove crashed direct links
        resulting_graph.remove_edges_from(self.crashed_links)

        # get alive nodes as list
        alive_nodes: list[str] = list(resulting_graph.nodes)

        # do links need to be checked?
        check_link = False

        if crashed_link is not None:
            first_link_node, second_link_node = crashed_link
            check_link = True

            # create set for key (node_link_1, node_link_2) into dictionary
            if crashed_link not in self.links_affected_by_crashes.keys():
                self.links_affected_by_crashes[crashed_link] = set()

        for crashed_node in crashed_nodes:
            # create set for key crashed_node into dictionary
            if crashed_node not in self.links_affected_by_crashes.keys():
                self.links_affected_by_crashes[crashed_node] = set()

        # local accumulator
        links_to_recalc = set()

        for index1 in range(0, len(alive_nodes)):
            # get first node id
            node1 = alive_nodes[index1]

            for index2 in range(index1 + 1, len(alive_nodes)):
                # get second node id
                node2 = alive_nodes[index2]

                path = self.links[node1][LinkInfo.PATH][node2]

                # if path is none then node1 and node2 are not linked
                if not path:
                    continue

                # re-calculate paths which includes the link
                if check_link:
                    if is_edge_part(path, first_link_node, second_link_node):
                        # this link should be re-calculated
                        links_to_recalc.add((node1, node2))
                        # add link to those which will be re-calculed when crashed_link resurrect
                        self.links_affected_by_crashes[crashed_link].add((node1, node2))

                # re-calculate paths which includes crashed node
                for crashed_node in crashed_nodes:
                    if crashed_node in path:
                        # this link should be re-calculated
                        links_to_recalc.add((node1, node2))
                        # add link to those which will be re-calculed when crashed_link resurrect
                        self.links_affected_by_crashes[crashed_node].add((node1, node2))

        # recalculate links' latency and path
        for (source, target) in links_to_recalc:
            try:
                new_latency, new_path = nx.single_source_dijkstra(
                    resulting_graph, source, target
                )
            except nx.NetworkXNoPath:
                # a new path doesn't exist
                new_latency, new_path = inf, None

            # update links structure from source to target and vice-versa
            self.links[source][LinkInfo.LATENCY][target] = new_latency
            self.links[source][LinkInfo.PATH][target] = new_path if new_path else None
            self.links[target][LinkInfo.LATENCY][source] = new_latency
            self.links[target][LinkInfo.PATH][source] = (
                new_path[::-1] if new_path else None
            )

    def recalculate_routes_after_resurrection(
        self, resurrected_nodes: list, resurrected_link: tuple
    ):
        # instance a copy of the original graph
        resulting_graph: nx.Graph = self.original_graph.copy()

        # remove crashed nodes
        resulting_graph.remove_nodes_from(self.crashed_nodes)
        # remove crashed direct links
        resulting_graph.remove_edges_from(self.crashed_links)

        # get alive nodes as list
        alive_nodes: list[str] = list(resulting_graph.nodes)

        # join resurrected nodes and link into the same structure
        resurrected_keys: list = resurrected_nodes + (
            [resurrected_link] if resurrected_link else []
        )

        links_to_recalc = set()
        for key in resurrected_keys:
            links_to_recalc.update(self.links_affected_by_crashes[key])
            # clear the set
            self.links_affected_by_crashes[key].clear()

        # recalculate links' latency and path
        for source, target in links_to_recalc:
            # skip if one of these node is crashed
            if source in self.crashed_nodes or target in self.crashed_nodes:
                continue
            try:
                new_latency, new_path = nx.single_source_dijkstra(
                    resulting_graph, source, target
                )
            except nx.NetworkXNoPath:
                # a new path doesn't exist
                new_latency, new_path = inf, None

            # update links structure from source to target and vice-versa
            self.links[source][LinkInfo.LATENCY][target] = new_latency
            self.links[source][LinkInfo.PATH][target] = new_path if new_path else None
            self.links[target][LinkInfo.LATENCY][source] = new_latency
            self.links[target][LinkInfo.PATH][source] = (
                new_path[::-1] if new_path else None
            )

        # re-calculate resurrected nodes' links
        for source in resurrected_nodes:
            for target in alive_nodes:
                try:
                    new_latency, new_path = nx.single_source_dijkstra(
                        resulting_graph, source, target
                    )
                except nx.NetworkXNoPath:
                    # a new path doesn't exist
                    new_latency, new_path = inf, None

                # update links structure from source to target and vice-versa
                self.links[source][LinkInfo.LATENCY][target] = new_latency
                self.links[source][LinkInfo.PATH][target] = (
                    new_path if new_path else None
                )
                self.links[target][LinkInfo.LATENCY][source] = new_latency
                self.links[target][LinkInfo.PATH][source] = (
                    new_path[::-1] if new_path else None
                )
