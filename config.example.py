"""
Archivo de configuración de ejemplo
Copia este archivo como config.py y ajusta los valores según tu setup
"""

# ==================== HARDWARE SETTINGS ====================

# Serial Communication
SERIAL_PORT = '/dev/ttyUSB0'  # Windows: 'COM3', Linux: '/dev/ttyUSB0', Mac: '/dev/cu.usbserial'
BAUDRATE = 9600
SERIAL_TIMEOUT = 1.0  # seconds

# Camera Settings
CAMERA_INDEX = 0  # 0 for default camera, 1 for external USB camera
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30

# ==================== VISION SETTINGS ====================

# Region of Interest (Scoring Zone)
ROI_X = 450  # Adjust based on your camera setup
ROI_Y = 200
ROI_WIDTH = 470
ROI_HEIGHT = 300

# Color Detection Ranges (HSV)
# Modify these during calibration
RED_LOWER_1 = (0, 100, 20)
RED_UPPER_1 = (10, 255, 255)
RED_LOWER_2 = (175, 100, 20)
RED_UPPER_2 = (180, 255, 255)

BLUE_LOWER = (90, 100, 20)
BLUE_UPPER = (130, 255, 255)

GREEN_LOWER = (35, 100, 20)
GREEN_UPPER = (85, 255, 255)

BLACK_LOWER = (0, 0, 0)
BLACK_UPPER = (180, 50, 50)

# Detection Parameters
MIN_BALL_AREA = 3000  # Adjust based on ball size and camera distance
MAX_BALL_AREA = 50000

# ==================== SCORING SETTINGS ====================

# Match Configuration
MATCH_DURATION = 150  # seconds (2:30)

# Point Values
POINTS_GREEN_BALL = 2
POINTS_BLACK_BALL = 5

# ==================== DISPLAY SETTINGS ====================

# Debug Windows
SHOW_DETECTION_WINDOWS = True  # Set False in production

# ==================== LOGGING SETTINGS ====================

# Log Level
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_CONSOLE = True

# ==================== ADVANCED SETTINGS ====================

# Performance
USE_GPU_ACCELERATION = False  # Requires OpenCV with CUDA
PROCESSING_THREADS = 2

# Data Directories (relative to project root)
DATA_DIR = "data"
CALIBRATION_DIR = "data/calibration"
RECORDINGS_DIR = "data/recordings"
LOGS_DIR = "logs"