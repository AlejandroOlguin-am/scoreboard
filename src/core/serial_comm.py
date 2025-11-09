# src/core/serial_comm.py

import serial
import time
import threading

class SerialCommunicator:
    """Maneja la conexión y el envío de datos al hardware (Arduino/Displays)."""
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        # Nota: Usamos el puerto estándar de Linux como default.
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.lock = threading.Lock() # Para asegurar el envío de datos desde hilos

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2) # Espera a que la conexión se inicialice
            print(f"Serial: Conectado a {self.port} a {self.baudrate} baudios.")
        except serial.SerialException as e:
            self.ser = None
            print(f"Serial ERROR: No se pudo conectar al puerto {self.port}. {e}")
            print("Serial: La comunicación al hardware estará deshabilitada.")

    def send_command(self, command: str):
        """Envía un comando (byte) al puerto serial si la conexión es válida."""
        if self.ser and self.ser.is_open:
            with self.lock:
                try:
                    # 'P' o 'N' en tu código se envían como bytes
                    self.ser.write(command.encode('ascii'))
                    print(f"Serial: Enviado comando '{command}'")
                except Exception as e:
                    print(f"Serial ERROR al enviar datos: {e}")

    def close(self):
        """Cierra la conexión serial."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial: Conexión cerrada.")