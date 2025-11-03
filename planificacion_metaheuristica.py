import random
import copy

# ACCIONES_PLANIFICADOR = [
#     {
#         'nombre': 'ir_a_poi',
#         'precondiciones': lambda estado, poi: estado['energia'] > 0,
#         'efectos': lambda estado, poi: {
#             'posicion': poi,
#             'energia': estado['energia'] - 10,  # Coste estimado
#             'muestras_recolectadas': estado['muestras_recolectadas'] | {poi} if poi not in estado['muestras_recolectadas'] else estado['muestras_recolectadas']
#         },
#         'coste': 10,
#         'tiempo': 15
#     },
#     {
#     "nombre":'recargar',
#     'precondiciones': lambda estado, base: estado['posicion'] == base and estado['energia'] < estado['bateria_max'],
#     'efectos': lambda estado, base: {
#         'energia': estado['bateria_max'],
#         'en_base': True
#     },
#     'coste': 0,
#     'tiempo': 30
# },
#     {
#         'nombre': 'dejar_muestras', 
#         'precondiciones': lambda estado, punto: estado['posicion'] == punto,
#         'efectos': lambda estado, punto: {
#             'muestras_recolectadas': set(),
#             'muestras_analizadas': estado['muestras_analizadas'] | estado['muestras_recolectadas']
#         },
#         'coste': 5,
#         'tiempo': 8
#     }
# ]

# En planificacion_metaheuristica.py

ACCIONES_PLANIFICADOR = [
    {
        'nombre': 'ir_a_poi',
        # Precondición: tener energía para al menos un paso
        'precondiciones': lambda estado, contexto, poi: estado['energia'] > 0,
        # Los efectos se calcularán dinámicamente en simulacion
        'efectos': None, 
    },
    {
        'nombre': 'ir_a_base',
        'precondiciones': lambda estado, contexto, base: estado['energia'] > 0 ,
        'efectos': None,
    },
    {
        'nombre': 'recargar',
        'precondiciones': lambda estado, contexto, base: estado['posicion'] == base and estado['energia'] < estado['bateria_max']
,
        'efectos': lambda estado, contexto, base: {
            'energia': estado['bateria_max'],
        },
        'coste': 0, # Coste fijo de la acción de recargar
        'tiempo': 10 # Tiempo fijo de la acción de recargar
    },
    {
        'nombre': 'dejar_muestras', 
        'precondiciones': lambda estado, contexto, punto: estado['posicion'] == punto and len(estado['muestras_recolectadas']) > 0,
        'efectos': lambda estado, contexto, punto: {
            'muestras_recolectadas': set(),
            'muestras_analizadas': estado['muestras_analizadas'] | estado['muestras_recolectadas']
        },
        'coste': 5,
        'tiempo': 8
    }
]
# En planificacion_metaheuristica.py

import random
import copy

