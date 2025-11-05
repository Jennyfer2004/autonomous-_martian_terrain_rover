from entorno import *

import time
import pandas as pd

NUM_EJECUCIONES = 30
TAMAÑO_MAPA = 4
ENERGIA_MAX = 100
RESULTADOS_FILE = 'resultados_comparacion.csv'

todos_los_resultados = []

for i in range(NUM_EJECUCIONES):
    print(f"\n--- Iniciando ejecución número {i+1} ---")
    
    contexto = ContextoMarciano(tamaño=TAMAÑO_MAPA, energia_max=ENERGIA_MAX)
    
    start_time = time.time()
    resultado_bfs = contexto.simular_con_bfs() 
    end_time = time.time()
    if resultado_bfs:
        todos_los_resultados.append({
            'Ejecucion': i + 1,
            'Algoritmo': 'BFS',
            'Coste_Plan': resultado_bfs['coste_plan'],
            'Tiempo_Busqueda': end_time - start_time,
            'Tiempo_Ejecucion': resultado_bfs['tiempo_ejecucion'],
            'Longitud_Plan': len(resultado_bfs['plan']),
            'Nodos_Explorados': resultado_bfs['nodos_explorados']
        })

    start_time = time.time()
    resultado_ga = contexto.simular_con_metaheuristica("GA") 
    end_time = time.time()
    if resultado_ga:
        todos_los_resultados.append({
            'Ejecucion': i + 1,
            'Algoritmo': 'GA',
            'Coste_Plan': resultado_ga['coste_plan'],
            'Tiempo_Busqueda': end_time - start_time,
            'Tiempo_Ejecucion': resultado_ga['tiempo_ejecucion'],
            'Longitud_Plan': len(resultado_ga['plan']),
            'Nodos_Explorados': 'N/A'
        })

    start_time = time.time()
    resultado_sa = contexto.simular_con_metaheuristica("SA")
    end_time = time.time()
    if resultado_sa:
        todos_los_resultados.append({
            'Ejecucion': i + 1,
            'Algoritmo': 'SA',
            'Coste_Plan': resultado_sa['coste_plan'],
            'Tiempo_Busqueda': end_time - start_time,
            'Tiempo_Ejecucion': resultado_sa['tiempo_ejecucion'],
            'Longitud_Plan': len(resultado_sa['plan']),
            'Nodos_Explorados': 'N/A'
        })

df = pd.DataFrame(todos_los_resultados)
df.to_csv(RESULTADOS_FILE, index=False)
print(f"\n✅ Todos los resultados guardados en '{RESULTADOS_FILE}'")
print(df.head()) 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('resultados_comparacion.csv')

print("--- Estadísticas Descriptivas ---")
stats_coste = df.groupby('Algoritmo')['Coste_Plan'].describe()
print(stats_coste)

stats_tiempo_busqueda = df.groupby('Algoritmo')['Tiempo_Busqueda'].describe()
print("\n--- Tiempo de Búsqueda ---")
print(stats_tiempo_busqueda)

sns.set_theme(style="whitegrid")

# Gráfico 1: Boxplot para comparar la distribución del Coste del Plan
plt.figure(figsize=(10, 6))
sns.boxplot(x='Algoritmo', y='Coste_Plan', data=df)
plt.title('Comparación del Coste del Plan entre Algoritmos')
plt.ylabel('Coste del Plan')
plt.xlabel('Algoritmo')
plt.show()

# Gráfico 2: Boxplot para comparar el Tiempo de Búsqueda
plt.figure(figsize=(10, 6))
sns.boxplot(x='Algoritmo', y='Tiempo_Busqueda', data=df)
plt.title('Comparación del Tiempo de Búsqueda entre Algoritmos')
plt.ylabel('Tiempo de Búsqueda (segundos)')
plt.xlabel('Algoritmo')
plt.show()

# Gráfico 3: Barplot para comparar la media del Tiempo de Ejecución
plt.figure(figsize=(10, 6))
sns.barplot(x='Algoritmo', y='Tiempo_Ejecucion', data=df, estimator='mean', errorbar='sd') 
plt.title('Tiempo de Ejecución Promedio del Plan')
plt.ylabel('Tiempo de Ejecución (segundos)')
plt.xlabel('Algoritmo')
plt.show()
