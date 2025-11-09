import time
import threading

class Temporizador:
    """Clase para gestionar el tiempo de la competencia (countdown)."""
    def __init__(self, tiempo_inicial: int):
        self.time_set = tiempo_inicial  # Tiempo total en segundos (ej: 150s)
        self.time_remaining = tiempo_inicial
        self.running = False
        self.lock = threading.Lock() # Uso de Lock para seguridad en hilos

    def start(self):
        """Inicia el temporizador."""
        with self.lock:
            if not self.running:
                self.start_time = time.time()
                self.running = True

    def stop(self):
        """Detiene el temporizador."""
        with self.lock:
            self.running = False

    def reset(self):
        """Reinicia el temporizador al tiempo inicial."""
        with self.lock:
            self.running = False
            self.time_remaining = self.time_set
    
    def update_clock(self):
        """Calcula el tiempo restante en cada ciclo."""
        with self.lock:
            if self.running:
                elapsed = time.time() - self.start_time
                self.time_remaining = max(self.time_set - elapsed, 0)
                if self.time_remaining == 0:
                    self.running = False

    def format_time(self) -> str:
        """Formatea el tiempo restante a MM:SS."""
        minutes, seconds = divmod(self.time_remaining, 60)
        return f"{int(minutes):02}:{int(seconds):02}"