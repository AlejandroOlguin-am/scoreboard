"""
Configuration File
Centralized configuration for the Scoreboard System.
"""

# ==================== HARDWARE SETTINGS ====================

# Serial Communication
SERIAL_PORT = 'COM3'  # Windows: 'COM3', Linux: '/dev/ttyUSB0', Mac: '/dev/cu.usbserial'
BAUDRATE = 9600
SERIAL_TIMEOUT = 1.0  # seconds

# Camera Settings
CAMERA_INDEX = 0  # 0 for default camera, 1 for external USB camera
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30


# ==================== VISION SETTINGS ====================

# Region of Interest (Scoring Zone)
ROI_X = 450
ROI_Y = 200
ROI_WIDTH = 470
ROI_HEIGHT = 300

# Color Detection Ranges (HSV)
# Red Ball Detection (Hue wraps around at 180)
RED_LOWER_1 = (0, 100, 20)
RED_UPPER_1 = (10, 255, 255)
RED_LOWER_2 = (175, 100, 20)
RED_UPPER_2 = (180, 255, 255)

# Blue Ball Detection
BLUE_LOWER = (90, 100, 20)
BLUE_UPPER = (130, 255, 255)

# Green Ball Detection
GREEN_LOWER = (35, 100, 20)
GREEN_UPPER = (85, 255, 255)

# Yellow Ball Detection (for testing/calibration)
YELLOW_LOWER = (20, 100, 20)
YELLOW_UPPER = (32, 255, 255)

# Black Ball Detection (low saturation, low value)
BLACK_LOWER = (0, 0, 0)
BLACK_UPPER = (180, 50, 50)

# Detection Parameters
MIN_BALL_AREA = 3000  # Minimum contour area in pixels
MAX_BALL_AREA = 50000  # Maximum contour area in pixels
MORPHOLOGY_KERNEL_SIZE = (3, 3)  # Kernel for morphological operations
DILATION_ITERATIONS = 2

# Tracking Parameters
MAX_DISAPPEARED_FRAMES = 30  # Frames before removing lost object
TRACKING_DISTANCE_THRESHOLD = 100  # Max distance (pixels) for matching


# ==================== SCORING SETTINGS ====================

# Match Configuration
MATCH_DURATION = 150  # seconds (2:30)

# Point Values (FIRST Global Challenge 2024 Rules)
POINTS_GREEN_BALL = 2
POINTS_BLACK_BALL = 5

# Alliance Configuration
RED_ALLIANCE = "RED"
BLUE_ALLIANCE = "BLUE"


# ==================== DISPLAY SETTINGS ====================

