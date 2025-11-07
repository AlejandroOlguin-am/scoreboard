# 🤖 Sistema de Puntuación para Competiciones de Robótica

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Sistema automatizado de puntuación que utiliza visión por computadora (OpenCV) para rastrear objetos y comunicarse en tiempo real con un microcontrolador PIC18F4550 para la visualización en un marcador físico. Desarrollado para el **FIRST Global Challenge 2024**.

## 🎯 Vista General

Este sistema soluciona el desafío de la puntuación en tiempo real. Detecta objetos (bolas de 2 y 5 puntos) en zonas de recolección y transmite el puntaje a un marcador físico.

### Características Clave
* **Visión:** Detección en tiempo real, rastreo multicolor y monitoreo de Regiones de Interés (ROI).
* **Puntuación:** Temporizador de cuenta regresiva y seguimiento de puntaje para dos alianzas.
* **Hardware:** Comunicación serial (UART) con PIC18F4550 para control de displays de 7 segmentos.

## 🏗️ Arquitectura del Sistema

El sistema se divide en dos módulos que se comunican serialmente:

1.  **Módulo de Visión (Python/OpenCV):** Captura video, detecta objetos, calcula el puntaje y envía la información serialmente.
2.  **Módulo de Display (PIC18F4550 C):** Recibe los datos seriales y gestiona la lógica del multiplexado para mostrar el tiempo y los puntajes en el hardware físico.



## 🛠️ Requisitos de Hardware

* **Computación:** PC/Portátil con Linux o Windows (mínimo 4GB RAM).
* **Cámara:** USB Webcam (mínimo 30 FPS).
* **Microcontrolador:** PIC18F4550 (20MHz), Displays de 7 segmentos y adaptador USB-a-Serial.

## 📦 Instalación

Sigue estos pasos para configurar el entorno de desarrollo y ejecución:

### 1. Python (Visión)
1.  Clonar el repositorio y moverse al directorio:
    ```bash
    git clone [https://github.com/yourusername/robotics-scoring-system.git](https://github.com/yourusername/robotics-scoring-system.git)
    cd robotics-scoring-system
    ```
2.  Crear y activar un entorno virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
3.  Instalar las dependencias de Python:
    ```bash
    pip install -r requirements.txt
    ```

### 2. Firmware (Microcontrolador)
1.  Compilar el código en `firmware/main.c` usando MPLAB.
2.  Grabar el archivo `.hex` resultante en el **PIC18F4550**.

## 🚀 Uso y Ejecución

1.  Asegura que el PIC esté conectado vía USB-Serial y la cámara esté activa.
2.  Edita `src/config.py` para establecer el `SERIAL_PORT` correcto (ej. `/dev/ttyUSB0` o `COM3`).
3.  Ejecuta la aplicación principal:
    ```bash
    python src/main.py
    ```

## 📚 Documentación Adicional

* **[Guía de Montaje de Hardware](docs/HARDWARE_SETUP.md)** - Diagramas de cableado y montaje físico.
* **[Protocolo de Comunicación](docs/PROTOCOL.md)** - Especificación del formato de datos seriales.

## 🤝 Contribuciones y Licencia

Este proyecto está bajo la [Licencia MIT](LICENSE). Las contribuciones son bienvenidas a través de Pull Requests.

## 🤝 Autor
Alejandro Olguin
    GitHub: @AlejandroOlguin-am
