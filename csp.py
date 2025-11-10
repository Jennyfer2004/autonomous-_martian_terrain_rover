import random
import copy 

class CSPRover:
    def __init__(self, contexto,PI=3,max_solutions=1000000):
        self.contexto = contexto
        self.max_solutions=max_solutions
        self.dominios={}
        self.variables = []
        
        self.PI=PI
        
    
    def definir_dominios(self):
        """Define los dominios de cada variable"""
        dominio_PI = [
            (x, y)
            for x in range(self.contexto.tamaño)
            for y in range(self.contexto.tamaño)
            if self.contexto.celda_valida(x, y)
        ]

        dominio_recoleccion = [
            (x, y)
            for x in range(self.contexto.tamaño)
            for y in range(self.contexto.tamaño)
            if self.contexto.mapa[x][y] == '.'
        ]

        for i in range(self.PI):
            self.variables.append(f"PI_{i}")
            self.dominios[f"PI_{i}"] = list(dominio_PI)

        self.variables.append("REC")
        self.dominios["REC"] = list(dominio_recoleccion)
        
    def restricciones(self,asignacion):
        """Agrega funciones que validan las restricciones del CSP"""

        posiciones = list(asignacion.values())

        if len(set(posiciones)) < len(self.variables):

            return False
        pis = [v for k, v in asignacion.items() if "PI_" in k and v is not None]

        for destino in pis:
            costo, tiempo, _ = self.contexto.buscar((0, 0), destino)

            if not costo :
                return False
            if costo >= 45:
                return False
        return True
    
    def es_consistente(self, variable, valor):
        """Verifica si asignar 'valor' a 'variable' es consistente con lasmrestricciones, considerando la asignación actual."""

        for var_asignada, val_asignado in self.asignacion.items():
            if valor == val_asignado:
                return False 

        if "PI_" in variable:
            costo, _, _ = self.contexto.buscar((0, 0), valor)
            if not costo or costo >= 45:
                return False
        
        return True
    
    def seleccionar_variable_sin_asignar(self):
        """ Selecciona la siguiente variable a asignar"""
        for var in self.variables:
            if var not in self.asignacion:
                return var
        return None
    
    def retroceso(self):
        """
        Función recursiva principal del algoritmo de backtracking.
        """
        print(self.iteraciones_validas)

        if len(self.asignacion) == len(self.variables):
            self.todas_las_soluciones.append(copy.deepcopy(self.asignacion))
            self.iteraciones_validas+=1
            return 

        var = self.seleccionar_variable_sin_asignar()

        for valor in self.dominios[var]:

            if self.es_consistente(var, valor):
                self.asignacion[var] = valor

                self.retroceso()
                del self.asignacion[var]

        return 
    def resolver(self):
        """Inicia el proceso de resolución con backtracking."""
        
        print(f"Iniciando búsqueda de todas las soluciones (límite: {self.max_solutions})...")

        self.asignacion = {}
        self.todas_las_soluciones = []
        self.iteraciones_validas=0
        
        self.retroceso()
        if not self.todas_las_soluciones:
            print("No se encontró ninguna solución para este entorno.")
            return None
        print(f"Se encontraron un total de {len(self.todas_las_soluciones)} soluciones.")

        solucion_elegida = random.choice(self.todas_las_soluciones)
        
        print("¡Solución elegida al azar!")
        return solucion_elegida
    
    
    def ejecutar(self):
        """Ejecuta todo el proceso CSP"""
        self.definir_dominios()
        solucion = self.resolver()

        if solucion:
            print(solucion)
            return solucion 