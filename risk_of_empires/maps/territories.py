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
        self.dic_edges: dict = {}
        self.dic_surf_points: dict = {}  # Surface coordinates as list of SurfacePoint objects
        self.surf_coord = []  # Surface coordinates ordered by phi in format for drawing utility
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
        self.dic_edges[name] = edge
        self.dic_quadrants[q] = 1

    def delete_edge(self, name):
        """
        Delete an edge from the territory
        :param name:    Name of the edge to delete
        :return:
        """
        try:
            del self.dic_edges[name]
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
        for edge in self.dic_edges.values():
            x_max = max(x_max, np.abs(edge.l * np.cos(edge.phi))/2)
            y_max = max(y_max, np.abs(edge.l * np.sin(edge.phi))/2)

        # Calculate distance to edge of the map
        x_lim = map_size[0] * (min(1, 1 + q_coeff(q)[0]) - q_coeff(q)[0] * self.center[0]/map_size[0])
        y_lim = map_size[1] * (min(1, 1 + q_coeff(q)[1]) - q_coeff(q)[1] * self.center[1]/map_size[1])

        # Return point in quadrant ensuring that doesn't fall beyond the edge of the map
        return (self.center[0] + q_coeff(q)[0] * min(x_max, x_lim), self.center[1] + q_coeff(q)[1] * min(y_max, y_lim))

    def add_surface_point(self, p:list[int]):
        """
        Method that adds surface points to the territory
        :return:
        """
        phi = calc_phi_points(self.center, p)
        q = calc_quadrant(self.center, p)
        surf_point = SurfacePoint(p, phi, q)
        name = f"{self.name}_{len(self.dic_surf_points)+1}"
        self.dic_surf_points[name] = surf_point

    def order_edges_by_phi(self, l_edge=[]):
        """
        Method that orders edges according to phi. If subset of edges
        l_edge is passed, that specific subset is ordered and returned
        :return:
        """
        if l_edge:
            subset = {k: self.dic_edges[k] for k in l_edge}
            return dict(sorted(subset.items(), key=lambda item: item[1].phi))
        else:
            dic_edges = dict(sorted(self.dic_edges.items(), key=lambda item: item[1].phi))
            self.dic_edges = dic_edges


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


