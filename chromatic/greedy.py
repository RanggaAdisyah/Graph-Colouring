import random

def greedy_coloring_welsh(graph):
    """
    Greedy Colouring (Welsh-Powell):
    Pewarnaan graf dengan urutan node berdasarkan derajat (degree) tertinggi ke terendah.
    Setiap node diberi warna sekecil mungkin yang tidak dipakai tetangganya.
    """
    order = sorted(graph, key=lambda x: len(graph[x]), reverse=True)
    color_map = {}
    for node in order:
        neighbor_colors = {color_map[n] for n in graph[node] if n in color_map}
        color = 1
        while color in neighbor_colors:
            color += 1
        color_map[node] = color
    return color_map

def greedy_coloring_random(graph):
    """
    Greedy Colouring (Random Order):
    Pewarnaan graf dengan urutan node acak.
    Setiap node diberi warna sekecil mungkin yang tidak dipakai tetangganya.
    """
    order = list(graph.keys())
    random.shuffle(order)
    color_map = {}
    for node in order:
        neighbor_colors = {color_map[n] for n in graph[node] if n in color_map}
        color = 1
        while color in neighbor_colors:
            color += 1
        color_map[node] = color
    return color_map 