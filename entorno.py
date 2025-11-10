

import random

from rover import *
from csp import *
from busqueda import *
from planificacion_metaheuristica import *
from bfs import *
from constantes import *

class ContextoMarciano:
    def __init__(self, tamaño=15, energia_max=100,tiempo_max = 180,rover=[0,0],base=(0,0)):
        self.tamaño = tamaño
        self.mapa = self.generar_mapa()
        self.rover = Rover(rover[0], rover[1], energia_max,tiempo_max)
        self.base = base
        self.muestras_analizadas = set()

        self.existen_puntos_interes=self.asignar_puntos_interes()
        
    def generar_mapa(self):
        """Genera el mapa aleatoriamente con los obstáculos"""
        terrenos = ['.',"*", 'A', 'D', 'O']
        pesos = [0.5,0.3 ,0.25, 0.15, 0.1]
        return [[random.choices(terrenos, pesos)[0] for _ in range(15)] for _ in range(15)]
    
    def asignar_puntos_interes(self):
        """Ejecuta el CSP para ubicar puntos de interés y recolección."""
        
        csp = CSPRover(self)
        solucion = csp.ejecutar()

        if solucion:
            
            self.puntos_interes = [solucion[var] for var in solucion if "PI_" in var]
            self.punto_recolectar = solucion["REC"]
            return True
        else:
            return False
            
    def mostrar_mapa(self):
        """ Mostrar el mapa"""
        for i in range(self.tamaño):
            fila = ""
            for j in range(self.tamaño):
                if (i, j) == (self.rover.x, self.rover.y):
                    fila += " R "
                elif (i, j) == self.base:
                    fila += " B "
                elif (i, j) in self.puntos_interes:
                    fila += " I "
                elif (i, j) in self.punto_recolectar:
                    fila += " M "
                else:
                    fila +=" "+ self.mapa[i][j] + " "
        print(f"Energía: {self.rover.energia} | Tiempo: {self.rover.tiempo_restante} | Muestras: {self.rover.muestras} ")
        
    def tipo_terreno(self, x, y):
        """Dice que tipo de terreno es"""
        if 0 <= x < self.tamaño and 0 <= y < self.tamaño:
            return self.mapa[x][y]
        return 'O'

    def coste_movimiento(self, terreno):
        """Coste de moverse """
        if terreno == '.': return 1
        if terreno == 'A': return 2
        if terreno == 'D': return 3
        if terreno == '*': return 5

        return 999  # obstáculo o inválido
    
    def tiempo_movimiento(self, terreno):
        """tiempo de moverse"""
        if terreno == '.': return 2
        if terreno == 'A': return 6
        if terreno == 'D': return 8
        if terreno == '*': return 10

        return 999  # obstáculo o inválido
    
    def celda_valida(self, x, y):
        """Celdas válidas"""
        if 0 <= x < self.tamaño and 0 <= y < self.tamaño:
            return self.mapa[x][y] != 'O'
        return False

    def buscar(self,posicion=None,base=None,tipo="a_star",tipo_heuristica="manhattan"):
        """Llama a la función buscar_ruta y devuelve coste , tiempo y la ruta encontrada """
        if posicion and base:
            ruta= buscar_ruta(self, posicion, base,tipo,tipo_heuristica)
        else: 
            ruta=buscar_ruta(self, (self.rover.x, self.rover.y), self.base,tipo,tipo_heuristica)
        if ruta:
            coste=0
            tiempo=0
            for paso in ruta:
                terreno = self.tipo_terreno(paso[0], paso[1])
                coste += self.coste_movimiento(terreno)
                tiempo +=self.tiempo_movimiento(terreno)
            return (coste,tiempo,ruta)
        else:
            print("No existe una ruta entre esas dos ubicaiones")
            return None,None,None
    def _volver_a_base(self):
        """Vuelve a la base desde la posición actual"""
        coste,tiempo,ruta = self.buscar((self.rover.x, self.rover.y), self.base)
        if ruta:
            for paso in ruta:
                if self.rover.energia <= 0:
                    break
                dx = paso[0] - self.rover.x
                dy = paso[1] - self.rover.y
                terreno = self.tipo_terreno(paso[0], paso[1])
                coste = self.coste_movimiento(terreno)
                self.rover.mover(dx, dy, coste)

    def _definir_estado_objetivo(self):
        """Define el estado inicial y la función objetivo para la misión completa."""
        estado_inicial = {
            'posicion': (self.rover.x, self.rover.y),
            'energia': self.rover.energia,
            'bateria_max': self.rover.energia_max,
            'muestras_recolectadas': set(),
            'muestras_analizadas': set(),
        }

        def es_objetivo(estado):
            """
            La misión se cumple SOLO si:
            1. Se han visitado y analizado TODOS los POIs.
            2. Se han dejado todas las muestras (implícito en el paso 1).
            3. El rover está de VUELTA en la base.
            """
            todos_pois_analizados = len(estado['muestras_analizadas']) == len(self.puntos_interes)
            en_base_final = estado['posicion'] == self.base
            
            return todos_pois_analizados and en_base_final
                    
        return estado_inicial, es_objetivo


    def simular_con_bfs(self):
        """
        Inicia la simulación usando Búsqueda en Anchura (BFS) para planificar la misión.
        BFS garantiza encontrar el plan de menor coste.
        """
        print(f"\n Iniciando simulación con BÚSQUEDA EN ANCHURA (BFS)...\n")
        
        if not hasattr(self, 'puntos_interes') or not self.puntos_interes:
            print(" No hay puntos de interés definidos. No se puede planificar la misión.")
            return None

        estado_inicial, es_objetivo = self._definir_estado_objetivo()
        
        planificador_bfs = PlanificadorBFS(
            contexto=self,
            estado_inicial=estado_inicial,
            objetivos=es_objetivo,
            acciones=ACCIONES_PLANIFICADOR
        )
        
        mejor_plan = planificador_bfs.resolver()

        if mejor_plan:
            print(f"\n Plan óptimo encontrado con {len(mejor_plan)} pasos.")
            return [self._ejecutar_plan(mejor_plan), mejor_plan]
        else:
            print("\n No se pudo encontrar un plan viable para la misión.")
            print("   Puede deberse a que los POIs son inalcanzables con la energía disponible.")
            return None
    def simular_con_metaheuristica(self, algoritmo="GA"):
        """
        Inicia la simulación usando una metaheurística seleccionada para planificar la misión.
        Opciones: "GA" (Algoritmo Genético), "SA" (Recocido Simulado).
        """
        print(f"\n Iniciando simulación con METAHEURÍSTICA ({algoritmo.upper()})...\n")
        
        if not hasattr(self, 'puntos_interes') or not self.puntos_interes:
            print(" No hay puntos de interés definidos. No se puede planificar la misión.")
            return None

        estado_inicial, es_objetivo = self._definir_estado_objetivo()

        optimizador = None
        
        if algoritmo == "GA":
            optimizador = PlanificadorMetaheuristicoAG(
                contexto=self,
                estado_inicial=estado_inicial,
                objetivos=es_objetivo,
                acciones=ACCIONES_PLANIFICADOR,
                tam_poblacion=50,    
                generaciones=100,
                tasa_mutacion=0.3
            )
        elif algoritmo == "SA":

            optimizador = PlanificadorMetaheuristicoSA(
                contexto=self,
                estado_inicial=estado_inicial,
                objetivos=es_objetivo,
                acciones=ACCIONES_PLANIFICADOR,
                temp_inicial=1000,
                enfriamiento=0.995,
            )
        else:
            print(" Algoritmo de metaheurística no reconocido. Usa 'GA' o 'SA'.")
            return None
        
        print("🔍 Buscando el mejor plan...")
        mejor_plan = optimizador.optimizar()

        if mejor_plan:
            print(f"\n Plan optimizado encontrado con {len(mejor_plan)} pasos.")
            return [self._ejecutar_plan(mejor_plan),mejor_plan]
        else:
            print("\n No se pudo encontrar un plan viable para la misión.")
            print("   Puede deberse a que los POIs son inalcanzables con la energía disponible.")
            return None
    def _ejecutar_plan(self, plan):
        """Ejecuta un plan paso a paso con verificación de seguridad energética y acumula coste y tiempo."""
        print(" Ejecutando plan optimizado con sistema de seguridad...")

        coste_total = 0
        tiempo_total = 0

        for i, (accion_nombre, parametro) in enumerate(plan):

            if self.rover.energia <= 0:
                print("⚡ Energía agotada durante la ejecución del plan.")
                break

            print(f"\n[{i+1}/{len(plan)}] Ejecutando: {accion_nombre} {parametro}")
            
            if accion_nombre == 'ir_a_poi':
                coste, tiempo, _ = self._ejecutar_ir_a_poi(parametro)
            elif accion_nombre == 'ir_a_base':
                coste, tiempo, _ = self._ejecutar_ir_a_base(parametro)
            elif accion_nombre == 'recargar':
                coste, tiempo = self._ejecutar_recargar()
            elif accion_nombre == 'dejar_muestras' :
                coste, tiempo = self._ejecutar_dejar_muestras()
            else:
                coste = 0
                tiempo = 0

            coste_total += coste
            tiempo_total += tiempo

            time.sleep(0.5)  

        print("\n🏁 Ejecución del plan completada.")
        print(f"💰 Coste total de la ruta: {coste_total}")
        print(f"⏱️ Tiempo total de ejecución: {tiempo_total}")

        if self.mision_completada():
            print("✅ ¡MISIÓN CUMPLIDA CON ÉXITO!")
            return coste_total,tiempo_total

        else:
            print(" La misión NO se completó completamente.")
            print(f"Estado final: Muestras analizadas {len(self.muestras_analizadas)}/{len(self.puntos_interes)}, Rover en base: {(self.rover.x, self.rover.y) == self.base}")
            return None


    def _ejecutar_ir_a_base(self, base):
        """Mueve el rover desde su posición actual hasta la base, devolviendo el coste y tiempo totales."""
        coste_total = 0
        tiempo_total = 0

        coste1, tiempo1, ruta = self.buscar((self.rover.x, self.rover.y), base)
        if not ruta:
            print(" No se encontró ruta hacia la base.")
            return float("inf"), float("inf"), None

        for paso in ruta:
            if self.rover.energia <= 0:
                print(" Energía agotada antes de llegar a la base.")
                break
            dx = paso[0] - self.rover.x
            dy = paso[1] - self.rover.y
            terreno = self.tipo_terreno(paso[0], paso[1])
            coste = self.coste_movimiento(terreno)
            tiempo = self.tiempo_movimiento(terreno)
            if self.rover.mover(dx, dy, coste, tiempo):
                coste_total += coste
                tiempo_total += tiempo

        print(f" Llegó a la base con energía {self.rover.energia}.")
        return coste_total, tiempo_total, ruta

                
    def _ejecutar_ir_a_poi(self, poi):
        """Mueve el rover al punto de interés y realiza la recolección."""
        coste_total = 0
        tiempo_total = 0

        coste1, tiempo1, ruta = self.buscar((self.rover.x, self.rover.y), poi)
        if not ruta:
            print(f" No se encontró ruta hacia el POI {poi}.")
            return float("inf"), float("inf"), None

        for paso in ruta:
            if self.rover.energia <= 0:
                print(" Energía agotada antes de llegar al POI.")
                break
            dx = paso[0] - self.rover.x
            dy = paso[1] - self.rover.y
            terreno = self.tipo_terreno(paso[0], paso[1])
            coste = self.coste_movimiento(terreno)
            tiempo = self.tiempo_movimiento(terreno)
            if self.rover.mover(dx, dy, coste, tiempo):
                coste_total += coste
                tiempo_total += tiempo

        if (self.rover.x, self.rover.y) == poi:
            if poi not in self.rover.muestras_recolectadas:
                self.rover.recolectar(poi)
                self.rover.muestras_recolectadas.add(poi)
                print(f" Muestra recolectada en {poi}. Total: {len(self.rover.muestras_recolectadas)}")
            else:
                print(f" Muestra en {poi} ya había sido recolectada.")
        else:
            print(" No se llegó al punto de interés.")

        return coste_total, tiempo_total, ruta

    
    def _ejecutar_dejar_muestras(self):

        """Ejecuta la acción de dejar muestras, actualizando el estado global."""
        coste1,tiempo1,ruta = self.buscar( (self.rover.x, self.rover.y), self.punto_recolectar)

        if ruta:
            for paso in ruta:
                if self.rover.energia <= 0:
                    return coste1,tiempo1
                dx = paso[0] - self.rover.x
                dy = paso[1] - self.rover.y
                terreno = self.tipo_terreno(paso[0], paso[1])
                coste = self.coste_movimiento(terreno)
                tiempo = self.tiempo_movimiento(terreno)
                if not self.rover.mover(dx, dy, coste, tiempo):

                    print(" Movimiento fallido",self.rover.x, self.rover.y)
                    break
                
        if (self.rover.x, self.rover.y) == self.punto_recolectar:
            if len(self.rover.muestras_recolectadas) > 0:

                print(" Depositando muestras en el punto de recolección...")
                
                self.muestras_analizadas.update(self.rover.muestras_recolectadas)
                self.rover.muestras_recolectadas.clear()
                print(f"✅ Muestras depositadas. Total analizadas: {len(self.muestras_analizadas)}")
                return coste1, tiempo1

            else:
                print(" No hay muestras para depositar.")
                return coste1, tiempo1
        else:
            print(" No se puede depositar: no está en el punto de recolección.")
            return coste1, tiempo1


    def _ejecutar_recargar(self):
        """Recarga la batería del rover si está en la base. Devuelve el coste y el tiempo usados."""
        if (self.rover.x, self.rover.y) != self.base:
            print(" No se puede recargar fuera de la base.")
            return 0, 0

        energia_inicial = self.rover.energia
        self.rover.energia = self.rover.energia_max
        print(f"🔋 Recargando... Energía: {energia_inicial} → {self.rover.energia}")

        coste = 0  
        tiempo = 10  
        return coste, tiempo

            
    def mision_completada(self):
        """
        Verifica si la misión se ha completado en el mundo real,
        usando el estado real del rover y el contexto.
        """
        todos_pois_analizados = len(self.muestras_analizadas) >= len(self.puntos_interes)
        en_base_final = (self.rover.x, self.rover.y) == self.base
        
        return todos_pois_analizados and en_base_final
    