class PlanificadorMetaheuristicoAG:
    def __init__(self, contexto, estado_inicial, objetivos, acciones, tam_poblacion=30, generaciones=50, tasa_mutacion=0.2):
        self.contexto = contexto
        self.estado_inicial = estado_inicial
        self.objetivos = objetivos
        self.acciones = acciones
        self.tam_poblacion = tam_poblacion
        self.generaciones = generaciones
        self.tasa_mutacion = tasa_mutacion
        self.mejor_plan = None
        self.mejor_coste = float('inf')
        self.mejor_tiempo = float('inf')
        
    def reparar_plan(self, plan):
        """
        Ajusta el plan para:
        1. Evitar visitar el mismo POI dos veces.
        2. Forzar ir a base y recargar si la energía no alcanza para la siguiente acción.
        """
        pois_vistos = set()
        nuevo_plan = []
        energia = self.estado_inicial['energia']
        posicion = self.estado_inicial['posicion']

        for i, (accion, param) in enumerate(plan):
            # 🔹 Calcular coste estimado de esta acción
            if accion == 'ir_a_poi' or accion == 'ir_a_base' or accion=="dejar_muestras":
                coste_accion, tiempo_accion, ruta = self.contexto.buscar(posicion, param)
                if coste_accion == float('inf') or not ruta:
                    continue  # saltar acciones imposibles

            else:  # recargar
                coste_accion = 0
            coste_base,_,_=self.contexto.buscar(posicion, self.contexto.base)
            # 🔹 Coste de regresar a la base desde la posición destino
            coste_vuelta=coste_accion+coste_base

            # 🔹 Si la energía no alcanza, forzar recarga antes de la acción
            if energia < coste_accion:
                nuevo_plan.append(('ir_a_base', self.contexto.base))
                nuevo_plan.append(('recargar', self.contexto.base))
                energia = self.estado_inicial['bateria_max']
                posicion = self.contexto.base

            # 🔹 Evitar visitar el mismo POI dos veces
            if accion == 'ir_a_poi' and param in pois_vistos:
                continue

            nuevo_plan.append((accion, param))

            # 🔹 Actualizar estado simulado
            if accion == 'ir_a_poi' or accion == 'ir_a_base':
                energia -= coste_accion
                posicion = param
                if accion == 'ir_a_poi':
                    pois_vistos.add(param)
            elif accion == 'recargar':
                energia = self.estado_inicial['bateria_max']

        # 🔹 Al final, asegurarse de regresar a la base
        if posicion != self.contexto.base:
            nuevo_plan.append(('ir_a_base', self.contexto.base))
            nuevo_plan.append(('recargar', self.contexto.base))

        return nuevo_plan

    def crear_plan_aleatorio(self, longitud_max=12):
        """Crea un plan aleatorio pero con coherencia contextual y sin repetir POIs."""
        plan = []
        energia = self.estado_inicial['energia']
        posicion = self.estado_inicial['posicion']
        muestras = set()

        # 🔹 Copia mutable de los puntos de interés disponibles
        pois_disponibles = list(self.contexto.puntos_interes)

        for _ in range(random.randint(4, longitud_max)):
            # Si la energía está baja, prioriza recargar
            if energia < 20:
                plan.append(("ir_a_base", self.contexto.base))
                plan.append(("recargar", self.contexto.base))
                energia = self.estado_inicial['bateria_max']
                posicion = self.contexto.base
                continue

            # Si tiene muestras, a veces decide ir a dejar
            if len(muestras) > 0 and random.random() < 0.2:
                plan.append(("ir_a_base", self.contexto.base))
                plan.append(("recargar", self.contexto.base))
                plan.append(("dejar_muestras", self.contexto.punto_recolectar))
                muestras.clear()
                posicion = self.contexto.punto_recolectar
                continue

            # 🔹 Si ya visitó todos los POIs, rompe el bucle
            if not pois_disponibles:
                break

            # 🔹 Elegir un POI nuevo y eliminarlo de la lista
            poi = random.choice(pois_disponibles)
            pois_disponibles.remove(poi)

            plan.append(("ir_a_poi", poi))
            muestras.add(poi)
            posicion = poi

        # 🔹 Final del plan: dejar muestras y volver a base
        if len(muestras) > 0:
            plan.append(("dejar_muestras", self.contexto.punto_recolectar))
        if posicion != self.contexto.base:
            plan.append(("ir_a_base", self.contexto.base))
            plan.append(("recargar", self.contexto.base))

       # print(6555, plan)
        return plan

    # DENTRO de la clase PlanificadorMetaheuristicoAG

    def simular_plan(self, plan):
        """Evalúa un plan y devuelve su coste, tiempo y el estado final."""
        estado = copy.deepcopy(self.estado_inicial)
        coste_total = 0
        tiempo_total = 0
        puntuacion_progreso = 0
        COSTE_FALLO = 10000 
        # print(estado["energia"])
        for accion_nombre, param in plan:
            accion_dict = next((a for a in self.acciones if a['nombre'] == accion_nombre), None)
            if not accion_dict:
                # print(1111111)
                return COSTE_FALLO, COSTE_FALLO, None # Devuelve None como estado si falla

            if accion_nombre :
                coste_mov, tiempo_mov, ruta = self.contexto.buscar(estado['posicion'], param)
                if not ruta or coste_mov == float('inf') or 100 < coste_mov:
                    # print(222,coste_mov,tiempo_mov,estado['energia'])
                    return COSTE_FALLO, COSTE_FALLO, None
                estado['posicion'] = param
                estado['energia'] -= coste_mov
                coste_total += coste_mov
                tiempo_total += tiempo_mov
                if accion_nombre == 'ir_a_poi' and param in self.contexto.puntos_interes:
                    if param not in estado['muestras_recolectadas']:
                        estado['muestras_recolectadas'].add(param)
                        puntuacion_progreso -= 800 
            else: # recargar, dejar_muestras
                if not accion_dict['precondiciones'](estado, self.contexto, param):
                    return COSTE_FALLO, COSTE_FALLO, None
                if accion_dict['efectos']:
                    nuevo_estado = accion_dict['efectos'](estado, self.contexto, param)
                    estado.update(nuevo_estado)
                coste_total += accion_dict.get('coste', 0)
                tiempo_total += accion_dict.get('tiempo', 0)
                if accion_nombre == 'dejar_muestras':
                    puntuacion_progreso -= 1000

        if not self.objetivos(estado):
            penalizacion = 0
            pois_pendientes = len(self.contexto.puntos_interes) - len(estado['muestras_recolectadas'])
            penalizacion += pois_pendientes * 1200
            if estado['posicion'] != self.contexto.base:
                penalizacion += 1500
            coste_total += penalizacion

        coste_final = coste_total + puntuacion_progreso
        
        # <-- CAMBIO CLAVE: Devolver también el estado final
        return coste_final, tiempo_total, estado

