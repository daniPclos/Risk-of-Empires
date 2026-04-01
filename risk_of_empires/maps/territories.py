import numpy as np
from risk_of_empires.maps.edges import Edge, SurfacePoint
from risk_of_empires.utilities.geometry_tools import calc_dist_points, calc_phi_points, calc_mid_point, calc_quadrant


class Territory():
    """
    Class that represents a territory in the map. It contains a dictionary
    of edges which connect it to other territories.
    """
    def __init__(
        self,
        name,
        center: list[int],
    ):
        """
        Territory constructor.
        :param name:        Name of the territory.
        :param center:      Coordinates of the center of the territory.
        :param center:
        """
        self.name = name
        self.center = center
        self.edges: dict = {}
        self.surf_points: list[SurfacePoint] = []
        self.surf_coord = []
        self.dic_quadrants = {"Q1": 0,
                              "Q2": 0,
                              "Q3": 0,
                              "Q4": 0}

    def create_edge(self, terr):
        """
        Method that creates edges between territories
        :param terr:        Territory to create an edge with
        :return:
        """
        nodes = [self.name, terr.name]
        name = "_".join(sorted([self.name, terr.name]))
        l = calc_dist_points(self.center, terr.center)
        phi = calc_phi_points(self.center, terr.center)
        p = calc_mid_point(self.center, terr.center)
        q = calc_quadrant(self.center, p)
        edge = Edge(name, nodes, l, phi, q, p)
        self.edges[name] = edge
        self.dic_quadrants[q] = 1

    def delete_edge(self, name):
        """
        Delete an edge from the territory
        :param name:    Name of the edge to delete
        :return:
        """
        try:
            del self.edges[name]
        except KeyError:
            print(f"Edge {name} not found")

    def add_point_to_quadrant(self, q:str, map_size:tuple):
        """
        Method that fills surface points in quadrants
        around the territory's center where there are no
        points, typically for edge-of-map territories.
        :param q:               Identified quadrant with missing points
        :param map_size:        Size of the map
        :return:
        """
        # Compute maximum distances in X and Y directions for existing edges to balance a similar distance in the missing quadrant
        x_max, y_max = 100, 100
        for edge in self.edges.values():
            x_max = max(x_max, np.abs(edge.l * np.cos(edge.phi))/2)
            y_max = max(y_max, np.abs(edge.l * np.sin(edge.phi))/2)

        # Calculate distance to edge of the map
        x_lim = map_size[0] * (min(1, 1 + q_coeff(q)[0]) - q_coeff(q)[0] * self.center[0]/map_size[0])
        y_lim = map_size[1] * (min(1, 1 + q_coeff(q)[1]) - q_coeff(q)[1] * self.center[1]/map_size[1])

        # Return point in quadrant ensuring that doesn't fall beyond the edge of the map
        return (self.center[0] + q_coeff(q)[0] * min(x_max, x_lim), self.center[1] + q_coeff(q)[1] * min(y_max, y_lim))


def q_coeff(q:str):
    """
    Returns x and y coefficient of quadrant q
    :param q:           Quadrant name
    :return:
    """
    dic_q_coeff = {
        "Q1": (1, 1),
        "Q2": (-1, 1),
        "Q3": (-1, -1),
        "Q4": (1, -1),
    }
    return dic_q_coeff[q]

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
        self.dic_points_adj = None
        self.dic_ponts_cross = None

    def get_bound_p(self):
        """
        Method that returns the boundary points between the territories, assuming
        they are all connected to each other, i.e. complete.
        :return:
        """
        # Get boundary points for K3
        if len(self.l_terr)==3:
            self.dic_points_adj = {edge.name: edge.p for edge in self.dic_edges.values()}

        elif len(self.l_terr)==4:
            dic_points_adj = {}
            dic_points_cross = {}



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
            # Add new edges or overwrite existing ones
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