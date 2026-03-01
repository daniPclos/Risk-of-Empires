import pygame
import random


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
        self.l_terr: list[Territory] = []
        self.color_list = [
            (200, 180, 0),
            (255, 100, 203),
            (166, 168, 255),
            (255, 250, 134),
            (168, 123, 255),
        ]

    def generate_map(self, n_terr=10, n_cont=2, min_dist=10):
        width, height = self.display.get_size()
        l_centers = random_points_with_spacing(width, height, min_dist, n_terr)
        for idx, t in enumerate(l_centers):
            surf_coord = ([t[0]-5, t[1]-5], [t[0]+5, t[1]-5], [t[0], t[1]+5])
            self.l_terr.append(Territory(f"terr_{idx}", t, surf_coord))
            self.draw_territory(self.display, surf_coord)

    def draw_map(self):
        """
        Draw the map from the territory list
        :return:
        """
        for terr in self.l_terr:
            self.draw_territory(self.display, terr.surf_coord)

    def draw_territory(self, display: pygame.Surface, surf_coord):
        """
        Draw a territory from its coordinates
        :param display:     Board display
        :param surf_coord:  Territory surface coordinates
        :return:
        """
        pygame.draw.polygon(display, self.color_list[0], surf_coord)

class Territory():
    def __init__(
        self,
        name,
        center: list[int],
        surf_coord,
    ):
        self.center = center
        self.name = name
        self.surf_coord = surf_coord
        self.edges = None

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

def test_map():
    """
    Test map generation
    """
    display = pygame.display.set_mode((600, 500))
    clock = pygame.Clock()
    pygame.display.set_caption("Risk of Empires")
    # how many territories to spawn every frame
    n_terr = 10  # Number of territories
    n_cont = 2  # Number of continents


    # Create map
    map = Map(display)

    display.fill((20, 20, 40))
    map.generate_map(n_terr=n_terr, n_cont=n_cont)

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
    test_map()