# En el método fitness
    def fitness(self, plan):
        coste, tiempo, _ = self.simular_plan(plan) # <-- Usar _ para ignorar el estado
        if coste == 10000: # O tu COSTE_FALLO
            return 0.0
        valor_combinado = coste + 0.1 * tiempo
        if valor_combinado<=0: 
            return 1
        return 1 / (1 + valor_combinado)

    def cruzar(self, plan1, plan2):
        if not plan1 or not plan2 or len(plan1)<5 or len(plan2)<5 : 
            return copy.deepcopy(plan1), copy.deepcopy(plan2)
        p = random.randint(1, min(len(plan1), len(plan2)) - 1)
        hijo1 = plan1[:p] + plan2[p:]
        hijo2 = plan2[:p] + plan1[p:]
        return hijo1, hijo2

    def mutar(self, plan):
        """Cambia aleatoriamente una acción."""
        if random.random() < self.tasa_mutacion and len(plan) > 0:
            idx = random.randint(0, len(plan) - 1)
            acciones_nombres = [a['nombre'] for a in self.acciones]
            nueva_accion = random.choice(acciones_nombres)
            param = None
            if nueva_accion == "ir_a_poi":
                param = random.choice(list(self.contexto.puntos_interes))
            elif nueva_accion in ["ir_a_base", "recargar"]:
                param = self.contexto.base
            elif nueva_accion == "dejar_muestras":
                param = self.contexto.punto_recolectar
            plan[idx] = (nueva_accion, param)
        return plan

    # def reparar_plan(self, plan):
    #     """Eliminar repeticiones innecesarias y forzar coherencia básica."""
    #     # Ejemplos: no visitar el mismo POI dos veces seguidas, 
    #     # asegurar recargar si hay muchos desplazamientos sin base, limitar repeticiones.
    #     pois_vistos = set()
    #     nuevo = []
    #     energia = self.estado_inicial['energia']
    #     for accion, param in plan:
    #         if accion == 'ir_a_poi':
    #             if param in pois_vistos:
    #                 continue
    #             pois_vistos.add(param)
    #             nuevo.append((accion, param))
    #             energia -= 10
    #         else:
    #             nuevo.append((accion, param))
    #             if accion == 'recargar':
    #                 energia = self.estado_inicial['bateria_max']
    #     # Si energía negativa, forzamos ir a base y recargar antes del final
    #     if energia < 0 and nuevo[-1][0] != 'recargar':
    #         nuevo.append(('ir_a_base', self.contexto.base))
    #         nuevo.append(('recargar', self.contexto.base))
    #     return nuevo

    def optimizar(self):
        """Ejecución principal del algoritmo genético."""
        poblacion = [self.crear_plan_aleatorio() for _ in range(self.tam_poblacion)]
        if not poblacion: return None

        for gen in range(self.generaciones):
            fitnesses = [self.fitness(p) for p in poblacion]
            
            # Guardar el mejor plan global (lógica existente)
            idx_mejor_gen = fitnesses.index(max(fitnesses))
            plan_mejor_gen = poblacion[idx_mejor_gen]
            # print(3333,plan_mejor_gen)
            # <-- CAMBIO CLAVE: Actualizar la llamada a simular_plan
            coste_actual, tiempo_actual, estado_final_mejor = self.simular_plan(plan_mejor_gen)
            
            if coste_actual < self.mejor_coste:
                self.mejor_coste = coste_actual
                self.mejor_tiempo = tiempo_actual
                self.mejor_plan = plan_mejor_gen
                print(f"Generación {gen}: Nuevo mejor plan{plan_mejor_gen}. Coste: {self.mejor_coste:.2f}, Tiempo: {self.mejor_tiempo:.2f}")

            # <-- NUEVA LÓGICA: Filtrar y guardar todos los planes válidos
            for plan in poblacion:
                coste, tiempo, estado_final = self.simular_plan(plan)
                # Si el plan es válido (no falló y cumple el objetivo)
                if coste != 10000 and self.objetivos(estado_final):
                    # Guardamos el plan como una tupla para que pueda ir en un set
                    self.planes_validos.add(tuple(plan))

            # Crear la siguiente generación (lógica existente)
            nueva_poblacion = [plan_mejor_gen] 
            while len(nueva_poblacion) < self.tam_poblacion:
                p1, p2 = random.sample(poblacion, 2)
                hijo1, hijo2 = self.cruzar(p1, p2)
                hijo1 = self.reparar_plan(self.mutar(hijo1))
                hijo2 = self.reparar_plan(self.mutar(hijo2))
                nueva_poblacion.append(self.mutar(hijo1))
                if len(nueva_poblacion) < self.tam_poblacion:
                    nueva_poblacion.append(self.mutar(hijo2))
            poblacion = nueva_poblacion

        print("\n✅ Optimización completada.")

        return self.mejor_plan

