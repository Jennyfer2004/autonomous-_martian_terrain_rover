import heapq
import math

def heuristica(a, b, tipo="euclidiana"):
    """Define las heurísticas utilizadas en la búsqueda"""
    if tipo == "manhattan":
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def buscar_ruta(contexto, inicio, objetivo, tipo="a_star", tipo_heuristica="manhattan"):
    """ Devuelve la ruta entre dos puntos usando el algoritmo especificado"""
    open_set = []

    heapq.heappush(open_set, (0, 0, 0, inicio))
    came_from = {}
    g_score = {inicio: [0, 0]} 

    while open_set:
        f, costo, tiempo, actual = heapq.heappop(open_set)

        if actual == objetivo:
            ruta = [actual]
            while actual in came_from:
                actual = came_from[actual]
                ruta.append(actual)
            ruta.reverse()
            return ruta

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = actual[0]+dx, actual[1]+dy
            if not contexto.celda_valida(nx, ny):
                continue

            terreno = contexto.tipo_terreno(nx, ny)
            coste_mov = contexto.coste_movimiento(terreno)
            tiempo_mov = contexto.tiempo_movimiento(terreno)

            nuevo_costo = costo + coste_mov
            nuevo_tiempo = tiempo + tiempo_mov

            if (nx, ny) not in g_score or nuevo_costo < g_score[(nx, ny)][0] or \
               (nuevo_costo == g_score[(nx, ny)][0] and nuevo_tiempo < g_score[(nx, ny)][1]):

                g_score[(nx, ny)] = [nuevo_costo, nuevo_tiempo]

                if tipo == "a_star":
                    f = nuevo_costo + heuristica((nx, ny), objetivo, tipo_heuristica)
                else:  # dijkstra
                    f = nuevo_costo

                heapq.heappush(open_set, (f, nuevo_costo, nuevo_tiempo, (nx, ny)))
                came_from[(nx, ny)] = actual

    return None
