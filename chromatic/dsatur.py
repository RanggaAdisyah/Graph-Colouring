def dsatur_coloring(graph):
    # DSatur: pilih node dengan derajat saturasi tertinggi
    color_map = {}
    saturation = {node: 0 for node in graph}
    degrees = {node: len(neigh) for node, neigh in graph.items()}
    while len(color_map) < len(graph):
        # Pilih node dengan saturasi tertinggi, jika seri pilih derajat tertinggi
        uncolored = [n for n in graph if n not in color_map]
        max_sat = max(saturation[n] for n in uncolored)
        candidates = [n for n in uncolored if saturation[n] == max_sat]
        node = max(candidates, key=lambda n: degrees[n])
        neighbor_colors = {color_map[n] for n in graph[node] if n in color_map}
        color = 1
        while color in neighbor_colors:
            color += 1
        color_map[node] = color
        # Update saturasi tetangga
        for n in graph[node]:
            if n not in color_map:
                neighbor_colors_n = {color_map[nb] for nb in graph[n] if nb in color_map}
                saturation[n] = len(neighbor_colors_n)
    return color_map 