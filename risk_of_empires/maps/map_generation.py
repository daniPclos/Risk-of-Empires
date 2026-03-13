import math
import numpy as np
import pygame
import random
from risk_of_empires.utilities.drawing_tools import color_palette
from itertools import combinations


class MapGenerator:
    def __init__(
            self,
            dic_pars
    ):
        """
        Container class for the map board
        :param display:
        """
        self.dic_pars = dic_pars
        self.dic_terr: dict = {}
        self.color_list = color_palette()

    def generate_map(self):
        """
        Method that generates the map as a graph containing territories as nodes
        with edges defining their connections
        :param n_terr:                  Number of territories to generate
        :param n_cont:                  Number of continents to generate
        :param min_dist:                Minimum distance between territories
        :return:
        """
        width, height = self.dic_pars["display_size"]
        # Create center points for the different territories
        l_centers = random_points_with_spacing(width, height, self.dic_pars["min_dist"], self.dic_pars["n_terr"])
        for idx, t in enumerate(l_centers):
            self.dic_terr[f"terr_{idx}"] = (Territory(f"terr_{idx}", t))

        self.create_edges(self.dic_pars["n_edg"])
        self.create_terr_surfaces()

    def create_edges(self, n_edg):
        """
        Method that creates edges between territories, determining their connectivity.
        This is done by computing the distance between territories and picking the
        n_av closest ones as edges.
        :param n_edg: Number of edges to generate per territory
        :return:
        """
        # Determine closest n_edg neighbours
        for terr in self.dic_terr.values():
            dic_dist = {}
            for terr_it in self.dic_terr.values():
                dic_dist[terr_it.name] = calc_dist_points(terr.center, terr_it.center)
            # Remove itself from distances sort them and store the closest edges
            del dic_dist[terr.name]
            dic_edges = dict(sorted(dic_dist.items(), key=lambda item: item[1])[:n_edg])
            for terr_name in dic_edges.keys():
                terr.create_edge(self.dic_terr[terr_name])
                self.dic_terr[terr_name].create_edge(self.dic_terr[terr.name])  # Create reciprocal edge

        # Remove edges that lay beyond a nearer edge
        phi_max = self.dic_pars["phi_max"]
        for terr in self.dic_terr.values():
            l_edges_to_delete = []
            dic_edge_rec_to_delete = {}
            for edge1, edge2 in combinations(terr.edges.values(), 2):
                if abs(edge1.phi - edge2.phi) < phi_max:
                    edge_del = edge1 if edge1.l > edge2.l else edge2
                    l_edges_to_delete.append(edge_del.name)
                    dic_edge_rec_to_delete[edge_del.nodes[1]] = f"{edge_del.nodes[1]}_{terr.name}"
            # Delete identified edges
            for edge_name in l_edges_to_delete:
                print(f"deleting edge {edge_name}")
                terr.delete_edge(edge_name)
            # Delete reciprocal edges
            for terr_name, edge_del in dic_edge_rec_to_delete.items():
                print(f"deleting reciprocal edge {edge_del}")
                self.dic_terr[terr_name].delete_edge(edge_del)

        # Sort edges by phi to ensure drawing continuous points along the periphery
        for terr in self.dic_terr.values():
            terr.edges = dict(
                sorted(terr.edges.items(), key=lambda item: item[1].phi)
            )

        # for edge in terr.edges.values():
        #     print(f"edge nodes = {edge.nodes}\nedge l = {edge.l}\nedge phi = {edge.phi}\n")

    def create_terr_surfaces(self):
        """
        Method that creates territory surfaces from distances between
        closest neighbours defined as edges
        :return:
        """
        for terr_name, terr in self.dic_terr.items():
            l_edge_coord = []
            # Find middle points between territory center and edges
            for edge in terr.edges.values():
                l_edge_coord.append([(terr.center[0] + self.dic_terr[edge.nodes[1]].center[0]) / 2,
                                     (terr.center[1] + self.dic_terr[edge.nodes[1]].center[1]) / 2])
            terr.surf_coord = l_edge_coord


class Territory():
    def __init__(
        self,
        name,
        center: list[int],
    ):
        self.name = name
        self.center = center
        self.surf_coord = None
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
        edge = Edge(name, nodes, l, phi)
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

class Edge():
    def __init__(self, name:str, nodes: list[str], l, phi):
        self.name = name
        self.nodes = nodes
        self.l = l
        self.phi = phi

class MapRenderer:

    def __init__(self, display):
        self.display = display
        self.color_list = color_palette()

    def draw_map(self, dic_terr):
        """
        Draw the map from the territory list
        :return:
        """
        # Draw territory surfaces
        for idx, terr in enumerate(dic_terr.values()):
            self.draw_territory(terr.surf_coord, color=idx + 1)

        # Draw territory centers
        self.draw_centers(dic_terr)


    def draw_territory(self, surf_coord, color=0):
        """
        Draw a territory from its coordinates
        :param display:     Board display
        :param surf_coord:  Territory surface coordinates
        :return:
        """
        pygame.draw.polygon(self.display, self.color_list[color], surf_coord)

    def draw_centers(self, dic_terr):
        """
        Method that draws the centers of the territories
        :return:
        """
        for t in dic_terr.values():
            pygame.draw.polygon(self.display, self.color_list[0], ([t.center[0] - 5, t.center[1] - 5],
                                                                   [t.center[0] + 5, t.center[1] - 5],
                                                                   [t.center[0], t.center[1] + 5]))
class Map:

    def __init__(self, display, dic_par):

        self.map_gen = MapGenerator(dic_par)
        self.renderer = MapRenderer(display)

    def generate_map(self):
        self.map_gen.generate_map()

    def draw_map(self):
        self.renderer.draw_map(self.map_gen.dic_terr)

def calc_dist_points(p1, p2):
    """
    Calculate the distance between two points
    :param p1:      point 1 (x, y)
    :param p2:      point 2 (x, y)
    :return:
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def calc_phi_points(p1, p2):
    """
    Calculate angle between the line generated by the points
    p1, p2 and the X-axis of the map
    :param p1:      point 1 (x, y)
    :param p2:      point 2 (x, y)
    :return:
    """
    return np.arctan2(p2[1] - p1[1], p2[0] - p1[0])

def random_points_with_spacing(width, height, min_dist, count):
    """
    Function to randomly draw random points within a certain distance
    :param width:       width of the map
    :param height:      height of the map
    :param min_dist:    minimum distance between the point
    :param count:       number of random points to draw
    :return:
    """
    points = []

    while len(points) < count:
        p = [random.uniform(0, width), random.uniform(0, height)]
        if all((p[0]-q[0])**2 + (p[1]-q[1])**2 >= min_dist**2 for q in points):
            points.append(p)

    return points


def test_map(dic_pars):
    """
    Test map generation
    """
    display = pygame.display.set_mode(dic_pars["display_size"])
    clock = pygame.Clock()
    pygame.display.set_caption("Risk of Empires")

    # Create map
    # map = MapGenerator(display)
    map = Map(display, dic_pars)


    display.fill((20, 20, 40))
    map.generate_map()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass

        display.fill((20, 20, 40))
        map.draw_map()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    dic_pars = {
        "display_size": (600, 500),  # Display size (X-pixels, Y-pixels)
        "n_terr": 20,  # Number of territories
        "n_cont": 2,  # Number of continents
        "min_dist": 50,  # Minimum distance between territory centers (pixels)
        "n_edg": 9,  # Maximum number of edges (i.e. boundaries) with other territories
        "phi_max": 0.3  # Maximum angle between 2 edges (avoid creating boundary with a territory that has another in between
    }
    test_map(dic_pars)