# class PlanificadorMetaheuristicoAG:
#     def __init__(self, contexto, estado_inicial, objetivos, acciones, tam_poblacion=30, generaciones=50, tasa_mutacion=0.2):
#         self.contexto = contexto
#         self.estado_inicial = estado_inicial
#         self.objetivos = objetivos
#         self.acciones = acciones
#         self.tam_poblacion = tam_poblacion
#         self.generaciones = generaciones
#         self.tasa_mutacion = tasa_mutacion
#         self.mejor_plan = None
#         self.mejor_coste = float('inf')
#         self.mejor_tiempo= float('inf')

#     def crear_plan_aleatorio(self, longitud=6):
#         """Crea un plan aleatorio combinando acciones posibles."""
        
#         acciones_nombres = [a['nombre'] for a in self.acciones]
#         plan = []
#         for _ in range(longitud):
#             accion = random.choice(acciones_nombres)
#             if accion == "ir_a_poi":
#                 poi = random.choice(self.contexto.puntos_interes)
#                 plan.append((accion, poi))
#             elif accion == "recargar":
#                 plan.append((accion, self.contexto.base))
#             elif accion == "dejar_muestras":
#                 plan.append((accion, self.contexto.punto_recolectar))
#             else:
#                 plan.append((accion, None))
#         return plan

#     def simular_plan(self, plan):
#         """Evalúa un plan ejecutando las acciones sobre una copia del estado."""
        
#         estado = copy.deepcopy(self.estado_inicial)
#         coste_total = 0
#         tiempo_total= 0 

