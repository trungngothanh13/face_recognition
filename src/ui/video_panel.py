# src/ui/video_panel.py
"""
Video display panel for Face Recognition System
Handles video stream, motion detection, and face recognition display
"""
import tkinter as tk
from tkinter import ttk
import cv2
import time
from PIL import Image, ImageTk

from ..processing.video_stream import VideoStream
from ..processing.motion_detector import MotionDetector

class VideoPanel:
    """Video display and control panel"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        # Video components
        self.video_stream = None
        self.motion_detector = None
        
        # Motion detection state
        self.last_motion_time = 0
        self.face_detection_active = False
        self.motion_cooldown = 3.0
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create video panel widgets"""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Live Camera Feed")
        
        # Video display
        self.video_label = tk.Label(
            self.frame, 
            text="Camera feed will appear here", 
            bg="black", 
            fg="white", 
            width=80, 
            height=30
        )
        self.video_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Control buttons
        self.create_control_buttons()
        
        # Recognition status
        self.recognition_status = tk.Label(self.frame, text="", fg="blue")
        self.recognition_status.pack(pady=5)
    
    def create_control_buttons(self):
        """Create control buttons"""
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(pady=10)
        
        self.start_button = ttk.Button(
            control_frame, 
            text="Start Recognition", 
            command=self.main_window.start_recognition
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            control_frame, 
            text="Stop Recognition", 
            command=self.main_window.stop_recognition, 
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.manual_button = ttk.Button(
            control_frame, 
            text="Manual Attendance", 
            command=self.main_window.manual_attendance
        )
        self.manual_button.pack(side=tk.LEFT, padx=5)
    
    def start_video_processing(self):
        """Initialize video processing components"""
        try:
            # Initialize video stream
            self.video_stream = VideoStream(0).start()
            self.motion_detector = MotionDetector(threshold=25, min_area=500)
            
            # Update button states
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            print("✅ Video processing started")
            
        except Exception as e:
            print(f"❌ Failed to start video processing: {e}")
            raise
    
    def stop_video_processing(self):
        """Stop video processing components"""
        # Stop video stream
        if self.video_stream:
            self.video_stream.stop()
            self.video_stream = None
        
        # Reset motion detector
        self.motion_detector = None
        
        # Update button states
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Clear video display
        self.video_label.config(image="", text="Camera feed stopped")
        self.recognition_status.config(text="")
        
        print("📴 Video processing stopped")
    
    def process_frame(self, known_encodings, known_names, face_processor):
        """
        Process a single video frame
        
        Returns:
            recognition_results: List of recognition results
        """
        if not self.video_stream or not self.motion_detector:
            return []
        
        try:
            # Read frame
            ret, frame = self.video_stream.read()
            if not ret:
                return []
            
            # Motion detection
            motion_detected, motion_frame = self.motion_detector.detect(frame)
            current_time = time.time()
            
            # Update motion state
            if motion_detected:
                self.last_motion_time = current_time
                self.face_detection_active = True
            elif current_time - self.last_motion_time > self.motion_cooldown:
                self.face_detection_active = False
            
            recognition_results = []
            
            # Face recognition if active
            if self.face_detection_active and known_encodings:
                processed_frame, results = face_processor.recognize_faces(
                    frame, known_encodings, known_names, threshold=0.6
                )
                recognition_results = results
                display_frame = processed_frame
                
                # Update recognition status
                if results:
                    recognized_names = [r[0] for r in results if r[0] != "Unknown"]
                    if recognized_names:
                        status_text = f"Recognized: {', '.join(set(recognized_names))}"
                    else:
                        status_text = f"Detected {len(results)} face(s)"
                    self.update_recognition_status(status_text)
                else:
                    self.update_recognition_status("")
            else:
                display_frame = motion_frame
                self.update_recognition_status("")
            
            # Add status overlay
            self.add_status_overlay(display_frame)
            
            # Update video display
            self.update_video_display(display_frame)
            
            return recognition_results
            
        except Exception as e:
            print(f"Frame processing error: {e}")
            return []
    
    def add_status_overlay(self, frame):
        """Add status overlay to frame"""
        # System status
        status = "ACTIVE: Face Recognition" if self.face_detection_active else "STANDBY: Motion Detection"
        color = (0, 255, 0) if self.face_detection_active else (128, 128, 128)
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Mode info
        has_faces = len(self.main_window.known_encodings) > 0
        has_recognition = self.main_window.face_processor.use_face_recognition
        
        if has_recognition and has_faces:
            mode_text = "AUTO RECOGNITION"
            mode_color = (0, 255, 0)
        elif has_recognition:
            mode_text = "RECOGNITION READY (No faces enrolled)"
            mode_color = (0, 255, 255)
        else:
            mode_text = "DETECTION ONLY"
            mode_color = (255, 255, 0)
        
        cv2.putText(frame, mode_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, mode_color, 1)
    
    def update_video_display(self, frame):
        """Update the video display with larger size"""
        try:
            # Resize frame for display
            display_frame = cv2.resize(frame, (800, 600))
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_frame)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update label
            self.video_label.config(image=photo, text="")
            self.video_label.image = photo  # Keep reference
            
        except Exception as e:
            print(f"Display update error: {e}")
    
    def update_recognition_status(self, text):
        """Update recognition status text"""
        self.main_window.root.after(0, lambda: self.recognition_status.config(text=text))
    
    def show_recognition_status(self, text, color="blue"):
        """Show recognition status with color"""
        def update_status():
            self.recognition_status.config(text=text, fg=color)
        
        def reset_color():
            self.recognition_status.config(fg="blue")
        
        self.main_window.root.after(0, update_status)
        if color != "blue":
            self.main_window.root.after(3000, reset_color)