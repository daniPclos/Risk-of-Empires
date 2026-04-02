import pygame

from risk_of_empires.maps.edges import SurfacePoint
from risk_of_empires.maps.territories import Territory, CompleteGraphGenerator
from risk_of_empires.utilities.drawing_tools import color_palette
from risk_of_empires.utilities.geometry_tools import *
from itertools import combinations


class MapGenerator:
    """
    Class that contains the logic to generate the map coordinates
    """
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
        self.k_x = None

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
        self.order_edges_phi()
        self.extract_complete_graphs()
        self.add_boundary_points()
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

            # Remove itself from distances, sort them and store the n_edg closest edges
            del dic_dist[terr.name]
            dic_edges = dict(sorted(dic_dist.items(), key=lambda item: item[1])[:n_edg])
            for terr_name in dic_edges.keys():
                terr.create_edge(self.dic_terr[terr_name])
                self.dic_terr[terr_name].create_edge(self.dic_terr[terr.name])  # Create reciprocal edge

        # Remove edges that lay beyond a nearer edge
        phi_min = self.dic_pars["phi_min"]
        for terr in self.dic_terr.values():
            l_edges_to_delete = []
            dic_edge_rec_to_delete = {}
            for edge1, edge2 in combinations(terr.edges.values(), 2):
                if abs(edge1.phi - edge2.phi) < phi_min:
                    edge_del = edge1 if edge1.l > edge2.l else edge2
                    l_edges_to_delete.append(edge_del.name)
                    dic_edge_rec_to_delete[edge_del.nodes[1]] = edge_del.name

            # Delete identified edges
            for edge_name in l_edges_to_delete:
                print(f"deleting edge {edge_name}")
                terr.delete_edge(edge_name)

            # Delete reciprocal edges
            for terr_name, edge_del in dic_edge_rec_to_delete.items():
                print(f"deleting reciprocal edge {edge_del}")
                self.dic_terr[terr_name].delete_edge(edge_del)

    def order_edges_phi(self):
        """
        Order edges by angle phi
        :return:
        """
        for terr in self.dic_terr.values():
            terr.edges = dict(sorted(terr.edges.items(), key=lambda item: item[1].phi))

    def extract_complete_graphs(self):
        """
        Method that extracts complete graphs within the map.
        That is sets of 3, 4, ..., n_edge territories that are
        all connected to each other.
        :return:
        """
        k_x = CompleteGraphGenerator()
        for terr_name, terr in self.dic_terr.items():
            # Add potential K3 (triangles) and K4 (cross-squares)
            edges = list(terr.edges.values())
            if len(edges) == 2:
                terr1 = self.dic_terr[edges[0].nodes[1]]
                terr2 = self.dic_terr[edges[1].nodes[1]]
                k_x.add_graph([terr, terr1, terr2],
                              {edge.name: edge for edge in edges})
            elif len(edges) == 3:
                terr1 = self.dic_terr[edges[0].nodes[1]]
                terr2 = self.dic_terr[edges[1].nodes[1]]
                terr3 = self.dic_terr[edges[2].nodes[1]]
                k_x.add_graph([terr, terr1, terr2, terr3],
                              {edge.name: edge for edge in edges})

                # Add K3
                for i in range(len(edges)):
                    terr1 = self.dic_terr[edges[i].nodes[1]]
                    terr2 = self.dic_terr[edges[(i + 1) % len(edges)].nodes[1]]
                    k_x.add_graph([terr, terr1, terr2],
                                  {edges[i].name: edges[i],
                                   edges[(i + 1) % len(edges)].name: edges[(i + 1) % len(edges)]})
            else:
                for i in range(len(edges)):
                    # Add K3
                    terr1 = self.dic_terr[edges[i].nodes[1]]
                    terr2 = self.dic_terr[edges[(i + 1) % len(edges)].nodes[1]]
                    k_x.add_graph([terr, terr1, terr2],
                                  {edges[i].name: edges[i],
                                   edges[(i + 1) % len(edges)].name: edges[(i + 1) % len(edges)]})

                    # Add K4
                    terr1 = self.dic_terr[edges[i].nodes[1]]
                    terr2 = self.dic_terr[edges[(i + 1) % len(edges)].nodes[1]]
                    terr3 = self.dic_terr[edges[(i + 2) % len(edges)].nodes[1]]
                    k_x.add_graph([terr, terr1, terr2, terr3],
                                  {edges[i].name: edges[i],
                                   edges[(i + 1) % len(edges)].name: edges[(i + 1) % len(edges)],
                                   edges[(i + 2) % len(edges)].name: edges[(i + 2) % len(edges)]})

        # transfer complete graphs (keep incomplete graphs as they might be useful in the future)
        k_x.transfer_complete_graphs()
        k_x.get_bound_p_for_complete_graphs()
        self.k_x = k_x

    def add_boundary_points(self):
        """
        Method that adds and readjusts boundary points between territories
        to avoid overlaps.
        :return:
        """
        for k_x in self.k_x.dic_complete_graphs.values():
            if k_x.n == 3:
                x = np.average([vals[0] for vals in k_x.dic_points_adj.values()])
                y = np.average([vals[1] for vals in k_x.dic_points_adj.values()])
                for terr in k_x.l_terr:
                    p = [x,y]
                    phi = calc_phi_points(terr.center, p)
                    q = calc_quadrant(terr.center, p)
                    surf_point = SurfacePoint(p, phi, q)
                    terr.surf_points.append(surf_point)

    def create_terr_surfaces(self):
        """
        Method that defines the territory surface points
        :return:
        """
        # Add midpoints between territories and edges
        for terr_name, terr in self.dic_terr.items():
            # Find middle points between territory center and edges
            for edge in terr.edges.values():
                p = calc_mid_point(terr.center, self.dic_terr[edge.nodes[1]].center)
                phi = calc_phi_points(terr.center, p)
                q = calc_quadrant(terr.center, p)
                surf_point = SurfacePoint(p, phi, q)
                terr.surf_points.append(surf_point)

            # Add additional points in missing quadrants
            for q, val in terr.dic_quadrants.items():
                if val==0:
                    p = terr.add_point_to_quadrant(q, self.dic_pars["display_size"])
                    phi = calc_phi_points(terr.center, p)
                    terr.surf_points.append(SurfacePoint(p, phi, q))

            # Order the points based on angle phi to ensure drawing continuous points along the periphery
            terr.surf_points.sort(key=lambda obj: obj.phi)

            # Extract surface points
            for p in terr.surf_points:
                terr.surf_coord.append(p.point)


class MapRenderer:
    """
    Class that renders the map
    """
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
    """
    Wrapper class that integrates the map generator and the map
    rendering classes
    """
    def __init__(self, display, dic_par):

        self.map_gen = MapGenerator(dic_par)
        self.renderer = MapRenderer(display)

    def generate_map(self):
        self.map_gen.generate_map()

    def draw_map(self):
        self.renderer.draw_map(self.map_gen.dic_terr)


def test_map(dic_pars):
    """
    Test map generation
    """
    display = pygame.display.set_mode(dic_pars["display_size"])
    clock = pygame.Clock()
    pygame.display.set_caption("Risk of Empires")

    # Create map
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
        "display_size": (900, 700),  # Display size (X-pixels, Y-pixels)
        "n_terr": 20,  # Number of territories
        "n_cont": 5,  # Number of continents
        "min_dist": 50,  # Minimum distance between territory centers (pixels)
        "n_edg": 5,  # Maximum number of edges (i.e. boundaries) with other territories
        "phi_min": 0.3  # Minimum angle between 2 edges (avoid creating boundary with a territory that has another in between
    }
    test_map(dic_pars)