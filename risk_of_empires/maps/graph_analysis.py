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

    def get_adj_cross_edges(self):
        """
        Method that classifies edges from complete graphs between
        edges that join adjacent territories and edges that join
        non-adjacent territories (i.e. crosses inside a square for a K4).
        :return:
        """
        # Get boundary points for K3
        if self.n==3:
            self.dic_points_adj = {edge.name: edge.p for edge in self.dic_edges.values()}

        elif self.n==4:
            # Identify first cross-edge and then 2nd edge after ordering by phi
            terr1 = self.l_terr[0]
            for terr in self.l_terr:
                print(f"{terr.name} has center {terr.center}")
            # Method using minimum phi difference between edges
            l_edges_t1 = [val for key, val in self.dic_edges.items() if is_str_in_concat_str(terr1.name, key)]
            print(f"terr1.name: {terr1.name}")
            print(f"l_edges_t1 =  {[edge.name for edge in l_edges_t1]}")
            edg_c1 = self.get_cross_edge(l_edges_t1, terr1.name)
            print(f"edg_c1.name: {edg_c1.name}")
            self.dic_points_cross[edg_c1.name] = edg_c1.p

            # Identify the other crossed edge by doing the same with one of the territories not bordering edg_c1
            terr2_c1_name = [t for t in edg_c1.nodes if t!=terr1.name][0]
            print(f"terr2_c1_name: {terr2_c1_name}")
            for terr3 in self.l_terr[1:]:
                if terr3.name != terr2_c1_name:
                    # Method using minimum phi difference between edges
                    l_edges_t2 = [val for key, val in self.dic_edges.items() if
                                      is_str_in_concat_str(terr3.name, key)]
                    print(f"terr3.name: {terr3.name}")
                    print(f"l_edges_t2 = {[edge.name for edge in l_edges_t2]}")
                    edg_c2 = self.get_cross_edge(l_edges_t2, terr3.name)
                    self.dic_points_cross[edg_c2.name] = edg_c2.p
                    break

            # Store adjacent edges by subtraction
            for edge in self.dic_edges.values():
                if edge.name != edg_c1.name and edge.name != edg_c2.name:
                    self.dic_points_adj[edge.name] = edge.p
        else:
            warnings.warn(f"get_bound_p not implemented for complete graphs of {self.n} territories.")

    def get_cross_edge(self, l_edges:list[Edge], terr_name:str):
        """
        Method that returns the cross edges (i.e. not adjacent)
        for a given vertex of the complete graph
        :param l_edges:
        :return:
        """
        l_phi_corr = []
        # Correct angle's sign based on reference territory
        for edge in l_edges:
            if edge.nodes[0] == terr_name:
                l_phi_corr.append(edge.phi)
            elif edge.nodes[1] == terr_name:
                l_phi_corr.append(-edge.phi)
            else:
                raise ValueError ("edge does not belong the reference territory")

        l_phi_diff = []

        # Calculate angles differences and pick the smallest sum as one belonging to the cross edge
        for phi in l_phi_corr:
            print(f"phi = {phi}")
            l_phi_diff.append(sum(abs(phi - phi2) for phi2 in l_phi_corr))

        print(f"l_phi_diff = {l_phi_diff}")
        i_min = l_phi_diff.index(min(l_phi_diff))

        return l_edges[i_min]


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

    def remove_k3s_within_k4s(self):
        """
        Method that removes k3 that are part of
        a k4 subgraph, to avoid drawing upon each other
        :return:
        """
        l_k_x_to_remove = []
        for graph in self.dic_complete_graphs.values():
            print(f"graph name = {graph.name}")
            if graph.n == 3:
                for graph2 in self.dic_complete_graphs.values():
                    if graph2.n == 4:
                        for idx, terr_name in enumerate(graph.name.split("_")):
                            if not terr_name in graph2.name:
                                break
                            elif idx == 2:
                                l_k_x_to_remove.append(graph.name)
        for k3_name in l_k_x_to_remove:
            self.dic_complete_graphs.pop(k3_name)
            print(f"Removed {k3_name} from complete graphs.")


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

    def get_adj_cross_edges_all_graphs(self):
        """
        Method that saves the boundary points between the territories forming
        complete graphs.
        :return:
        """
        for graph in self.dic_complete_graphs.values():
            graph.get_adj_cross_edges()
