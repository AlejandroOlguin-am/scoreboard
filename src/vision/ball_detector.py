"""
Ball Detector Module
Detects colored balls using background subtraction and HSV color filtering.
"""

import cv2
import numpy as np
import config


class BallDetector:
    """
    Detects balls in video frames using hybrid approach:
    1. Background subtraction for motion detection
    2. HSV color filtering for specific ball colors
    3. Morphological operations for noise reduction
    """
    
    def __init__(self):
        """Initialize ball detector with configured parameters."""
        # Background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=config.BG_SUBTRACTOR_HISTORY,
            varThreshold=config.BG_SUBTRACTOR_THRESHOLD,
            detectShadows=config.BG_SUBTRACTOR_DETECT_SHADOWS
        )
        
        # Morphological kernel
        self.kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            config.MORPHOLOGY_KERNEL_SIZE
        )
        
        # Color ranges (HSV)
        self.color_ranges = self._load_color_ranges()
        
        # Statistics
        self.frames_processed = 0
        self.balls_detected = 0
    
    def _load_color_ranges(self):
        """
        Load configured color detection ranges.
        
        Returns:
            dict: Color configurations
        """
        return {
            'red': {
                'lower': [
                    np.array(config.RED_LOWER_1, np.uint8),
                    np.array(config.RED_LOWER_2, np.uint8)
                ],
                'upper': [
                    np.array(config.RED_UPPER_1, np.uint8),
                    np.array(config.RED_UPPER_2, np.uint8)
                ]
            },
            'blue': {
                'lower': [np.array(config.BLUE_LOWER, np.uint8)],
                'upper': [np.array(config.BLUE_UPPER, np.uint8)]
            },
            'green': {
                'lower': [np.array(config.GREEN_LOWER, np.uint8)],
                'upper': [np.array(config.GREEN_UPPER, np.uint8)]
            },
            'black': {
                'lower': [np.array(config.BLACK_LOWER, np.uint8)],
                'upper': [np.array(config.BLACK_UPPER, np.uint8)]
            }
        }
    
    def detect(self, frame, target_colors=None):
        """
        Detect balls in frame.
        
        Args:
            frame: Input video frame (BGR)
            target_colors (list): List of colors to detect (default: all)
            
        Returns:
            list: List of detections as [x, y, width, height]
        """
        if target_colors is None:
            target_colors = ['red']  # Default to red for compatibility
        
        self.frames_processed += 1
        
        # Convert to grayscale for background subtraction
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(gray)
        
        # Threshold to binary
        _, motion_mask = cv2.threshold(fg_mask, 254, 255, cv2.THRESH_BINARY)
        
        # Morphological operations to clean up mask
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_OPEN, self.kernel)
        motion_mask = cv2.dilate(motion_mask, None, iterations=config.DILATION_ITERATIONS)
        
        # Convert to HSV for color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create combined color mask
        color_mask = np.zeros_like(motion_mask)
        
        for color in target_colors:
            if color in self.color_ranges:
                color_config = self.color_ranges[color]
                
                # Handle multiple ranges (e.g., red wraps around hue)
                temp_masks = []
                for lower, upper in zip(color_config['lower'], color_config['upper']):
                    temp_mask = cv2.inRange(hsv, lower, upper)
                    temp_masks.append(temp_mask)
                
                # Combine masks for this color
                if len(temp_masks) > 1:
                    color_specific_mask = cv2.add(temp_masks[0], temp_masks[1])
                else:
                    color_specific_mask = temp_masks[0]
                
                # Add to combined mask
                color_mask = cv2.add(color_mask, color_specific_mask)
        
        # Combine motion and color masks
        combined_mask = cv2.bitwise_and(motion_mask, color_mask)
        
        # Find contours
        contours, _ = cv2.findContours(
            combined_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by area and extract bounding boxes
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if config.MIN_BALL_AREA < area < config.MAX_BALL_AREA:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Additional shape validation (aspect ratio)
                aspect_ratio = w / float(h) if h > 0 else 0
                
                # Balls should be roughly circular (aspect ratio close to 1)
                if 0.5 < aspect_ratio < 2.0:
                    detections.append([x, y, w, h])
                    self.balls_detected += 1
        
        return detections
    
    def detect_with_masks(self, frame, target_colors=None):
        """
        Detect balls and return debug masks for visualization.
        
        Args:
            frame: Input video frame
            target_colors: Colors to detect
            
        Returns:
            tuple: (detections, motion_mask, color_mask, combined_mask)
        """
        if target_colors is None:
            target_colors = ['red']
        
        # Grayscale and background subtraction
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fg_mask = self.bg_subtractor.apply(gray)
        _, motion_mask = cv2.threshold(fg_mask, 254, 255, cv2.THRESH_BINARY)
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_OPEN, self.kernel)
        motion_mask = cv2.dilate(motion_mask, None, iterations=config.DILATION_ITERATIONS)
        
        # HSV color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color_mask = np.zeros_like(motion_mask)
        
        for color in target_colors:
            if color in self.color_ranges:
                color_config = self.color_ranges[color]
                temp_masks = []
                
                for lower, upper in zip(color_config['lower'], color_config['upper']):
                    temp_mask = cv2.inRange(hsv, lower, upper)
                    temp_masks.append(temp_mask)
                
                if len(temp_masks) > 1:
                    color_specific_mask = cv2.add(temp_masks[0], temp_masks[1])
                else:
                    color_specific_mask = temp_masks[0]
                
                color_mask = cv2.add(color_mask, color_specific_mask)
        
        # Combined mask
        combined_mask = cv2.bitwise_and(motion_mask, color_mask)
        
        # Find detections
        contours, _ = cv2.findContours(
            combined_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if config.MIN_BALL_AREA < area < config.MAX_BALL_AREA:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / float(h) if h > 0 else 0
                if 0.5 < aspect_ratio < 2.0:
                    detections.append([x, y, w, h])
        
        return detections, motion_mask, color_mask, combined_mask
    
    def reset_background(self):
        """Reset background model (useful when camera moves or scene changes)."""
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=config.BG_SUBTRACTOR_HISTORY,
            varThreshold=config.BG_SUBTRACTOR_THRESHOLD,
            detectShadows=config.BG_SUBTRACTOR_DETECT_SHADOWS
        )
    
    def get_statistics(self):
        """
        Get detection statistics.
        
        Returns:
            dict: Statistics dictionary
        """
        return {
            'frames_processed': self.frames_processed,
            'balls_detected': self.balls_detected,
            'avg_detections_per_frame': (
                self.balls_detected / self.frames_processed 
                if self.frames_processed > 0 else 0
            )
        }
    
    def calibrate_colors(self, frame):
        """
        Interactive color calibration helper.
        
        Args:
            frame: Sample frame for calibration
            
        Returns:
            dict: Calibrated HSV ranges
        """
        def nothing(x):
            pass
        
        # Create window with trackbars
        cv2.namedWindow('Color Calibration')
        
        # HSV range trackbars
        cv2.createTrackbar('H Min', 'Color Calibration', 0, 179, nothing)
        cv2.createTrackbar('H Max', 'Color Calibration', 179, 179, nothing)
        cv2.createTrackbar('S Min', 'Color Calibration', 0, 255, nothing)
        cv2.createTrackbar('S Max', 'Color Calibration', 255, 255, nothing)
        cv2.createTrackbar('V Min', 'Color Calibration', 0, 255, nothing)
        cv2.createTrackbar('V Max', 'Color Calibration', 255, 255, nothing)
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        print("Adjust trackbars to isolate ball color. Press 'q' to finish.")
        
        while True:
            # Get trackbar values
            h_min = cv2.getTrackbarPos('H Min', 'Color Calibration')
            h_max = cv2.getTrackbarPos('H Max', 'Color Calibration')
            s_min = cv2.getTrackbarPos('S Min', 'Color Calibration')
            s_max = cv2.getTrackbarPos('S Max', 'Color Calibration')
            v_min = cv2.getTrackbarPos('V Min', 'Color Calibration')
            v_max = cv2.getTrackbarPos('V Max', 'Color Calibration')
            
            # Create mask
            lower = np.array([h_min, s_min, v_min])
            upper = np.array([h_max, s_max, v_max])
            mask = cv2.inRange(hsv, lower, upper)
            
            # Apply mask
            result = cv2.bitwise_and(frame, frame, mask=mask)
            
            # Display
            cv2.imshow('Original', frame)
            cv2.imshow('Mask', mask)
            cv2.imshow('Result', result)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyWindow('Color Calibration')
        
        return {
            'lower': (h_min, s_min, v_min),
            'upper': (h_max, s_max, v_max)
        }


if __name__ == "__main__":
    # Test ball detector
    print("Testing Ball Detector...")
    
    detector = BallDetector()
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit, 'r' to reset background, 'c' to calibrate colors")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect balls
        detections, motion_mask, color_mask, combined_mask = detector.detect_with_masks(frame)
        
        # Draw detections
        for det in detections:
            x, y, w, h = det
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "BALL", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Show stats
        stats = detector.get_statistics()
        cv2.putText(
            frame,
            f"Detected: {len(detections)} | Total: {stats['balls_detected']}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        # Display
        cv2.imshow('Detection', frame)
        cv2.imshow('Motion Mask', motion_mask)
        cv2.imshow('Color Mask', color_mask)
        cv2.imshow('Combined Mask', combined_mask)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            detector.reset_background()
            print("Background model reset")
        elif key == ord('c'):
            ranges = detector.calibrate_colors(frame)
            print(f"Calibrated ranges: {ranges}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nFinal Statistics: {detector.get_statistics()}")