# GUI Colors (BGR format for OpenCV)
COLOR_RED_ALLIANCE = (0, 0, 255)
COLOR_BLUE_ALLIANCE = (255, 0, 0)
COLOR_TIMER_BG = (0, 0, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_DETECTION_BOX = (0, 255, 0)
COLOR_ROI_BOX = (255, 255, 0)

# Font Settings
FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE_LARGE = 1.5
FONT_SCALE_MEDIUM = 1.0
FONT_SCALE_SMALL = 0.6
FONT_THICKNESS = 2


# ==================== LOGGING & DEBUG ====================

# Debug Mode
DEBUG = True
SHOW_DETECTION_WINDOWS = True
SHOW_MASK_WINDOWS = False

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "scoring_system.log"
LOG_TO_CONSOLE = True


# ==================== CALIBRATION ====================

# Camera Calibration (if using undistortion)
CAMERA_MATRIX = None  # Load from file if available
DISTORTION_COEFFS = None

# Auto-calibration
AUTO_CALIBRATE_ON_STARTUP = False
CALIBRATION_FRAMES_REQUIRED = 30


# ==================== ADVANCED SETTINGS ====================

# Performance
USE_GPU_ACCELERATION = False  # Requires OpenCV with CUDA
PROCESSING_THREADS = 2

# Background Subtraction
BG_SUBTRACTOR_HISTORY = 500
BG_SUBTRACTOR_THRESHOLD = 16
BG_SUBTRACTOR_DETECT_SHADOWS = False

# Communication Protocol
PACKET_START_BYTE = 0xAA
PACKET_END_BYTE = 0x55
MAX_RETRIES = 3
RETRY_DELAY = 0.1  # seconds


# ==================== FILE PATHS ====================

# Data Directories
DATA_DIR = "data"
CALIBRATION_DIR = "data/calibration"
RECORDINGS_DIR = "data/recordings"
LOGS_DIR = "logs"

# Assets
ASSETS_DIR = "assets"
ICON_PATH = "assets/icon.png"


# ==================== HELPER FUNCTIONS ====================

def get_ball_color_ranges():
    """
    Get all configured ball color ranges.
    
    Returns:
        dict: Color name -> (lower_hsv, upper_hsv, points)
    """
    return {
        'red': ([RED_LOWER_1, RED_LOWER_2], [RED_UPPER_1, RED_UPPER_2], POINTS_GREEN_BALL),
        'blue': (BLUE_LOWER, BLUE_UPPER, POINTS_GREEN_BALL),
        'green': (GREEN_LOWER, GREEN_UPPER, POINTS_GREEN_BALL),
        'black': (BLACK_LOWER, BLACK_UPPER, POINTS_BLACK_BALL),
    }


def validate_config():
    """
    Validate configuration parameters.
    
    Returns:
        list: List of validation warnings/errors
    """
    warnings = []
    
    # Check ROI bounds
    if ROI_X + ROI_WIDTH > FRAME_WIDTH:
        warnings.append(f"ROI exceeds frame width: {ROI_X + ROI_WIDTH} > {FRAME_WIDTH}")
    
    if ROI_Y + ROI_HEIGHT > FRAME_HEIGHT:
        warnings.append(f"ROI exceeds frame height: {ROI_Y + ROI_HEIGHT} > {FRAME_HEIGHT}")
    
    # Check area thresholds
    if MIN_BALL_AREA >= MAX_BALL_AREA:
        warnings.append("MIN_BALL_AREA must be less than MAX_BALL_AREA")
    
    # Check match duration
    if MATCH_DURATION <= 0:
        warnings.append("MATCH_DURATION must be positive")
    
    return warnings


# Auto-validate on import
if DEBUG:
    validation_warnings = validate_config()
    if validation_warnings:
        print("⚠️  Configuration Warnings:")
        for warning in validation_warnings:
            print(f"   - {warning}")


if __name__ == "__main__":
    # Print configuration summary
    print("=" * 60)
    print("SCOREBOARD - CONFIGURATION")
    print("=" * 60)
    print(f"\n📷 Camera: Index {CAMERA_INDEX} ({FRAME_WIDTH}x{FRAME_HEIGHT})")
    print(f"🔌 Serial: {SERIAL_PORT} @ {BAUDRATE} baud")
    print(f"⏱️  Match Duration: {MATCH_DURATION}s ({MATCH_DURATION // 60}:{MATCH_DURATION % 60:02d})")
    print(f"🎯 ROI: ({ROI_X}, {ROI_Y}) - {ROI_WIDTH}x{ROI_HEIGHT}")
    print(f"🏀 Ball Detection: Area {MIN_BALL_AREA}-{MAX_BALL_AREA} pixels")
    print(f"🎨 Colors: Red, Blue, Green ({POINTS_GREEN_BALL}pts), Black ({POINTS_BLACK_BALL}pts)")
    print(f"🐛 Debug Mode: {'Enabled' if DEBUG else 'Disabled'}")
    
    # Validate
    warnings = validate_config()
    if warnings:
        print(f"\n⚠️  {len(warnings)} Warning(s):")
        for w in warnings:
            print(f"   - {w}")
    else:
        print("\n✅ Configuration valid")
    
    print("\n" + "=" * 60)