import statistics
import time
from entorno import ContextoMarciano
import statistics
import time
from entorno import ContextoMarciano
import matplotlib.pyplot as plt
from collections import defaultdict

algoritmos = ["dijkstra", "a_star"]
heuristicas = ["euclidiana", "manhattan"]
repeticiones = 100
resultados = []

for _ in range(repeticiones):
    contexto = ContextoMarciano()
    if not contexto.existen_puntos_interes:
        continue

    inicio = contexto.base
    objetivo = contexto.puntos_interes[0]

    for t in algoritmos:
        print(t)
        if t == "dijkstra":
            coste, tiempo, ruta = contexto.buscar(inicio, objetivo, tipo=t)

            resultados.append({
                "algoritmo": t,
                "heuristica": None,
                "pasos": len(ruta) if ruta else None,
                "costo": coste,
                "tiempo": tiempo
            })
        else:
            for h in heuristicas:
                coste, tiempo, ruta = contexto.buscar(inicio, objetivo, tipo=t, tipo_heuristica=h)

                resultados.append({
                    "algoritmo": t,
                    "heuristica": h,
                    "pasos": len(ruta) if ruta else None,
                    "costo": coste,
                    "tiempo": tiempo
                })


agrupados = defaultdict(list)
for r in resultados:
    clave = (r["algoritmo"], r["heuristica"])
    agrupados[clave].append(r)

alg_heu = []
prom_pasos = []
prom_costo = []
prom_tiempo_real = []

for clave, vals in agrupados.items():
    pasos = [v["pasos"] for v in vals if v["pasos"] is not None]
    costo = [v["costo"] for v in vals if v["costo"] is not None]
    tiempo_real = [v["tiempo_real"] for v in vals if v["tiempo_real"] is not None]

    etiqueta = f"{clave[0].upper()} | {clave[1]}" if clave[1] else clave[0].upper()
    alg_heu.append(etiqueta)
    prom_pasos.append(statistics.mean(pasos) if pasos else 0)
    prom_costo.append(statistics.mean(costo) if costo else 0)
    prom_tiempo_real.append(statistics.mean(tiempo_real) if tiempo_real else 0)


# Pasos promedio
plt.figure(figsize=(10, 5))
plt.bar(alg_heu, prom_pasos, color="skyblue")
plt.ylabel("Pasos promedio")
plt.xticks(rotation=45, ha="right")
plt.title("Comparación de pasos promedio por algoritmo y heurística")
plt.tight_layout()
plt.show()

# Costo promedio
plt.figure(figsize=(10, 5))
plt.bar(alg_heu, prom_costo, color="salmon")
plt.ylabel("Costo promedio")
plt.xticks(rotation=45, ha="right")
plt.title("Comparación de costo promedio por algoritmo y heurística")
plt.tight_layout()
plt.show()

# Tiempo promedio (real)
plt.figure(figsize=(10, 5))
plt.bar(alg_heu, prom_tiempo_real, color="lightgreen")
plt.ylabel("Tiempo promedio real (s)")
plt.xticks(rotation=45, ha="right")
plt.title("Comparación de tiempo real promedio por algoritmo y heurística")
plt.tight_layout()
plt.show()


pasos_todos = []
costo_todos = []
tiempo_todos = []
labels = []

for clave, vals in agrupados.items():
    pasos = [v["pasos"] for v in vals if v["pasos"] is not None]
    costo = [v["costo"] for v in vals if v["costo"] is not None]
    tiempo = [v["tiempo_real"] for v in vals if v["tiempo_real"] is not None]

    pasos_todos.append(pasos)
    costo_todos.append(costo)
    tiempo_todos.append(tiempo)
    labels.append(f"{clave[0].upper()} | {clave[1]}" if clave[1] else clave[0].upper())

# Boxplot de pasos
plt.figure(figsize=(12, 6))
plt.boxplot(pasos_todos, labels=labels)
plt.ylabel("Pasos")
plt.xticks(rotation=45, ha="right")
plt.title("Distribución de pasos por algoritmo y heurística")
plt.tight_layout()
plt.show()

# Boxplot de tiempo real
plt.figure(figsize=(12, 6))
plt.boxplot(tiempo_todos, labels=labels)
plt.ylabel("Tiempo real (s)")
plt.xticks(rotation=45, ha="right")
plt.title("Distribución del tiempo real por algoritmo y heurística")
plt.tight_layout()
plt.show()