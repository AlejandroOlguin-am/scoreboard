# 📚 API Reference

Este documento detalla la API pública del Sistema de Puntuación Robótica.

## 🎯 Módulos Principales

### 🎥 Vision Module (`vision/`)

#### `BallDetector` (ball_detector.py)
```python
class BallDetector:
    """Detector de bolas usando background subtraction y filtrado HSV."""
    
    def __init__(self):
        """Inicializar detector con parámetros de config.py."""
        
    def detect(self, frame, target_colors=None) -> List[List[int]]:
        """
        Detectar bolas en un frame.
        
        Args:
            frame: Frame de video (BGR)
            target_colors: Lista de colores a detectar
            
        Returns:
            List[List[int]]: Lista de detecciones [x, y, width, height]
        """
        
    def detect_with_masks(self, frame, target_colors=None) -> Tuple[list, np.ndarray, np.ndarray, np.ndarray]:
        """
        Detectar bolas y retornar máscaras de debug.
        
        Args:
            frame: Frame de video
            target_colors: Colores a detectar
            
        Returns:
            Tuple: (detections, motion_mask, color_mask, combined_mask)
        """
        
    def calibrate_colors(self, frame) -> dict:
        """
        Calibrar rangos de color interactivamente.
        
        Args:
            frame: Frame para calibración
            
        Returns:
            dict: Rangos HSV calibrados
        """
```

#### `ObjectTracker` (tracker.py)
```python
class ObjectTracker:
    """Tracker de objetos usando centroides."""
    
    def __init__(self, max_disappeared=30):
        """
        Inicializar tracker.
        
        Args:
            max_disappeared: Frames antes de eliminar objeto
        """
        
    def update(self, detections: List[List[int]]) -> List[List[int]]:
        """
        Actualizar tracking con nuevas detecciones.
        
        Args:
            detections: Lista de [x, y, w, h]
            
        Returns:
            List[List[int]]: Objetos trackeados [x, y, w, h, id]
        """
        
    def get_max_id(self) -> int:
        """
        Obtener ID máximo asignado.
        
        Returns:
            int: ID más alto usado
        """
```

### ⚡ Communication Module (`communication/`)

#### `SerialHandler` (serial_handler.py)
```python
class SerialHandler:
    """Manejador de comunicación serial con PIC18F4550."""
    
    def __init__(self, port=None, baudrate=9600, timeout=1):
        """
        Inicializar handler serial.
        
        Args:
            port: Puerto serial (ej: 'COM3', '/dev/ttyUSB0')
            baudrate: Velocidad en baudios
            timeout: Timeout de lectura
        """
        
    def connect(self) -> bool:
        """
        Establecer conexión serial.
        
        Returns:
            bool: True si conexión exitosa
        """
        
    def send_scores(self, red_score: int, blue_score: int) -> bool:
        """
        Enviar puntajes al PIC.
        
        Args:
            red_score: Puntaje rojo (0-99)
            blue_score: Puntaje azul (0-99)
            
        Returns:
            bool: True si envío exitoso
        """
        
    def send_timer(self, minutes: int, seconds: int) -> bool:
        """
        Enviar tiempo al PIC.
        
        Args:
            minutes: Minutos (0-99)
            seconds: Segundos (0-59)
            
        Returns:
            bool: True si envío exitoso
        """
```

### ⏱️ Scoring Module (`scoring/`)

#### `ScoreManager` (score_manager.py)
```python
class ScoreManager:
    """Gestor de puntajes para ambas alianzas."""
    
    def update_from_tracking(self, red_max_id: int, blue_max_id: int = 0):
        """
        Actualizar puntajes desde tracking.
        
        Args:
            red_max_id: ID máximo rojo
            blue_max_id: ID máximo azul
        """
        
    def add_ball(self, alliance: str, ball_color: str, ball_id: int):
        """
        Registrar evento de bola.
        
        Args:
            alliance: 'RED' o 'BLUE'
            ball_color: Color de la bola
            ball_id: ID de tracking
        """
        
    def get_match_summary(self) -> dict:
        """
        Obtener resumen detallado.
        
        Returns:
            dict: Estadísticas del match
        """
```

#### `MatchTimer` (timer.py)
```python
class MatchTimer:
    """Timer de cuenta regresiva para matches."""
    
    def __init__(self, duration: int = 150):
        """
        Inicializar timer.
        
        Args:
            duration: Duración en segundos
        """
        
    def start(self):
        """Iniciar o reanudar timer."""
        
    def stop(self):
        """Pausar timer."""
        
    def reset(self):
        """Reiniciar a duración inicial."""
        
    def get_time_components(self) -> Tuple[int, int]:
        """
        Obtener minutos y segundos.
        
        Returns:
            Tuple[int, int]: (minutos, segundos)
        """
```

