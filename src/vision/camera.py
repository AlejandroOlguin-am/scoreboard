"""
Camera Module
Handles camera initialization, calibration and image acquisition.
"""

import cv2
import numpy as np
import time
from pathlib import Path
import yaml
import config


class Camera:
    """
    Camera handler with calibration and image processing capabilities.
    """
    
    def __init__(self, camera_index=None):
        """
        Initialize camera.
        
        Args:
            camera_index (int): Camera index (None for config default)
        """
        self.camera_index = camera_index if camera_index is not None else config.CAMERA_INDEX
        self.cap = None
        self.frame_count = 0
        self.last_frame_time = 0
        self.fps = 0
        
        # Calibration parameters
        self.camera_matrix = None
        self.dist_coeffs = None
        self.calibrated = False
        
        # Load calibration if exists
        self._load_calibration()
    
    def start(self):
        """
        Start camera capture.
        
        Returns:
            bool: True if camera started successfully
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # Set camera parameters
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, config.FPS)
            
            # Verify settings
            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"Camera initialized at {actual_width}x{actual_height} @ {actual_fps}fps")
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def stop(self):
        """Release camera resources."""
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def read(self, undistort=True):
        """
        Read frame from camera.
        
        Args:
            undistort (bool): Apply undistortion if calibrated
            
        Returns:
            tuple: (success, frame)
        """
        if not self.cap:
            return False, None
        
        ret, frame = self.cap.read()
        if not ret:
            return False, None
        
        # Update FPS calculation
        current_time = time.time()
        if self.last_frame_time:
            self.fps = 1 / (current_time - self.last_frame_time)
        self.last_frame_time = current_time
        self.frame_count += 1
        
        # Apply undistortion if calibrated
        if undistort and self.calibrated:
            frame = cv2.undistort(
                frame,
                self.camera_matrix,
                self.dist_coeffs
            )
        
        return True, frame
    
    def calibrate(self, chessboard_size=(9, 6), square_size=0.025):
        """
        Calibrate camera using chessboard pattern.
        
        Args:
            chessboard_size (tuple): Number of inner corners
            square_size (float): Size of squares in meters
            
        Returns:
            bool: True if calibration successful
        """
        # Prepare object points
        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:,:2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1,2)
        objp *= square_size
        
        # Arrays to store object points and image points
        objpoints = []  # 3D points in real world space
        imgpoints = []  # 2D points in image plane
        
        print("Starting calibration. Press 'c' to capture pattern, 'q' to finish.")
        while True:
            ret, frame = self.read(undistort=False)
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
            
            # Draw corners
            frame_draw = frame.copy()
            if ret:
                cv2.drawChessboardCorners(frame_draw, chessboard_size, corners, ret)
            
            cv2.imshow('Calibration', frame_draw)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('c') and ret:
                objpoints.append(objp)
                imgpoints.append(corners)
                print(f"Pattern {len(objpoints)} captured")
            
            elif key == ord('q'):
                break
        
        cv2.destroyWindow('Calibration')
        
        if len(objpoints) < 5:
            print("Not enough patterns captured")
            return False
        
        # Calibrate camera
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None
        )
        
        if ret:
            self.camera_matrix = mtx
            self.dist_coeffs = dist
            self.calibrated = True
            self._save_calibration()
            print("Calibration successful")
            return True
        else:
            print("Calibration failed")
            return False
    
    def auto_exposure(self, target_brightness=127, tolerance=10):
        """
        Auto adjust exposure to reach target brightness.
        
        Args:
            target_brightness (int): Target mean brightness (0-255)
            tolerance (int): Acceptable deviation
        """
        if not self.cap:
            return
        
        current_exposure = self.cap.get(cv2.CAP_PROP_EXPOSURE)
        
        while True:
            ret, frame = self.read(undistort=False)
            if not ret:
                break
            
            mean_brightness = cv2.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))[0]
            
            if abs(mean_brightness - target_brightness) <= tolerance:
                break
            
            # Adjust exposure
            if mean_brightness < target_brightness:
                current_exposure *= 1.1
            else:
                current_exposure *= 0.9
            
            self.cap.set(cv2.CAP_PROP_EXPOSURE, current_exposure)
    
    def _load_calibration(self):
        """Load camera calibration from file."""
        calib_file = Path(config.CALIBRATION_DIR) / "camera_params.yaml"
        
        if not calib_file.exists():
            return
        
        try:
            with open(calib_file, 'r') as f:
                data = yaml.safe_load(f)
                self.camera_matrix = np.array(data['camera_matrix'])
                self.dist_coeffs = np.array(data['dist_coeffs'])
                self.calibrated = True
                print("Camera calibration loaded")
        except Exception as e:
            print(f"Error loading calibration: {e}")
    
    def _save_calibration(self):
        """Save camera calibration to file."""
        calib_file = Path(config.CALIBRATION_DIR) / "camera_params.yaml"
        
        # Ensure directory exists
        calib_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = {
                'camera_matrix': self.camera_matrix.tolist(),
                'dist_coeffs': self.dist_coeffs.tolist()
            }
            
            with open(calib_file, 'w') as f:
                yaml.dump(data, f)
            print("Calibration saved")
        except Exception as e:
            print(f"Error saving calibration: {e}")
    
    def get_stats(self):
        """
        Get camera statistics.
        
        Returns:
            dict: Statistics dictionary
        """
        return {
            'frame_count': self.frame_count,
            'fps': self.fps,
            'resolution': (
                int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            ) if self.cap else None,
            'calibrated': self.calibrated
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


if __name__ == "__main__":
    # Test camera
    camera = Camera()
    
    if not camera.start():
        print("Could not start camera")
        exit()
    
    print("Press 'c' to calibrate, 'e' for auto exposure, 'q' to quit")
    
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            
            # Show stats
            stats = camera.get_stats()
            cv2.putText(
                frame,
                f"FPS: {stats['fps']:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            
            cv2.imshow('Camera Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                camera.calibrate()
            elif key == ord('e'):
                camera.auto_exposure()
    
    finally:
        camera.stop()
        cv2.destroyAllWindows()
        print("\nCamera statistics:")
        print(camera.get_stats())
