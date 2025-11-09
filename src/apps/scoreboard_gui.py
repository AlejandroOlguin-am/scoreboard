# src/apps/scoreboard_gui.py

import cv2
import numpy as np
import threading
import time
import tkinter as tk
from tkinter import ttk

# Importamos las clases refactorizadas
from src.core.timer import Temporizador
from src.core.tracker import ObjectTracker 

# --- 1. Inicialización de Clases y Variables Globales ---

tiempo_inicial = 150 
temporizador = Temporizador(tiempo_inicial)

# Usamos un tracker distinto para cada color/equipo
seguimiento_rojo = ObjectTracker() 
seguimiento_azul = ObjectTracker() 

cap = cv2.VideoCapture(0)

# Rango de detección para los colores
azulBajo = np.array([110, 100, 20], np.uint8)
azulAlto = np.array([130, 255, 255], np.uint8)
rojoBajo1 = np.array([0, 100, 20], np.uint8)
rojoAlto1 = np.array([10, 255, 255], np.uint8)
rojoBajo2 = np.array([175, 100, 20], np.uint8)
rojoAlto2 = np.array([180, 255, 255], np.uint8)

deteccion = cv2.bgsegm.createBackgroundSubtractorMOG()
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

puntos_rojo_actuales = 0
puntos_azul_actuales = 0

# --- 2. Funciones de Control y Hilos ---

def start_timer_and_opencv():
    """Inicia el temporizador y el hilo de OpenCV/Detección."""
    temporizador.start()
    
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

def opencv_thread():
    """Hilo principal que maneja la captura de video y la lógica de detección."""
    global puntos_rojo_actuales, puntos_azul_actuales

    while temporizador.running or not temporizador.time_remaining == 0:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Definición de la Zona de Interés (ROI)
        zona = frame[200:500, 450:920]
        zona_gray = cv2.cvtColor(zona, cv2.COLOR_BGR2GRAY)

        # Máscaras de Color
        hsv = cv2.cvtColor(zona, cv2.COLOR_BGR2HSV)
        mask_azul = cv2.inRange(hsv, azulBajo, azulAlto)
        maskRojo1 = cv2.inRange(hsv, rojoBajo1, rojoAlto1)
        maskRojo2 = cv2.inRange(hsv, rojoBajo2, rojoAlto2)
        mask_rojo = cv2.add(maskRojo1, maskRojo2)

        # Máscara de Movimiento (MOG)
        mask = deteccion.apply(zona_gray)
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.dilate(mask, None, iterations=2)

        # Combinar máscaras (Movimiento AND Color)
        combined_mask_rojo = cv2.bitwise_and(mask, mask_rojo)
        combined_mask_azul = cv2.bitwise_and(mask, mask_azul)
        
        contornos_rojo, _ = cv2.findContours(combined_mask_rojo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contornos_azul, _ = cv2.findContours(combined_mask_azul, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # --- Puntuación Equipo Rojo ---
        detecciones_rojo = []
        for cont in contornos_rojo:
            if cv2.contourArea(cont) > 3000:
                detecciones_rojo.append(cv2.boundingRect(cont))
        
        info_id_rojo = seguimiento_rojo.rastreo(detecciones_rojo)
        puntos_rojo_actuales = seguimiento_rojo.get_current_count() # Actualiza el puntaje
        
        for inf in info_id_rojo:
            x, y, ancho, alto, id = inf
            cv2.putText(zona, str(id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2)
            cv2.rectangle(zona, (x, y), (x + ancho, y + alto), (0, 0, 255), 3) # Rojo

        # --- Puntuación Equipo Azul ---
        detecciones_azul = []
        for cont in contornos_azul:
            if cv2.contourArea(cont) > 3000:
                detecciones_azul.append(cv2.boundingRect(cont))
        
        info_id_azul = seguimiento_azul.rastreo(detecciones_azul)
        puntos_azul_actuales = seguimiento_azul.get_current_count() # Actualiza el puntaje

        for inf in info_id_azul:
            x, y, ancho, alto, id = inf
            cv2.putText(zona, str(id), (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2)
            cv2.rectangle(zona, (x, y), (x + ancho, y + alto), (255, 0, 0), 3) # Azul

        # --- Dibujar Marcador y HUD ---
        # Puntos Equipo Rojo
        cv2.rectangle(frame, (0, 0), (400, 60), (0, 0, 255), -1)
        textoA = f'ROJO PUNTOS = {puntos_rojo_actuales}'
        cv2.putText(frame, textoA, (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
        # Puntos Equipo Azul
        cv2.rectangle(frame, (900, 0), (frame.shape[1], 60), (255, 0, 0), -1)
        textoB = f'AZUL PUNTOS = {puntos_azul_actuales}'
        cv2.putText(frame, textoB, (920, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        # Mostrar temporizador
        cv2.rectangle(frame, (500, 0), (800, 80), (0, 0, 0), -1)
        tiempo_texto = temporizador.format_time()
        cv2.putText(frame, tiempo_texto, (frame.shape[1] // 2 - 50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Mostrar frames de depuración
        cv2.imshow('frame', frame)

        k = cv2.waitKey(10) & 0xFF
        if k == 27:
            break

    # --- Limpieza al salir ---
    cap.release()
    cv2.destroyAllWindows()

# --- 3. Configuración de Tkinter (La GUI de control) ---

root = tk.Tk()
root.title("FGC 2024 - Control de Marcador GUI")

start_button = ttk.Button(root, text="Iniciar Competición", command=start_timer_and_opencv)
start_button.grid(row=0, column=0, padx=10, pady=10)

root.mainloop()