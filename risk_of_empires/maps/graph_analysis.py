import warnings
from risk_of_empires.maps.edges import Edge
from risk_of_empires.maps.territories import Territory
from risk_of_empires.utilities.misc_tools import is_str_in_concat_str

class SubGraphX:
    """
    Class that represents a potential complete sub graph, where all territories
    are connected to each other.
    """
    def __init__(self, l_terr:list[Territory], name, dic_edges:dict[Edge]):
        """
        Complete graph constructor.
        :param l_terr:          list of territories
        :param dic_edges:         List of edges joining the territories

        """
        self.n = len(l_terr)
        self.l_terr = l_terr #l_terr.sort(key=lambda obj: obj.center[0])
        self.dic_edges = dic_edges
        self.name = name
        self.i_times = 1
        self.dic_points_adj = {}
        self.dic_points_cross = {}

    def get_bound_p(self):
        """
        Method that returns the boundary points between the territories, assuming
        they are all connected to each other, i.e. complete.
        :return:
        """
        # Get boundary points for K3
        if self.n==3:
            self.dic_points_adj = {edge.name: edge.p for edge in self.dic_edges.values()}

        elif self.n==4:
            dic_points_cross = {}
            dic_points_adj = {}

            # Identify first cross-edge and then 2nd edge after ordering by phi
            terr1 = self.l_terr[0]
            l_edges_t1 = [key for key in self.dic_edges.keys() if is_str_in_concat_str(terr1.name, key)]  # OBS terr1 IS in terr10_terr16
            l_edges_ord = terr1.order_edges_by_phi(l_edges_t1)
            edg_c1 = list(l_edges_ord.values())[1]
            self.dic_points_cross[edg_c1.name] = edg_c1.p

            # Identify the other crossed edge by doing the same with one of the territories not bordering edg_c1
            terr2_c1 = edg_c1.nodes[1]
            for terr2 in self.l_terr[1:]:
                if terr2.name != terr2_c1:
                    l_edges_t2 = [key for key in self.dic_edges.keys() if is_str_in_concat_str(terr2.name, key)]
                    l_edges_ord = terr2.order_edges_by_phi(l_edges_t2)
                    edge_c2 = list(l_edges_ord.values())[1]
                    self.dic_points_cross[edge_c2.name] = edge_c2.p
            # Store adjacent edges by subtraction
            for edge in self.dic_edges.values():
                if edge.name != edg_c1.name and edge.name != edge_c2.name:
                    self.dic_points_adj[edge.name] = edge.p
        else:
            warnings.warn(f"get_bound_p not implemented for complete graphs of {self.n} territories.")

class CompleteGraphGenerator():
    """
    Class that generates complete graphs by storing
    sets of territories from each territory perspective
    to assess cross-connectivity leading to complete graphs.
    """
    def __init__(self):
        self.dic_incomplete_graphs = {}
        self.dic_complete_graphs = {}

    def add_graph(self, l_terr:list[Territory], dic_edges:dict[Edge]):
        """
        Method that adds new graphs to dic_graphs if they do
        not yet exist or increases their counter to evaluate
        if they are complete, otherwise.
        :param l_terr:          List of territories candidates as
                                complete graphs
        :param dic_edges:         List of edges joining the territories
        :return:
        """
        name = self.make_graph_name(l_terr)
        if name in self.dic_incomplete_graphs:
            self.dic_incomplete_graphs[name].i_times += 1
            # Add new edges or overwrite existing ones with equivalent ones
            for edge_name, edge in dic_edges.items():
                self.dic_incomplete_graphs[name].dic_edges[edge_name] = edge
        else:
            self.dic_incomplete_graphs[name] = SubGraphX(l_terr, name, dic_edges)

    def make_graph_name(self, l_terr:list[Territory]):
        return "_".join(sorted([f"{terr.name}" for terr in l_terr]))

    def transfer_complete_graphs(self):
        """
        Method that transfer complete graphs to specific placeholder.
        :return:
        """
        l_graphs_to_transfer = []
        for graph_name, graph in self.dic_incomplete_graphs.items():
            if graph.i_times == graph.n:
                l_graphs_to_transfer.append(graph_name)

        for graph_name in l_graphs_to_transfer:
            self.dic_complete_graphs[graph_name] = self.dic_incomplete_graphs.pop(graph_name)

    def get_bound_p_for_complete_graphs(self):
        """
        Method that saves the boundary points between the territories forming
        complete graphs.
        :return:
        """
        for graph in self.dic_complete_graphs.values():
            graph.get_bound_p()
