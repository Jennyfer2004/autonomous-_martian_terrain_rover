import random

class CSPRover:
    def __init__(self, contexto,PI=3):
        self.contexto = contexto

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

    def resolver(self):
        """Busca una asignación que cumpla todas las restricciones"""

        variables = self.variables
        dominios = self.dominios

        for intento in range(10000):  
            asignacion = {
                var: random.choice(dominios[var]) for var in variables
            }

            if self.restricciones(asignacion):

                return asignacion 
        print(" No tiene solución posible este entorno")
        return None    
    
    def ejecutar(self):
        """Ejecuta todo el proceso CSP"""
        self.definir_dominios()
        solucion = self.resolver()

        if solucion:
            return solucion 