#         for accion_nombre, param in plan:
#             accion = next((a for a in self.acciones if a['nombre'] == accion_nombre), None)
#             if not accion:
#                 return float('inf'), float('inf')

#             if not accion['precondiciones'](estado, param):
#                 return float('inf'), float('inf')

#             nuevo_estado = copy.deepcopy(estado)
#             nuevo_estado.update(accion['efectos'](estado, param))

#             coste = accion.get('coste', 0)
#             coste_total += coste
            
#             tiempo = accion.get('tiempo', 0)
#             tiempo_total += tiempo
            
#             estado = nuevo_estado

#         if not self.objetivos(estado):
#             coste_total += 1000  

#         return coste_total,tiempo_total

#     def fitness(self, plan):
#         """Mayor fitness para menor coste."""
        
#         coste, tiempo = self.simular_plan(plan)
#         return 1 / (1 + coste )  , 1 / (1 + tiempo)

#     def cruzar(self, plan1, plan2):
#         """Cruce simple de un punto."""
        
#         punto = random.randint(1, len(plan1)-1)
#         hijo = plan1[:punto] + plan2[punto:]
#         return hijo

#     def mutar(self, plan):
#         """Cambia aleatoriamente una acción."""
        
#         if random.random() < self.tasa_mutacion:
#             idx = random.randint(0, len(plan)-1)
#             acciones_nombres = [a['nombre'] for a in self.acciones]
#             accion = random.choice(acciones_nombres)
#             if accion == "ir_a_poi":
#                 poi = random.choice(self.contexto.puntos_interes)
#                 plan[idx] = (accion, poi)
#             else:
#                 plan[idx] = (accion, None)
#         return plan

#     def optimizar(self):
#         """Ejecución principal del algoritmo genético."""
        
#         poblacion = [self.crear_plan_aleatorio() for _ in range(self.tam_poblacion)]

#         for gen in range(self.generaciones):
#             fitnesses = [self.fitness(p) for p in poblacion]
#             mejores_idx = sorted(range(len(poblacion)), key=lambda i: fitnesses[i], reverse=True)

#             mejor_actual = poblacion[mejores_idx[0]]
#             print(fitnesses[mejores_idx[0]])
#             if fitnesses[mejores_idx[0]][0]!=0 and fitnesses[mejores_idx[0]][0]!=0:
#                 mejor_coste,mejor_tiempo = 1 / fitnesses[mejores_idx[0]][0] - 1,1 / fitnesses[mejores_idx[0]][1] - 1
#             else:
#                 mejor_coste,mejor_tiempo=-1,-1
#             if mejor_coste < self.mejor_coste or mejor_tiempo< self.mejor_tiempo:
#                 self.mejor_coste = mejor_coste
#                 self.mejor_tiempo=mejor_tiempo
#                 self.mejor_plan = mejor_actual
#                 print(f"Generación {gen}: nuevo mejor plan con coste {mejor_coste:.2f} y tiempo {mejor_tiempo:.2f}")

#             nueva_poblacion = []
#             for _ in range(self.tam_poblacion // 2):
#                 p1, p2 = random.sample(poblacion, 2)
#                 hijo1 = self.mutar(self.cruzar(p1, p2))
#                 hijo2 = self.mutar(self.cruzar(p2, p1))
#                 nueva_poblacion += [hijo1, hijo2]
#             poblacion = nueva_poblacion

#         print("\n✅ Optimización completada.")
#         print("Mejor plan encontrado:")
#         for paso in self.mejor_plan:
#             print("  -", paso)
#         print(f"Coste total estimado: {self.mejor_coste:.2f}, tiempo total estimado{self.mejor_tiempo:.2f}")

#         return self.mejor_plan


