import random
import copy
import math

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
        Ajusta el plan para eliminar errores
        """
        pois_vistos = set()
        nuevo_plan = []
        energia = self.estado_inicial['energia']
        posicion = self.estado_inicial['posicion']

        for i, (accion, param) in enumerate(plan):

            if accion == 'ir_a_poi' or accion == 'ir_a_base' or accion=="dejar_muestras":
                coste_accion, tiempo_accion, ruta = self.contexto.buscar(posicion, param)
                if coste_accion == float('inf') or not ruta:
                    continue  

            else:  
                coste_accion = 0
            coste_base,_,_=self.contexto.buscar(posicion, self.contexto.base)

            coste_vuelta=coste_accion+coste_base

            if energia < coste_vuelta:
                nuevo_plan.append(('ir_a_base', self.contexto.base))
                nuevo_plan.append(('recargar', self.contexto.base))
                energia = self.estado_inicial['bateria_max']
                posicion = self.contexto.base

            if accion == 'ir_a_poi' and param in pois_vistos:
                continue

            nuevo_plan.append((accion, param))

            if accion == 'ir_a_poi' or accion == 'ir_a_base':
                energia -= coste_accion
                posicion = param
                if accion == 'ir_a_poi':
                    pois_vistos.add(param)
            elif accion == 'recargar':
                energia = self.estado_inicial['bateria_max']

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

        pois_disponibles = list(self.contexto.puntos_interes)

        for _ in range(random.randint(4, longitud_max)):
            if energia < 20:
                plan.append(("ir_a_base", self.contexto.base))
                plan.append(("recargar", self.contexto.base))
                energia = self.estado_inicial['bateria_max']
                posicion = self.contexto.base
                continue

            if len(muestras) > 0 and random.random() < 0.2:
                plan.append(("ir_a_base", self.contexto.base))
                plan.append(("recargar", self.contexto.base))
                plan.append(("dejar_muestras", self.contexto.punto_recolectar))
                muestras.clear()
                posicion = self.contexto.punto_recolectar
                continue

            if not pois_disponibles:
                break

            poi = random.choice(pois_disponibles)
            pois_disponibles.remove(poi)

            plan.append(("ir_a_poi", poi))
            muestras.add(poi)
            posicion = poi

        if len(muestras) > 0:
            plan.append(("dejar_muestras", self.contexto.punto_recolectar))
        if posicion != self.contexto.base:
            plan.append(("ir_a_base", self.contexto.base))
            plan.append(("recargar", self.contexto.base))

        return plan


    def simular_plan(self, plan):
        """Evalúa un plan y devuelve su coste, tiempo y el estado final."""
        estado = copy.deepcopy(self.estado_inicial)
        coste_total = 0
        tiempo_total = 0
        puntuacion_progreso = 0
        COSTE_FALLO = 10000 

        for accion_nombre, param in plan:
            accion_dict = next((a for a in self.acciones if a['nombre'] == accion_nombre), None)
            if not accion_dict:

                return COSTE_FALLO, COSTE_FALLO, None 

            if accion_nombre :
                coste_mov, tiempo_mov, ruta = self.contexto.buscar(estado['posicion'], param)
                if not ruta or coste_mov == float('inf') or 100 < coste_mov:

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
        
        return coste_final, tiempo_total, estado

    def fitness(self, plan):
        """Calcula el fitness"""
        coste, tiempo, _ = self.simular_plan(plan) 
        if coste == 10000: 
            return 0.0
        valor_combinado = coste + 0.1 * tiempo
        if valor_combinado<=0: 
            return 1
        return 1 / (1 + valor_combinado)

    def cruzar(self, plan1, plan2):
        """Ejecuta el cruce"""
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


    def optimizar(self):
        """Ejecución principal del algoritmo genético."""
        poblacion = [self.crear_plan_aleatorio() for _ in range(self.tam_poblacion)]
        if not poblacion: return None

        for gen in range(self.generaciones):
            fitnesses = [self.fitness(p) for p in poblacion]
            
            idx_mejor_gen = fitnesses.index(max(fitnesses))
            plan_mejor_gen = poblacion[idx_mejor_gen]
            coste_actual, tiempo_actual, estado_final_mejor = self.simular_plan(plan_mejor_gen)
            
            if coste_actual < self.mejor_coste:
                self.mejor_coste = coste_actual
                self.mejor_tiempo = tiempo_actual
                self.mejor_plan = plan_mejor_gen
                print(f"Generación {gen}: Nuevo mejor plan{plan_mejor_gen}. Coste: {self.mejor_coste:.2f}, Tiempo: {self.mejor_tiempo:.2f}")

            for plan in poblacion:
                coste, tiempo, estado_final = self.simular_plan(plan)
                if coste != 10000 and self.objetivos(estado_final):
                    self.planes_validos.add(tuple(plan))

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
        Ajusta el plan para arreglar errores"""
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

            if energia < coste_vuelta + coste_accion:
                nuevo_plan.append(('ir_a_base', self.contexto.base))
                nuevo_plan.append(('recargar', self.contexto.base))
                energia = self.estado_inicial['bateria_max']
                posicion = self.contexto.base

            if accion == 'ir_a_poi' and param in pois_vistos:
                i += 1
                continue

            if accion == 'ir_a_base' and i + 1 < len(plan) and plan[i + 1][0] == 'recargar':
                if len(nuevo_plan) >= 2 and nuevo_plan[-2][0] == 'ir_a_base' and nuevo_plan[-1][0] == 'recargar':
                    i += 2
                    continue

            nuevo_plan.append((accion, param))

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
        estado = copy.deepcopy(self.estado_inicial)  
        
        pois_no_visitados = self.contexto.puntos_interes.copy()
        random.shuffle(pois_no_visitados)
        for poi in pois_no_visitados:
            plan.append(('ir_a_poi', poi))
            estado['posicion'] = poi
            estado['energia'] -= 10  

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
        if random.random() < 0.7:
            poi = random.choice(self.contexto.puntos_interes)
            return [('ir_a_poi', poi)]
        else:
            return [
                ('ir_a_base', self.contexto.base),
                ('recargar', self.contexto.base)
        ]

    def _generar_vecino(self, solucion_actual):
        """Genera una solución vecina con operadores que respetan los bloques."""
        vecino = copy.deepcopy(solucion_actual)
        
        if random.random() < 0.3 and len(vecino) < self.longitud_max:  
            idx = random.randint(0, len(vecino))
            bloque_accion = self._crear_accion_aleatoria()
            for i, accion in enumerate(bloque_accion):
                vecino.insert(idx + i, accion)
                
        elif random.random() < 0.6 and len(vecino) > self.longitud_min: 
            idx = random.randint(0, len(vecino) - 1)
            if vecino[idx][0] == 'ir_a_base' and idx + 1 < len(vecino) and vecino[idx+1][0] == 'recargar':
                vecino.pop(idx+1) 
                vecino.pop(idx)  
            else:
                vecino.pop(idx)
                
        else: # 10% de probabilidad de cambiar (mutación)
            if vecino:
                idx = random.randint(0, len(vecino) - 1)
                bloque_accion = self._crear_accion_aleatoria()
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
            
            if estado['posicion']==param:
                return float("inf")
            if accion_nombre == 'ir_a_base' and estado['posicion'] == param:
                penalizacion_redundancia += 300 
                return float('inf')

            if accion_nombre == 'recargar' and estado['energia'] > estado['bateria_max'] * 0.3:
                penalizacion_redundancia += 400 
                return float('inf')

            precondiciones_cumplidas = accion['precondiciones'](estado, self.contexto, param)
            
            if not precondiciones_cumplidas:
                return float('inf')

            if accion['efectos']:
                nuevos_efectos = accion['efectos'](estado, self.contexto, param)
                estado.update(nuevos_efectos)
                
            if accion_nombre == 'ir_a_poi' and param:
                pois_visitados.add(param)
                    
            coste_total += accion.get('coste', 0)
            tiempo_total += accion.get('tiempo', 0)

        todos_pois = set(self.contexto.puntos_interes)
        pois_faltantes = todos_pois - pois_visitados
        penalizacion_pois = len(pois_faltantes) * 500

        if not self.objetivos(estado):
            penalizacion_pois += 1000

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

        print("\n Optimización con Recocido Simulado finalizada.")
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
        
        planificador_ag = PlanificadorMetaheuristicoAG(
            contexto=contexto,
            estado_inicial=estado_inicial,
            objetivos=es_objetivo,
            acciones=acciones,
            tam_poblacion=20,
            generaciones=30
        )
        
        plan_ag = planificador_ag.optimizar()
        
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