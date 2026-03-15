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
        self.name = name
        self.center = center
        self.surf_points: list[SurfacePoint] = []
        self.surf_coord = []
        self.edges: dict = {}

    def create_edge(self, terr):
        """
        Method that creates edges between territories
        :param terr:        Territory to create an edge with
        :return:
        """
        nodes = [self.name, terr.name]
        name = f"{self.name}_{terr.name}"
        l = calc_dist_points(self.center, terr.center)
        phi = calc_phi_points(self.center, terr.center)
        midt_point = calc_mid_point(self.center, terr.center)
        q = calc_quadrant(self.center, midt_point)
        edge = Edge(name, nodes, l, phi, q)
        self.edges[name] = edge

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