ACCIONES_PLANIFICADOR = [
    {
        'nombre': 'ir_a_poi',
        # Precondición: tener energía para al menos un paso
        'precondiciones': lambda estado, contexto, poi: estado['energia'] > 0,
        # Los efectos se calcularán dinámicamente en simulacion
        'efectos': None, 
    },
    {
        'nombre': 'ir_a_base',
        'precondiciones': lambda estado, contexto, base: estado['energia'] > 0  and estado['posicion'] != base,
        'efectos': None,
    },
    {
        'nombre': 'recargar',
        'precondiciones': lambda estado, contexto, base: estado['posicion'] == base and estado['energia'] <  30 ,
        'efectos': lambda estado, contexto, base: {
            'energia': estado['bateria_max'],
        },
        'coste': 0, # Coste fijo de la acción de recargar
        'tiempo': 10 # Tiempo fijo de la acción de recargar
    },
    {
        'nombre': 'dejar_muestras', 
        'precondiciones': lambda estado, contexto, punto: estado['posicion'] == punto and len(estado['muestras_recolectadas']) > 0,
        'efectos': lambda estado, contexto, punto: {
            'muestras_recolectadas': set(),
            'muestras_analizadas': estado['muestras_analizadas'] | estado['muestras_recolectadas']
        },
        'coste': 5,
        'tiempo': 8
    }]
import math
import random
import copy

