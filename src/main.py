import cv2
import numpy as np
import time
import threading
import argparse
from tkinter import ttk
import tkinter as tk
from pathlib import Path

# Import custom modules
from vision.ball_detector import BallDetector
from vision.tracker import ObjectTracker
from communication.serial_handler import SerialHandler, MockSerialHandler
from scoring.timer import MatchTimer
from scoring.score_manager import ScoreManager
import config


class RoboticsScoreSystem:
    """Main application class for the scoring system."""
    
    def __init__(self, simulate=False, record=False):
        """
        Initialize the scoring system.
        
        Args:
            simulate (bool): Run without hardware (mock mode)
            record (bool): Record video output
        """
        self.simulate = simulate
        self.record = record
        self.running = False
        
        # Initialize components
        self.timer = MatchTimer(config.MATCH_DURATION)
        self.score_manager = ScoreManager()
        self.tracker = ObjectTracker(max_disappeared=30)
        self.ball_detector = BallDetector()
        
        # Serial communication
        if simulate:
            self.serial = MockSerialHandler()
        else:
            self.serial = SerialHandler(
                port=config.SERIAL_PORT,
                baudrate=config.BAUDRATE
            )
        
        # Camera setup
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        
        # Video writer
        self.video_writer = None
        if record:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(
                'output_match.avi',
                fourcc,
                20.0,
                (config.FRAME_WIDTH, config.FRAME_HEIGHT)
            )
        
        # Threading
        self.lock = threading.Lock()
        self.opencv_thread = None
        
        # GUI
        self.root = None
        self.setup_gui()
    
    def setup_gui(self):
        """Setup Tkinter GUI for match control."""
        self.root = tk.Tk()
        self.root.title("Robotics Competition Scorer - Control Panel")
        self.root.geometry("500x300")
        
        # Title
        title = tk.Label(
            self.root,
            text="🤖 Competition Control Panel",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=20)
        
        # Timer display
        self.timer_label = tk.Label(
            self.root,
            text="00:00",
            font=("Arial", 48, "bold"),
            fg="red"
        )
        self.timer_label.pack(pady=10)
        
        # Score display
        score_frame = tk.Frame(self.root)
        score_frame.pack(pady=10)
        
        tk.Label(score_frame, text="Red Alliance:", font=("Arial", 12)).grid(row=0, column=0, padx=10)
        self.red_score_label = tk.Label(score_frame, text="0", font=("Arial", 20, "bold"), fg="red")
        self.red_score_label.grid(row=0, column=1)
        
        tk.Label(score_frame, text="Blue Alliance:", font=("Arial", 12)).grid(row=1, column=0, padx=10)
        self.blue_score_label = tk.Label(score_frame, text="0", font=("Arial", 20, "bold"), fg="blue")
        self.blue_score_label.grid(row=1, column=1)
        
        # Control buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.start_btn = ttk.Button(
            button_frame,
            text="▶ Start Match",
            command=self.start_match,
            width=15
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏸ Stop",
            command=self.stop_match,
            width=15,
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.reset_btn = ttk.Button(
            button_frame,
            text="🔄 Reset",
            command=self.reset_match,
            width=15
        )
        self.reset_btn.grid(row=0, column=2, padx=5)
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready to start",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Update GUI periodically
        self.update_gui()
    
    def start_match(self):
        """Start the competition match."""
        if not self.running:
            # Connect to PIC
            if not self.serial.connected:
                if not self.serial.connect():
                    self.status_label.config(text="❌ Failed to connect to hardware")
                    return
            
            # Start timer
            self.timer.start()
            self.running = True
            
            # Signal PIC
            self.serial.start_match()
            
            # Start vision thread
            self.opencv_thread = threading.Thread(target=self.vision_loop, daemon=True)
            self.opencv_thread.start()
            
            # Update GUI
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="🟢 Match in progress")
    
    def stop_match(self):
        """Stop the current match."""
        if self.running:
            self.running = False
            self.timer.stop()
            self.serial.stop_match()
            
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="⏸ Match stopped")
    
    def reset_match(self):
        """Reset match to initial state."""
        self.stop_match()
        
        self.timer.reset()
        self.score_manager.reset()
        self.tracker = ObjectTracker(max_disappeared=30)
        self.serial.reset_match()
        
        self.status_label.config(text="🔄 Match reset - Ready to start")
    
    def vision_loop(self):
        """Main vision processing loop."""
        print("Starting vision loop...")
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame")
                break
            
            # Define region of interest (scoring zone)
            roi = frame[
                config.ROI_Y:config.ROI_Y + config.ROI_HEIGHT,
                config.ROI_X:config.ROI_X + config.ROI_WIDTH
            ]
            
            # Detect balls in ROI
            detections = self.ball_detector.detect(roi)
            
            # Track objects
            tracked_objects = self.tracker.update(detections)
            
            # Update scores based on tracked IDs
            max_id = self.tracker.get_max_id()
            self.score_manager.update_from_tracking(max_id)
            
            # Draw visualizations
            self.draw_overlay(frame, roi, tracked_objects)
            
            # Send data to PIC
            self.send_to_pic()
            
            # Record if enabled
            if self.video_writer:
                self.video_writer.write(frame)
            
            # Display
            cv2.imshow("Competition View", frame)
            cv2.imshow("Detection Zone", roi)
            
            # Check for exit
            if cv2.waitKey(10) & 0xFF == 27:  # ESC key
                break
        
        print("Vision loop ended")
    
    def draw_overlay(self, frame, roi, tracked_objects):
        """
        Draw score overlays and visualizations.
        
        Args:
            frame: Main video frame
            roi: Region of interest
            tracked_objects: List of tracked objects
        """
        # Red alliance score
        cv2.rectangle(frame, (0, 0), (400, 60), (0, 0, 255), -1)
        red_text = f'RED: {self.score_manager.get_red_score()} pts'
        cv2.putText(frame, red_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Blue alliance score
        cv2.rectangle(frame, (frame.shape[1] - 400, 0), (frame.shape[1], 60), (255, 0, 0), -1)
        blue_text = f'BLUE: {self.score_manager.get_blue_score()} pts'
        cv2.putText(frame, blue_text, (frame.shape[1] - 380, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Timer
        cv2.rectangle(frame, (450, 0), (830, 80), (0, 0, 0), -1)
        timer_text = self.timer.format_time()
        cv2.putText(frame, timer_text, (frame.shape[1] // 2 - 80, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
        # Draw tracked objects
        for obj in tracked_objects:
            x, y, w, h, obj_id = obj
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(roi, f'ID:{obj_id}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Draw ROI rectangle on main frame
        cv2.rectangle(
            frame,
            (config.ROI_X, config.ROI_Y),
            (config.ROI_X + config.ROI_WIDTH, config.ROI_Y + config.ROI_HEIGHT),
            (255, 255, 0),
            2
        )
    
    def send_to_pic(self):
        """Send current scores and timer to PIC microcontroller."""
        if self.serial.connected:
            # Get scores
            red_score = self.score_manager.get_red_score()
            blue_score = self.score_manager.get_blue_score()
            
            # Get timer
            minutes, seconds = self.timer.get_time_components()
            
            # Send to PIC
            self.serial.send_scores(red_score, blue_score)
            self.serial.send_timer(minutes, seconds)
    
    def update_gui(self):
        """Update GUI labels periodically."""
        if self.root:
            # Update timer display
            self.timer_label.config(text=self.timer.format_time())
            
            # Update scores
            self.red_score_label.config(text=str(self.score_manager.get_red_score()))
            self.blue_score_label.config(text=str(self.score_manager.get_blue_score()))
            
            # Check if time expired
            if self.timer.is_expired() and self.running:
                self.stop_match()
                self.status_label.config(text="⏱ Time expired!")
            
            # Schedule next update
            self.root.after(100, self.update_gui)
    
    def run(self):
        """Start the application."""
        print("🤖 Robotics Scoring System Starting...")
        print(f"Mode: {'SIMULATION' if self.simulate else 'HARDWARE'}")
        print(f"Camera: Index {config.CAMERA_INDEX}")
        print(f"Serial: {config.SERIAL_PORT} @ {config.BAUDRATE} baud")
        
        try:
            self.root.mainloop()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("Shutting down...")
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        if self.video_writer:
            self.video_writer.release()
        
        if self.serial:
            self.serial.disconnect()
        
        cv2.destroyAllWindows()
        print("Shutdown complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Robotics Competition Scoring System')
    parser.add_argument('--simulate', action='store_true', help='Run without hardware')
    parser.add_argument('--record', action='store_true', help='Record video output')
    parser.add_argument('--camera', type=int, default=0, help='Camera index')
    
    args = parser.parse_args()
    
    # Override config if specified
    if args.camera is not None:
        config.CAMERA_INDEX = args.camera
    
    # Create and run application
    app = RoboticsScoreSystem(simulate=args.simulate, record=args.record)
    app.run()


if __name__ == "__main__":
    main()