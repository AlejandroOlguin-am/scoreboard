# Guía de Montaje de Hardware

Esta guía detalla el proceso de montaje del hardware para el Sistema de Puntuación Robótica.

## 📋 Lista de Componentes (BOM)

### Microcontrolador y Programación
- 1x PIC18F4550
- 1x Base DIP40
- 1x Cristal 20MHz
- 2x Capacitor 22pF
- 1x Adaptador USB-a-Serial (CH340, CP2102 o similar)

### Display
- 8x Display 7 segmentos cátodo común
- 8x Resistencia 220Ω (limitadoras para segmentos)
- 2x LED RGB (indicadores de alianza)
- 2x Resistencia 330Ω (para LEDs)

### Alimentación
- 1x Regulador 7805
- 1x Capacitor 100µF
- 2x Capacitor 100nF
- 1x LED indicador de poder
- 1x Resistencia 1kΩ
- 1x Jack DC o terminal block

### Otros
- 1x PCB (diseño disponible en `hardware/pcb/`)
- Cable USB
- Cables Dupont para prototipado
- Cámara USB (mínimo 30FPS, 720p recomendado)

## 🔧 Instrucciones de Montaje

### 1. Preparación del Microcontrolador

1. Inserta el PIC18F4550 en la base DIP40
2. Conecta el cristal de 20MHz:
   - Pin 13 (OSC1) → Cristal
   - Pin 14 (OSC2) → Cristal
   - Conecta capacitores de 22pF de cada terminal del cristal a GND

### 2. Configuración de Displays

Los displays están multiplexados para ahorrar pines:
```
Display    Función
1-2        Minutos
3-4        Segundos
5-6        Puntaje Rojo
7-8        Puntaje Azul
```

1. Conexión de segmentos (común para todos los displays):
   - Segmento a → RC0
   - Segmento b → RC1
   - Segmento c → RC2
   - Segmento d → RC3
   - Segmento e → RC4
   - Segmento f → RC5
   - Segmento g → RC6
   - (Punto decimal no usado)

2. Conexión de dígitos (cátodos comunes):
   - Display 1 → RD0
   - Display 2 → RD1
   - Display 3 → RD2
   - Display 4 → RD3
   - Display 5 → RD4
   - Display 6 → RD5
   - Display 7 → RD6
   - Display 8 → RD7

### 3. Conexión USB-Serial

1. Adaptador USB-Serial al PIC:
   - TX del adaptador → RC7 (RX del PIC)
   - RX del adaptador → RC6 (TX del PIC)
   - GND → GND
   - No conectar VCC del adaptador

### 4. LEDs de Alianza

1. LED RGB Rojo:
   - Ánodo → RB0 (con resistencia 330Ω)
   - Cátodo → GND

2. LED RGB Azul:
   - Ánodo → RB1 (con resistencia 330Ω)
   - Cátodo → GND

### 5. Alimentación

1. Regulador 7805:
   - IN → 7-12V DC
   - OUT → VDD del PIC
   - Capacitor 100µF en entrada y salida
   - Capacitor 100nF cerca del PIC

## 📸 Posicionamiento de Cámara

1. Monte la cámara a una altura de ~2m
2. Apunte hacia la zona de puntuación
3. Ajuste para capturar un área de ~1.5m x 1m
4. Evite reflejos y sombras
5. Ilumine uniformemente el área

## ⚙️ Calibración

### Cámara

1. Ejecute el script de calibración:
   ```bash
   python examples/camera_calibration.py
   ```
2. Siga las instrucciones en pantalla
3. Guarde los parámetros en `data/calibration/`

### Color

1. Ejecute el detector con modo calibración:
   ```bash
   python src/vision/ball_detector.py
   ```
2. Use las trackbars para ajustar rangos HSV
3. Actualice `config.py` con los valores

## 🔍 Verificación

1. **Test de Displays**
   ```bash
   python examples/serial_test.py
   ```
   Debe mostrar una secuencia de números

2. **Test de Detección**
   ```bash
   python examples/simple_detection.py
   ```
   Verifique que detecta objetos correctamente

## 📝 Notas

- Mantenga buena ventilación para el regulador
- Use cables de calibre adecuado
- Considere agregar fusible de protección
- Documente cualquier modificación

## 🛠️ Troubleshooting

### Displays No Encienden
- Verifique voltajes
- Confirme polaridad
- Revise resistencias

### Error de Comunicación
- Verifique conexiones TX/RX
- Confirme configuración del puerto
- Pruebe otro adaptador

### Detección Pobre
- Ajuste iluminación
- Recalibre colores
- Limpie lente de cámara

## 📑 Referencias

- [Datasheet PIC18F4550](https://ww1.microchip.com/downloads/en/devicedoc/39632c.pdf)
- [Diagrama Esquemático](docs/images/schematic.pdf)
- [PCB Layout](docs/images/pcb_layout.pdf)