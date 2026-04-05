import pytest
from risk_of_empires.maps.map_generation import MapGenerator


@pytest.fixture(scope="module")
def dic_pars():
    return {
        "display_size": (600, 500),  # Display size (X-pixels, Y-pixels)
        "n_terr": 20,  # Number of territories
        "n_cont": 2,  # Number of continents
        "min_dist": 50,  # Minimum distance between territory centers (pixels)
        "n_edg": 9,  # Maximum number of edges (i.e. boundaries) with other territories
        "phi_min": 0.3  # Maximum angle between 2 edges (avoid creating boundary with a territory that has another in between
    }

@pytest.fixture(scope="module")
def map(dic_pars):
    map = MapGenerator(dic_pars)
    map.generate_map()
    return map

def test_number_territories(map, dic_pars):
    """
    Test map_generation method
    :param map:         Map object
    :return:
    """
    assert len(map.dic_terr) == dic_pars["n_terr"]

def test_edge_reciprocity(map, dic_pars):
    """
    Assert that edges between territories are reciprocal, i.e.
    both territories are connected to each other.
    :param map:
    :param dic_pars:
    :return:
    """
    l_one_way_edges = []
    for terr in map.dic_terr.values():
        for edge in terr.dic_edges.values():
            # Retrieve neighbour's territory name
            terr2 = edge.nodes[1]
            try:
                # Attempt retrieving corresponding edge
                map.dic_terr[terr2].dic_edges[edge.name]
            except KeyError:
                l_one_way_edges.append(edge.name)
    assert len(l_one_way_edges) == 0