# class PlanificadorMetaheuristicoSA:
#     """
#     Optimizador de planes usando el algoritmo de Recocido Simulado (Simulated Annealing).
#     """
class PlanificadorMetaheuristicoSA:
    def __init__(self, contexto, estado_inicial, objetivos, acciones, temp_inicial=1000, temp_final=1, enfriamiento=0.995, longitud_min=5, longitud_max=9):
        self.contexto = contexto
        self.estado_inicial = estado_inicial
        self.objetivos = objetivos
        self.acciones = acciones
        
        self.temp_inicial = temp_inicial
        self.temp_final = temp_final
        self.enfriamiento = enfriamiento
        self.longitud_min = longitud_min
        self.longitud_max = longitud_max
        self.mejor_solucion = None
        self.mejor_coste = float('inf')

    def reparar_plan(self, plan):
        """
        Ajusta el plan para:
        1. Evitar visitar el mismo POI dos veces.
        2. Forzar ir a base y recargar si la energía no alcanza para la siguiente acción.
        3. Evitar secuencias consecutivas de 'ir_a_base' + 'recargar' repetidas.
        """
        pois_vistos = set()
        nuevo_plan = []
        energia = self.estado_inicial['energia']
        posicion = self.estado_inicial['posicion']

        i = 0
        while i < len(plan):
            accion, param = plan[i]

            if accion in ['ir_a_poi', 'ir_a_base', 'dejar_muestras']:
                coste_accion, tiempo_accion, ruta = self.contexto.buscar(posicion, param)
            else:  # recargar
                coste_accion = 0

            coste_base, _, _ = self.contexto.buscar(posicion, self.contexto.base)
            coste_vuelta = coste_accion + coste_base

            # Forzar ir a base y recargar si no hay energía suficiente
            if energia < coste_vuelta + coste_accion:
                nuevo_plan.append(('ir_a_base', self.contexto.base))
                nuevo_plan.append(('recargar', self.contexto.base))
                energia = self.estado_inicial['bateria_max']
                posicion = self.contexto.base

            # Evitar POIs repetidos
            if accion == 'ir_a_poi' and param in pois_vistos:
                i += 1
                continue

            # Evitar repeticiones consecutivas de 'ir_a_base' + 'recargar'
            if accion == 'ir_a_base' and i + 1 < len(plan) and plan[i + 1][0] == 'recargar':
                if len(nuevo_plan) >= 2 and nuevo_plan[-2][0] == 'ir_a_base' and nuevo_plan[-1][0] == 'recargar':
                    # Ya existe la secuencia, saltarla
                    i += 2
                    continue

            nuevo_plan.append((accion, param))

            # Actualizar estado simulado
            if accion in ['ir_a_poi', 'ir_a_base']:
                energia -= coste_accion
                posicion = param
                if accion == 'ir_a_poi':
                    pois_vistos.add(param)
            elif accion == 'recargar':
                energia = self.estado_inicial['bateria_max']

            i += 1

        return nuevo_plan

    
    def _crear_plan_aleatorio(self):
        plan = []
        estado = copy.deepcopy(self.estado_inicial)  # Para saber la posición actual
        
        # Visitar POIs
        pois_no_visitados = self.contexto.puntos_interes.copy()
        random.shuffle(pois_no_visitados)
        for poi in pois_no_visitados:
            plan.append(('ir_a_poi', poi))
            estado['posicion'] = poi
            estado['energia'] -= 10  # Simulación aproximada de energía

        # Acciones extra de recarga: solo si no estamos ya en la base
        acciones_extra = random.randint(1, 3)
        for _ in range(acciones_extra):
            if estado['posicion'] != self.contexto.base:
                plan.append(('ir_a_base', self.contexto.base))
                plan.append(('recargar', self.contexto.base))
                estado['posicion'] = self.contexto.base
                estado['energia'] = self.estado_inicial['bateria_max']

        # Acciones finales
        plan.append(('dejar_muestras', self.contexto.punto_recolectar))

        plan.append(('ir_a_base', self.contexto.base))
        plan.append(('recargar', self.contexto.base))
        plan=self.reparar_plan(plan)
        return plan


    def _crear_accion_aleatoria(self):
        """Crea una acción o un bloque de acciones aleatorio."""
            # 70% de probabilidad de añadir una acción de POI
        if random.random() < 0.7:
            poi = random.choice(self.contexto.puntos_interes)
            return [('ir_a_poi', poi)]
        else:
            # 30% de probabilidad de añadir el bloque de recarga
            return [
                ('ir_a_base', self.contexto.base),
                ('recargar', self.contexto.base)
        ]

    def _generar_vecino(self, solucion_actual):
        """Genera una solución vecina con operadores que respetan los bloques."""
        vecino = copy.deepcopy(solucion_actual)
        
        if random.random() < 0.3 and len(vecino) < self.longitud_max:  # 30% de probabilidad de insertar
            idx = random.randint(0, len(vecino))
            bloque_accion = self._crear_accion_aleatoria()
            # Insertamos el bloque en la posición aleatoria
            for i, accion in enumerate(bloque_accion):
                vecino.insert(idx + i, accion)
                
        elif random.random() < 0.6 and len(vecino) > self.longitud_min: # 60% de probabilidad de eliminar
            # Eliminar un bloque completo si es de recarga, o una acción normal
            idx = random.randint(0, len(vecino) - 1)
            if vecino[idx][0] == 'ir_a_base' and idx + 1 < len(vecino) and vecino[idx+1][0] == 'recargar':
                vecino.pop(idx+1) # Eliminar recargar
                vecino.pop(idx)   # Eliminar ir_a_base
            else:
                vecino.pop(idx)
                
        else: # 10% de probabilidad de cambiar (mutación)
            if vecino:
                idx = random.randint(0, len(vecino) - 1)
                bloque_accion = self._crear_accion_aleatoria()
                # Reemplazamos la acción en idx por el nuevo bloque
                vecino.pop(idx)
                for i, accion in enumerate(bloque_accion):
                    vecino.insert(idx + i, accion)
            
        return vecino
    
    def _calcular_coste_plan(self, plan):
        """Evalúa un plan con verificación estricta y penalizaciones de redundancia."""
        estado = copy.deepcopy(self.estado_inicial)
        coste_total = 0
        tiempo_total = 0
        
        pois_visitados = set()
        penalizacion_redundancia = 0

        for i, (accion_nombre, param) in enumerate(plan):
            accion = next((a for a in self.acciones if a['nombre'] == accion_nombre), None)
            if not accion:
                return float('inf')
            
            # --- NUEVA REGLA: Penalizar redundancias ---
            # 1. Penalizar ir a un sitio donde ya estás
            # print(accion_nombre,estado['posicion'],param)
            if estado['posicion']==param:
                return float("inf")
            if accion_nombre == 'ir_a_base' and estado['posicion'] == param:
                penalizacion_redundancia += 300 # Penalización por ir a la base estando en ella
                # print(f"  ⚠️ Penalización: 'ir_a_base' estando ya en la base.")
                return float('inf')

            # 2. Penalizar intentar recargar con la batería casi llena
            if accion_nombre == 'recargar' and estado['energia'] > estado['bateria_max'] * 0.3:
                penalizacion_redundancia += 400 # Penalización por recarga innecesaria
                return float('inf')
                # print(f"  ⚠️ Penalización: 'recargar' con energía alta ({estado['energia']}).")

            # VERIFICAR PRECONDICIONES (esto sigue siendo crucial)
            precondiciones_cumplidas = accion['precondiciones'](estado, self.contexto, param)
            
            if not precondiciones_cumplidas:
                # Si falla una precondición, el plan es inválido
                return float('inf')

            # APLICAR EFECTOS
            if accion['efectos']:
                nuevos_efectos = accion['efectos'](estado, self.contexto, param)
                estado.update(nuevos_efectos)
                
            # REGISTRAR POIs VISITADOS
            if accion_nombre == 'ir_a_poi' and param:
                pois_visitados.add(param)
                    
            coste_total += accion.get('coste', 0)
            tiempo_total += accion.get('tiempo', 0)

        # VERIFICAR OBJETIVO
        todos_pois = set(self.contexto.puntos_interes)
        pois_faltantes = todos_pois - pois_visitados
        penalizacion_pois = len(pois_faltantes) * 500

        if not self.objetivos(estado):
            penalizacion_pois += 1000

        # Añadimos la nueva penalización al coste final
        coste_unico = (0.7 * coste_total) + (0.3 * tiempo_total) + penalizacion_pois + penalizacion_redundancia
        
        return coste_unico


    def optimizar(self):
        """Ejecuta el algoritmo de Recocido Simulado para planificación."""
        solucion_actual = self._crear_plan_aleatorio()
        coste_actual = self._calcular_coste_plan(solucion_actual)

        self.mejor_solucion = copy.deepcopy(solucion_actual)
        self.mejor_coste = coste_actual
        
        temperatura = self.temp_inicial
        iteracion = 0
        
        while temperatura > self.temp_final:
            vecino = self._generar_vecino(solucion_actual)
            coste_vecino = self._calcular_coste_plan(vecino)
            if coste_vecino==float("inf"):
                temperatura *= self.enfriamiento
                iteracion += 1
                continue
            delta_coste = coste_vecino - coste_actual

            if delta_coste < 0 or random.random() < math.exp(-delta_coste / temperatura):
                solucion_actual = vecino

                coste_actual = coste_vecino

                if coste_actual < self.mejor_coste:
                    self.mejor_coste = coste_actual
                    self.mejor_solucion = copy.deepcopy(solucion_actual)
                    print(f"SA (Iter {iteracion}, Temp {temperatura:.2f}): Nuevo mejor coste: {self.mejor_coste:.2f}")

            temperatura *= self.enfriamiento
            iteracion += 1

        print("\n✅ Optimización con Recocido Simulado finalizada.")
        print("Mejor plan encontrado:")
        for paso in self.mejor_solucion:
            print("  -", paso)
        print(f"Coste combinado estimado: {self.mejor_coste:.2f}")
        
        return self.mejor_solucion
    
def crear_plan(estado_inicial, es_objetivo, acciones, contexto):
        """
        Crea un plan usando metaheurísticas combinando AG y SA
        """
        print("🧠 Creando plan con metaheurísticas...")
        
        # Probar primero con Algoritmo Genético
        planificador_ag = PlanificadorMetaheuristicoAG(
            contexto=contexto,
            estado_inicial=estado_inicial,
            objetivos=es_objetivo,
            acciones=acciones,
            tam_poblacion=20,
            generaciones=30
        )
        
        plan_ag = planificador_ag.optimizar()
        
        # Refinar con Recocido Simulado
        if plan_ag:
            planificador_sa = PlanificadorMetaheuristicoSA(
                contexto=contexto,
                estado_inicial=estado_inicial,
                objetivos=es_objetivo,
                acciones=acciones,
                longitud_plan=len(plan_ag)
            )
            plan_final = planificador_sa.optimizar()
            print(type(plan_final))
            print(plan_final)
            return plan_final
        
        return None