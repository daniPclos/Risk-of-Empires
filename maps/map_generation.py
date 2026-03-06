import math
import pygame
import random
from utilities.drawing_tools import color_palette

class Map:
    def __init__(
        self,
        display: pygame.Surface,
    ):
        """
        Container class for the map board
        :param display:
        """
        self.display = display
        self.dic_terr: dict = {}
        self.color_list = color_palette()

    def generate_map(self, n_terr=10, n_cont=2, min_dist=10, n_edg=5):
        """
        Method that generates the map as a graph containing territories as nodes
        with edges defining their connections
        :param n_terr:                  Number of territories to generate
        :param n_cont:                  Number of continents to generate
        :param min_dist:                Minimum distance between territories
        :return:
        """
        width, height = self.display.get_size()
        # Create center points for the different territories
        l_centers = random_points_with_spacing(width, height, min_dist, n_terr)
        for idx, t in enumerate(l_centers):
            self.dic_terr[f"terr_{idx}"] = (Territory(f"terr_{idx}", t))

        self.create_edges(n_edg)
        self.create_terr_surfaces()

    def create_edges(self, n_edg=5):
        """
        Method that creates edges between territories, determining their connectivity.
        This is done by computing the distance between territories and picking the
        n_av closest ones as edges.
        :param n_edg: Number of edges to generate per territory
        :return:
        """
        for terr in self.dic_terr.values():
            dic_dist = {}
            for terr_it in self.dic_terr.values():
                dic_dist[terr_it.name] = calc_dist_points(terr.center, terr_it.center)
            # Remove itself from distances sort them and store the closest edges
            del dic_dist[terr.name]
            terr.edges = dict(sorted(dic_dist.items(), key=lambda item: item[1])[:n_edg])
            print(f"terr.edges: {terr.edges}")

    def create_terr_surfaces(self):
        """
        Method that creates territory surfaces from distances between
        closest neighbours defined as edges
        :return:
        """
        for terr_name, terr in self.dic_terr.items():
            l_edge_coord = []
            # Find middle points between territory center and edges
            for edge in terr.edges.keys():
                l_edge_coord.append([(terr.center[0] + self.dic_terr[edge].center[0]) / 2, (terr.center[1] + self.dic_terr[edge].center[1]) / 2])
            terr.surf_coord = l_edge_coord


    def draw_map(self):
        """
        Draw the map from the territory list
        :return:
        """
        for idx, terr in enumerate(self.dic_terr.values()):
            self.draw_territory(terr.surf_coord, color=idx+1)

    def draw_territory(self, surf_coord, color=0):
        """
        Draw a territory from its coordinates
        :param display:     Board display
        :param surf_coord:  Territory surface coordinates
        :return:
        """
        pygame.draw.polygon(self.display, self.color_list[color], surf_coord)

    def draw_centers(self):
        """
        Method that draws the centers of the territories
        :return:
        """
        for t in self.dic_terr.values():
            pygame.draw.polygon(self.display, self.color_list[0], ([t.center[0]-5, t.center[1]-5],
                                                                   [t.center[0]+5, t.center[1]-5],
                                                                   [t.center[0], t.center[1]+5]))

class Territory():
    def __init__(
        self,
        name,
        center: list[int],
    ):
        self.center = center
        self.name = name
        self.surf_coord = None
        self.edges = None

def calc_dist_points(p1, p2):
    """
    Calculate the distance between two points
    :param p1:      point 1 (x, y)
    :param p2:      point 2 (x, y)
    :return:
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

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

def test_map(n_terr=10, n_cont=2, min_dist=10, n_edg=5):
    """
    Test map generation
    """
    display = pygame.display.set_mode((600, 500))
    clock = pygame.Clock()
    pygame.display.set_caption("Risk of Empires")

    # Create map
    map = Map(display)

    display.fill((20, 20, 40))
    map.generate_map(n_terr=n_terr, n_cont=n_cont, min_dist=min_dist, n_edg=n_edg)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass

        display.fill((20, 20, 40))
        map.draw_map()
        map.draw_centers()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    n_terr = 10
    n_cont = 2
    min_dist = 150
    n_edg = 3
    test_map(n_terr=n_terr, n_cont=n_cont, min_dist=min_dist, n_edg=n_edg)