## 🖥️ GUI Module (`gui/`)

#### `RoboticsScoreSystem` (main.py)
```python
class RoboticsScoreSystem:
    """Aplicación principal del sistema."""
    
    def __init__(self, simulate: bool = False, record: bool = False):
        """
        Inicializar sistema.
        
        Args:
            simulate: Modo simulación sin hardware
            record: Grabar video de salida
        """
        
    def run(self):
        """Iniciar la aplicación."""
        
    def start_match(self):
        """Iniciar partido."""
        
    def stop_match(self):
        """Detener partido."""
        
    def reset_match(self):
        """Reiniciar partido."""
```

## 🛠️ Uso de la API

### Ejemplo Básico
```python
from vision import BallDetector, ObjectTracker
from scoring import ScoreManager, MatchTimer
from communication import SerialHandler

# Inicializar componentes
detector = BallDetector()
tracker = ObjectTracker()
scores = ScoreManager()
timer = MatchTimer()
serial = SerialHandler('/dev/ttyUSB0')

# Procesar frame
detections = detector.detect(frame)
tracked = tracker.update(detections)

# Actualizar puntajes
max_id = tracker.get_max_id()
scores.update_from_tracking(max_id)

# Enviar a display
serial.send_scores(
    scores.get_red_score(),
    scores.get_blue_score()
)
```

### Modo Simulación
```python
from main import RoboticsScoreSystem

app = RoboticsScoreSystem(simulate=True)
app.run()
```

### Calibración de Color
```python
detector = BallDetector()
ranges = detector.calibrate_colors(frame)
print(f"HSV Ranges: {ranges}")
```

## 📊 Tipos de Datos

### Detecciones
```python
Detection = List[int]  # [x, y, width, height]
TrackedObject = List[int]  # [x, y, width, height, object_id]
```

### Rangos de Color
```python
ColorRange = {
    'lower': List[np.ndarray],  # [array([h, s, v])]
    'upper': List[np.ndarray]   # [array([h, s, v])]
}
```

### Resumen de Match
```python
MatchSummary = {
    'red_score': int,
    'blue_score': int,
    'red_balls': int,
    'blue_balls': int,
    'leader': str,
    'score_difference': int,
    'red_ball_details': List[Tuple[int, str, int]],
    'blue_ball_details': List[Tuple[int, str, int]]
}
```

## 🎯 Eventos

### SerialHandler
- `on_connect(port: str)`
- `on_disconnect()`
- `on_error(error: str)`
- `on_packet_sent(packet: bytes)`

### MatchTimer
- `on_start()`
- `on_stop()`
- `on_expire()`
- `on_tick(time_remaining: float)`

### ScoreManager
- `on_score_change(alliance: str, new_score: int)`
- `on_ball_scored(alliance: str, ball_id: int, points: int)`

## ⚙️ Configuración

Ver `config.py` para opciones configurables:
- Parámetros de visión
- Configuración serial
- Valores de puntuación
- Ajustes de GUI
- Modos de debug

## 🔄 Ciclo de Vida

1. Inicialización:
   ```python
   app = RoboticsScoreSystem()
   ```

2. Conexión Hardware:
   ```python
   app.serial.connect()
   ```

3. Match Loop:
   ```python
   app.start_match()
   # Auto-updates until match ends
   ```

4. Cleanup:
   ```python
   app.cleanup()
   ```

## 🐛 Debug y Logging

```python
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Debug masks
detector = BallDetector()
dets, motion, color, combined = detector.detect_with_masks(frame)
```

## 🔍 Testing

```python
# Unit tests
pytest tests/test_ball_detector.py
pytest tests/test_tracker.py

# Coverage
pytest --cov=src tests/
```

## 🚀 Performance

- **BallDetector**: ~30fps @ 720p
- **ObjectTracker**: O(n²) complejidad
- **SerialHandler**: 9600 baud, ~100 packets/sec
- **GUI**: 60fps target

## ⚠️ Known Issues

1. Pérdida de tracking en condiciones de baja luz
2. Latencia serial en matches largos
3. Falsos positivos en detección de color

## 🔄 Versioning

API sigue [Semantic Versioning](https://semver.org/):
- MAJOR: Cambios incompatibles
- MINOR: Funcionalidad nueva compatible
- PATCH: Bug fixes compatibles
