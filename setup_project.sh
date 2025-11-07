#!/bin/bash

echo "🤖 Creating Robotics Scoring System Project Structure..."

# Create main directories
mkdir -p src/{vision,communication,scoring,gui,utils}
mkdir -p firmware/build
mkdir -p tests
mkdir -p examples
mkdir -p docs/images
mkdir -p data/{calibration,recordings,logs}
mkdir -p assets/sounds

# Create __init__.py files
touch src/__init__.py
touch src/vision/__init__.py
touch src/communication/__init__.py
touch src/scoring/__init__.py
touch src/gui/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

# Create placeholder files
touch src/vision/camera.py
touch src/communication/protocol.py
touch src/gui/control_panel.py
touch src/utils/logger.py
touch src/utils/helpers.py

touch firmware/README.md
touch firmware/uart.c
touch firmware/uart.h
touch firmware/display.c
touch firmware/display.h
touch firmware/Makefile

touch tests/test_ball_detector.py
touch tests/test_tracker.py
touch tests/test_serial_handler.py
touch tests/test_score_manager.py
touch tests/test_timer.py

touch examples/camera_calibration.py
touch examples/serial_test.py
touch examples/simple_detection.py
touch examples/simulation_mode.py

touch docs/API.md
touch docs/TROUBLESHOOTING.md
touch docs/CONTRIBUTING.md

touch data/calibration/camera_params.yaml
touch assets/icon.png

echo "✅ Project structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Copy your code files to their respective locations"
echo "2. Initialize git: git init"
echo "3. Add remote: git remote add origin "
echo "4. Commit: git add . && git commit -m 'Initial commit'"
echo "5. Push: git push -u origin main"
