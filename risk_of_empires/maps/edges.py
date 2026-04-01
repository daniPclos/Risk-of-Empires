class Edge():
    """
    Class that represents an edge connecting two territories.
    """
    def __init__(self, name:str, nodes: list[str], l, phi, q, p):
        """
        Initialize an edge connecting two territories.
        :param name:        Name of the edge as ("node1_node2")
        :param nodes:       List of 2 territory names (aka nodes) being connected by the edge
        :param l:           Length between the two territory centers
        :param phi:         Angle between the two territory centers and the X-axis of the map
        :param q:           Quadrant where the edge connects with respect to the center of the
                            territory storing the edge
        :param p:           Point of the edge connecting the two territories

        """
        self.name = name
        self.nodes = nodes
        self.l = l
        self.phi = phi
        self.q = q
        self.p = p


class SurfacePoint():
    """
    Class that represents a point belonging to a territory surface.
    """
    def __init__(self, point: list[int], phi, q):
        """
        Initialize a point belonging to a territory surface.
        :param point:           point coordinates
        :param phi:             angle between the line terr.center-point and the X-axis of the map
        :param q:               Quadrant where the point is with respect to the center of the
                                territory storing the surface point
        """
        self.point = point
        self.phi = phi
        self.q = q
