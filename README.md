

# Rover Autónomo Marciano para Exploración en Entornos Desconocidos

Proyecto de simulación de un rover autónomo diseñado para ejecutar misiones científicas en un entorno marciano desconocido, utilizando técnicas avanzadas de inteligencia artificial para la navegación, planificación y optimización de recursos.

## Características Principales

- **Navegación Punto a Punto**: Implementación y comparación de algoritmos de búsqueda (Dijkstra y A*) con diferentes heurísticas
- **Planificación con Metaheurísticas**: Estrategias de misión mediante Algoritmo Genético y Recocido Simulado
- **Satisfacción de Restricciones (CSP)**: Generación automática de mapas viables
- **Optimización de Recursos**: Gestión energética y planificación de rutas eficientes
- **Simulación Completa**: Ejecución autónoma de misiones con recolección de muestras

## Requisitos

- Python 3.8 o superior
- Las siguientes dependencias (instalables con pip):
  - numpy
  - matplotlib
  - networkx
  - scipy

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/Jennyfer2004/autonomous-_martian_terrain_rover.git
cd autonomous-_martian_terrain_rover
```

## Ejecución

Para ejecutar la simulación completa del rover autónomo:

```bash
python main.py
```

Este comando iniciará la simulación con metaheurísticas, donde el rover explorará el entorno, visitará puntos de interés científico, gestionará sus recursos energéticos y retornará a la base.

## Resultados Principales

### Algoritmos de Búsqueda

| Algoritmo | Heurística | Promedio Pasos | Promedio Costo | Promedio Tiempo (ms) |
|-----------|------------|----------------|----------------|---------------------|
| a_star    | manhattan  | 15.67          | 26.91          | 0.228               |
| a_star    | euclidiana | 15.69          | 26.91          | 0.258               |
| dijkstra  | ---        | 15.67          | 26.91          | 0.322               |

### Estrategias de Planificación

| Algoritmo | Mean (Costo) | Std (Costo) | Mean (Tiempo ms) |
|-----------|--------------|-------------|------------------|
| BFS       | 50.57        | 11.01       | 2.55             |
| SA        | 51.87        | 17.09       | 3.83             |
| GA        | 59.25        | 15.53       | 7.93             |

## Conclusiones

- **A*** con la heurística de **Distancia Manhattan** es la opción más eficiente para la navegación punto a punto en entornos de cuadrícula.
- El **Recocido Simulado (SA)** es una metaheurística superior al Algoritmo Genético para este problema específico de planificación, ofreciendo un excelente equilibrio entre calidad de la solución y tiempo de cómputo.
- La integración de técnicas de búsqueda, planificación y CSP permite descomponer un problema complejo en subproblemas manejables.

## Mejoras Futuras

- **Aprendizaje por Refuerzo**: Implementar un agente que aprenda políticas de navegación óptimas a través de la experiencia.
- **Re-planificación Dinámica**: Desarrollar un sistema que pueda adaptar el plan en tiempo real ante eventos imprevistos.
- **Comunicación Multi-agente**: Simular escenarios con múltiples rovers colaborando en una misión.


## Autor

Jennifer de la Caridad Sánchez Santana
