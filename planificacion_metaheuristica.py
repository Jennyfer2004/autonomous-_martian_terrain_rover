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
        self.mejor_tiempo= float('inf')

    def crear_plan_aleatorio(self, longitud=6):
        """Crea un plan aleatorio combinando acciones posibles."""
        
        acciones_nombres = [a['nombre'] for a in self.acciones]
        plan = []
        for _ in range(longitud):
            accion = random.choice(acciones_nombres)
            if accion == "ir_a_poi":
                poi = random.choice(self.contexto.puntos_interes)
                plan.append((accion, poi))
            elif accion == "recargar":
                plan.append((accion, self.contexto.base))
            elif accion == "dejar_muestras":
                plan.append((accion, self.contexto.punto_recolectar))
            else:
                plan.append((accion, None))
        return plan

    def simular_plan(self, plan):
        """Evalúa un plan ejecutando las acciones sobre una copia del estado."""
        
        estado = copy.deepcopy(self.estado_inicial)
        coste_total = 0
        tiempo_total= 0 

        for accion_nombre, param in plan:
            accion = next((a for a in self.acciones if a['nombre'] == accion_nombre), None)
            if not accion:
                return float('inf')

            if not accion['precondiciones'](estado, param):
                return float('inf')

            nuevo_estado = copy.deepcopy(estado)
            nuevo_estado.update(accion['efectos'](estado, param))

            coste = accion.get('coste', 0)
            coste_total += coste
            
            tiempo = accion.get('tiempo', 0)
            tiempo_total += tiempo
            
            estado = nuevo_estado

        if not self.objetivos(estado):
            coste_total += 1000  

        return coste_total,tiempo_total

    def fitness(self, plan):
        """Mayor fitness para menor coste."""
        
        coste, tiempo = self.simular_plan(plan)
        return 1 / (1 + coste )  , 1 / (1 + tiempo)

    def cruzar(self, plan1, plan2):
        """Cruce simple de un punto."""
        
        punto = random.randint(1, len(plan1)-1)
        hijo = plan1[:punto] + plan2[punto:]
        return hijo

    def mutar(self, plan):
        """Cambia aleatoriamente una acción."""
        
        if random.random() < self.tasa_mutacion:
            idx = random.randint(0, len(plan)-1)
            acciones_nombres = [a['nombre'] for a in self.acciones]
            accion = random.choice(acciones_nombres)
            if accion == "ir_a_poi":
                poi = random.choice(self.contexto.puntos_interes)
                plan[idx] = (accion, poi)
            else:
                plan[idx] = (accion, None)
        return plan

    def optimizar(self):
        """Ejecución principal del algoritmo genético."""
        
        poblacion = [self.crear_plan_aleatorio() for _ in range(self.tam_poblacion)]

        for gen in range(self.generaciones):
            fitnesses = [self.fitness(p) for p in poblacion]
            mejores_idx = sorted(range(len(poblacion)), key=lambda i: fitnesses[i], reverse=True)

            mejor_actual = poblacion[mejores_idx[0]]
            mejor_coste,mejor_tiempo = 1 / fitnesses[mejores_idx[0]] - 1
            
            if mejor_coste < self.mejor_coste or mejor_tiempo< self.mejor_tiempo:
                self.mejor_coste = mejor_coste
                self.mejor_tiempo=mejor_tiempo
                self.mejor_plan = mejor_actual
                print(f"Generación {gen}: nuevo mejor plan con coste {mejor_coste:.2f} y tiempo {mejor_tiempo:.2f}")

            nueva_poblacion = []
            for _ in range(self.tam_poblacion // 2):
                p1, p2 = random.sample(poblacion, 2)
                hijo1 = self.mutar(self.cruzar(p1, p2))
                hijo2 = self.mutar(self.cruzar(p2, p1))
                nueva_poblacion += [hijo1, hijo2]
            poblacion = nueva_poblacion

        print("\n✅ Optimización completada.")
        print("Mejor plan encontrado:")
        for paso in self.mejor_plan:
            print("  -", paso)
        print(f"Coste total estimado: {self.mejor_coste:.2f}, tiempo total estimado{self.mejor_tiempo:.2f}")

        return self.mejor_plan


import math
import random
import copy

class PlanificadorMetaheuristicoSA:
    """
    Optimizador de planes usando el algoritmo de Recocido Simulado (Simulated Annealing).
    """
    def __init__(self, contexto, estado_inicial, objetivos, acciones, temp_inicial=1000, temp_final=1, enfriamiento=0.995, longitud_plan=6):
        self.contexto = contexto
        self.estado_inicial = estado_inicial
        self.objetivos = objetivos
        self.acciones = acciones
        
        self.temp_inicial = temp_inicial
        self.temp_final = temp_final
        self.enfriamiento = enfriamiento
        self.mejor_solucion = None
        self.mejor_coste = float('inf')

    def _crear_plan_aleatorio(self):
        """Crea un plan aleatorio combinando acciones posibles."""
        
        acciones_nombres = [a['nombre'] for a in self.acciones]
        plan = []
        for _ in range(self.longitud_plan):
            accion = random.choice(acciones_nombres)
            if accion == "ir_a_poi":
                poi = random.choice(self.contexto.puntos_interes)
                plan.append((accion, poi))
            elif accion == "recargar":
                plan.append((accion, self.contexto.base))
            elif accion == "dejar_muestras":
                plan.append((accion, self.contexto.punto_recolectar))
            else:
                plan.append((accion, None))
        return plan

    def _generar_vecino(self, solucion_actual):
        """Genera una solución vecina aplicando una mutación simple."""
        vecino = copy.deepcopy(solucion_actual)
        if len(vecino) == 0:
            return vecino
        
        idx = random.randint(0, len(vecino) - 1)
        acciones_nombres = [a['nombre'] for a in self.acciones]
        nueva_accion_nombre = random.choice(acciones_nombres)

        if nueva_accion_nombre == "ir_a_poi":
            poi = random.choice(self.contexto.puntos_interes)
            vecino[idx] = (nueva_accion_nombre, poi)
        elif nueva_accion_nombre == "recargar":
            vecino[idx] = (nueva_accion_nombre, self.contexto.base)
        elif nueva_accion_nombre == "dejar_muestras":
            vecino[idx] = (nueva_accion_nombre, self.contexto.punto_recolectar)
        else:
            vecino[idx] = (nueva_accion_nombre, None)
            
        return vecino

    def _calcular_coste_plan(self, plan):
        """Evalúa un plan y devuelve un coste único combinando coste y tiempo."""
        estado = copy.deepcopy(self.estado_inicial)
        coste_total = 0
        tiempo_total = 0
        penalizacion = 1000

        for accion_nombre, param in plan:
            accion = next((a for a in self.acciones if a['nombre'] == accion_nombre), None)
            if not accion or not accion['precondiciones'](estado, param):
                return float('inf')

            estado.update(accion['efectos'](estado, param))
            coste_total += accion.get('coste', 0)
            tiempo_total += accion.get('tiempo', 0)

        if not self.objetivos(estado):
            coste_total += penalizacion

        # Combinamos coste y tiempo. Ajusta los pesos según sea necesario.
        coste_unico = (0.7 * coste_total) + (0.3 * tiempo_total)
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