import time 
class Rover:
    def __init__(self, x, y, energia_max, tiempo_max=180):
        self.x = x
        self.y = y
        self.energia = energia_max
        self.energia_max = energia_max
        self.tiempo_max= tiempo_max
        self.tiempo_restante= tiempo_max
        self.muestras = 0
        self.muestras_recolectadas = set() 
        self.imagenes = 0
        self.comunicacion = True  # Solo True cuando está en base
        self.dejar_muestras= True # Solo cuando esta en el punto estrategico de poner las muestras 

    def mover(self, dx, dy, coste, tiempo):
        if self.energia >= coste :
            self.x += dx
            self.y += dy
            self.energia -= coste
            self.tiempo_restante-tiempo
            return True
        else:
            print("Energía insuficiente para moverse.")

    def recargar(self):
        if self.energia<=self.energia_max:
            time.sleep(2)
        else:
            time.sleep(1)
        self.energia = self.energia_max
        print("Rover recargado en la base.")

    def recolectar(self, coordenadas_poi):
        if self.energia >= 2:
            self.muestras_recolectadas.add(coordenadas_poi)
            self.energia -= 2
            print(f"🧪 Muestra de {coordenadas_poi} guardada en el rover.")
            return True
        else:
            print("❌ Energía insuficiente para recolectar.",self.energia)
            return False
        
    def tirar_fotos(self):
        if self.energia>1 and self.tiempo_restante>2:
            self.imagenes+=1
            self.energia-=1
            self.tiempo_restante-=2
        else:
            print(" No tiene sufificente energía o tiempo para realizar esta acción")
        
