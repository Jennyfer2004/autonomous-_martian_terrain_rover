import time
import copy
from collections import deque

class PlanificadorBFS:
    def __init__(self, contexto, estado_inicial, objetivos, acciones):
        self.contexto = contexto
        self.estado_inicial = estado_inicial
        self.objetivos = objetivos
        self.acciones = acciones
        self.mejor_plan = None
        self.mejor_coste = float('inf')
        self.nodos_explorados = 0

    def es_objetivo(self,estado,plan_actual):
            """
            La misión se cumple si:
            1. Se han visitado todos los POIs.
            2. Se han dejado todas las muestras.
            3. El rover está en la base.
            """

            todos_pois_analizados = len(estado['muestras_analizadas']) == len(self.contexto.puntos_interes)
            en_base_final = estado['posicion'] == self.contexto.base
            
            return todos_pois_analizados and en_base_final
        
    def resolver(self):
        """Búsqueda en anchura para encontrar el plan óptimo."""
        
        print("🧠 Iniciando búsqueda BFS...")
        start_time = time.time()
        
        cola = deque([(copy.deepcopy(self.estado_inicial), [], 0)])
        
        estados_visitados = set()
        
        while cola or len(plan_actual)>=10:
            estado_actual, plan_actual, coste_actual = cola.popleft()
            self.nodos_explorados += 1
            
            if plan_actual!=[]:
                estado_hash = self._hash_estado(plan_actual)
                if str(estado_hash) in estados_visitados:
                    continue
                estados_visitados.add(str(estado_hash))
            
            if self.es_objetivo(estado_actual,plan_actual):
                end_time = time.time()
                print(f"\n ¡Plan óptimo encontrado!")
                print(f" Nodos explorados: {self.nodos_explorados}")
                print(f"⏱ Tiempo de búsqueda: {end_time - start_time:.4f} segundos")
                print(f" Coste total del plan: {coste_actual}")
                self.mejor_plan = plan_actual
                self.mejor_coste = coste_actual

                return self.mejor_plan
            
            for accion in self._acciones_posibles(estado_actual):

                nombre_accion, parametro = accion
                nuevo_estado = self._aplicar_accion(estado_actual, nombre_accion, parametro,plan_actual)

                if nuevo_estado is not None:
                    nuevo_coste = coste_actual + self._coste_accion(estado_actual, nombre_accion, parametro)
                    nuevo_plan = plan_actual + [accion]
                    cola.append((nuevo_estado, nuevo_plan, nuevo_coste))
        
        print("\n❌ No se pudo encontrar un plan que resuelva el problema.")
        return None
    

    def _hash_estado(self, estado):
        return (estado)
    

    def _acciones_posibles(self, estado):
        """
        Devuelve una lista de TODAS las acciones válidas para el estado actual.
        """
        acciones_posibles = []
        
        for accion_dict in self.acciones:
            nombre_accion = accion_dict['nombre']
            parametro = None

            if nombre_accion == 'ir_a_poi':
                for poi in self.contexto.puntos_interes:
                    if poi not in estado['muestras_recolectadas'] or poi not in estado['muestras_recolectadas']:
                        parametro = poi
                        if accion_dict['precondiciones'](estado, self.contexto, parametro):
                            acciones_posibles.append((nombre_accion, parametro))
            
            elif nombre_accion == 'dejar_muestras':
                parametro = self.contexto.punto_recolectar
                if len(estado['muestras_recolectadas']) > 0 : 

                    acciones_posibles.append((nombre_accion, parametro))
            
            elif nombre_accion == 'ir_a_base':
                parametro = self.contexto.base
                if accion_dict['precondiciones'](estado, self.contexto, parametro):
                    acciones_posibles.append((nombre_accion, parametro))
            
            elif nombre_accion == 'recargar':
                parametro = self.contexto.base
                if accion_dict['precondiciones'](estado, self.contexto, parametro):
                    acciones_posibles.append((nombre_accion, parametro))

        return acciones_posibles

    def _aplicar_accion(self, estado, nombre_accion, parametro,plan):
        nuevo_estado = copy.deepcopy(estado)
        
        if nombre_accion in ['ir_a_poi', 'ir_a_base']:
            coste, _, ruta = self.contexto.buscar(estado['posicion'], parametro)
            if coste == float('inf') or not ruta or estado['energia'] < coste:
                return None
            
            nuevo_estado['posicion'] = parametro
            nuevo_estado['energia'] -= coste
            
            if nombre_accion == 'ir_a_poi':
                nuevo_estado['muestras_recolectadas'].add(parametro)
                
        else:           
            coste, _, ruta = self.contexto.buscar(estado['posicion'], parametro)
            if coste == float('inf') or not ruta or estado['energia'] < coste:
                return None
            nuevo_estado['posicion'] = parametro
            nuevo_estado['energia'] -= coste
            
            accion_dict = next((a for a in self.acciones if a['nombre'] == nombre_accion), None)
            if accion_dict and accion_dict['efectos']:
                efectos = accion_dict['efectos'](nuevo_estado, self.contexto, parametro)
                nuevo_estado.update(efectos)
        
        return nuevo_estado


    def _coste_accion(self, estado, nombre_accion, parametro):
            """Calcula el coste de una acción."""
            coste, _, _ = self.contexto.buscar(estado['posicion'], parametro)
            return coste if coste != float('inf') else 999

        
