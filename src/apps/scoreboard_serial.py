# src/apps/scoreboard_serial.py

import cv2
import numpy as np
import threading
import time
import tkinter as tk
from tkinter import ttk

# Importamos las clases refactorizadas
from src.core.timer import Temporizador
from src.core.tracker import ObjectTracker 
from src.core.serial_comm import SerialCommunicator

# --- 1. Inicialización de Clases y Variables Globales ---

# Inicialización del temporizador
tiempo_inicial = 150  # 2 minutos y 30 segundos
temporizador = Temporizador(tiempo_inicial)

# Inicialización del Rastreador y Comunicación Serial
# Usamos un solo rastreador para la versión serial (solo rastrea el equipo Rojo)
seguimiento = ObjectTracker() 
serial_comm = SerialCommunicator(port='/dev/ttyUSB0', baudrate=9600) # ¡Ajusta el puerto en Linux!

cap = cv2.VideoCapture(0) # Nota: Usas '2' en tu código original, ajusta según tu cámara

# Rango de detección para el color Rojo (doble rango en HSV)
rojoBajo1 = np.array([0, 100, 20], np.uint8)
rojoAlto1 = np.array([10, 255, 255], np.uint8)
rojoBajo2 = np.array([175, 100, 20], np.uint8)
rojoAlto2 = np.array([180, 255, 255], np.uint8)

deteccion = cv2.bgsegm.createBackgroundSubtractorMOG()
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

# Contadores de puntuación (dependerán del rastreador)
puntos_rojo_actuales = 0 

# --- 2. Funciones de Control y Hilos ---

def start_timer_and_opencv():
    """Función que inicia el temporizador y el hilo de OpenCV/Detección."""
    temporizador.start()
    
    # Iniciar el hilo de OpenCV
    opencv_t = threading.Thread(target=opencv_thread)
    opencv_t.daemon = True
    opencv_t.start()

def temporizador_thread():
    """Hilo que actualiza la lógica interna del temporizador."""
    while True:
        temporizador.update_clock()
        time.sleep(0.1)

t = threading.Thread(target=temporizador_thread)
t.daemon = True
t.start()

def send_scoreboard_data(rojo_score: int, azul_score: int, tiempo_restante: float):
    # Asegúrate de que serial_comm.ser es tu objeto serial de PySerial
    
    # Formatear Puntuaciones (a 2 dígitos)
    score_r_str = f"{rojo_score:02d}"
    score_a_str = f"{azul_score:02d}"
    
    # Formatear Tiempo (a MM:SS)
    minutes, seconds = divmod(tiempo_restante, 60)
    time_str = f"{int(minutes):02d}:{int(seconds):02d}"
    
    # Construir la Trama (Ej: R12A05_02:30)
    trama = f"R{score_r_str}A{score_a_str}_{time_str}\n" 
    
    try:
        if serial_comm.ser and serial_comm.ser.is_open:
            serial_comm.ser.write(trama.encode('ascii'))
            # print(f"Enviado: {trama.strip()}")
    except Exception as e:
        # Manejo de error
        pass


def opencv_thread():
    """Hilo principal que maneja la captura de video y la lógica de detección."""
    global puntos_rojo_actuales

    while temporizador.running or not temporizador.time_remaining == 0:
        ret, frame = cap.read()
        if not ret:
            break
            
        # --- Preprocesamiento y Detección ---
        # Definición de la Zona de Interés (ROI)
        zona = frame[400:700, 360:830]
        zona_gray = cv2.cvtColor(zona, cv2.COLOR_BGR2GRAY)

        # Máscaras de Color (HSV)
        hsv = cv2.cvtColor(zona, cv2.COLOR_BGR2HSV)
        maskRojo1 = cv2.inRange(hsv, rojoBajo1, rojoAlto1)
        maskRojo2 = cv2.inRange(hsv, rojoBajo2, rojoAlto2)
        mask_color = cv2.add(maskRojo1, maskRojo2)

        # Máscara de Movimiento (MOG)
        mask = deteccion.apply(zona_gray)
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.dilate(mask, None, iterations=2)

        # Combinar máscaras
        combined_mask = cv2.bitwise_and(mask, mask_color)
        contornos, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # --- Rastreo y Puntuación ---
        detecciones = []
        for cont in contornos:
            area = cv2.contourArea(cont)
            if area > 3000:
                x, y, ancho, alto = cv2.boundingRect(cont)
                detecciones.append([x, y, ancho, alto])

        info_id = seguimiento.rastreo(detecciones)
        
        # Lógica de Puntuación: Si el conteo del rastreador cambia, es un nuevo punto
        nuevo_conteo = seguimiento.get_current_count()

        if nuevo_conteo > puntos_rojo_actuales:
            puntos_rojo_actuales = nuevo_conteo
            # Aquí se envía el comando 'P'
            serial_comm.send_command('P') 
        
        # --- Dibujar resultados ---
        for inf in info_id:
            x, y, ancho, alto, id = inf
            cv2.putText(zona, str(id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2)
            cv2.rectangle(zona, (x, y), (x + ancho, y + alto), (255, 255, 0), 3)

        # Dibujar marcador en el frame principal (simplificado para serial)
        cv2.rectangle(frame, (0, 0), (400, 60), (0, 0, 255), -1)
        textoA = f'PUNTOS ROJO = {puntos_rojo_actuales}'
        cv2.putText(frame, textoA, (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
        # Dibujar temporizador
        cv2.rectangle(frame, (500, 0), (800, 80), (0, 0, 0), -1)
        tiempo_texto = temporizador.format_time()
        cv2.putText(frame, tiempo_texto, (frame.shape[1] // 2 - 50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Mostrar frames de depuración
        cv2.imshow('zona', zona)
        cv2.imshow("frame", frame)

        info_id = seguimiento.rastreo(detecciones)
        nuevo_conteo = seguimiento.get_current_count() # Obtiene el conteo total de objetos únicos

        if nuevo_conteo > puntos_rojo_actuales:
            puntos_rojo_actuales = nuevo_conteo
            serial_comm.send_command('P') 

        k = cv2.waitKey(10) & 0xFF
        if k == 27: # ESC para salir
            break

    # --- Limpieza al salir ---
    cap.release()
    cv2.destroyAllWindows()
    serial_comm.close()

# --- 3. Configuración de Tkinter (La GUI de control) ---

root = tk.Tk()
root.title("FGC 2024 - Control de Marcador Serial")

start_button = ttk.Button(root, text="Iniciar Competición", command=start_timer_and_opencv)
start_button.grid(row=0, column=0, padx=10, pady=10)

root.mainloop()