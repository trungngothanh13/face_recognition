# Update src/processing/video_processor.py
import cv2
import time
import os
from datetime import datetime
from threading import Thread

class VideoProcessor:
    def __init__(self, video_stream, motion_detector, face_processor):
        """
        Initialize the video processor
        
        Args:
            video_stream: VideoStream object
            motion_detector: MotionDetector object
            face_processor: FaceProcessor object
        """
        self.video_stream = video_stream
        self.motion_detector = motion_detector
        self.face_processor = face_processor
        
        self.running = False
        self.processing_thread = None
        
        # Settings
        self.motion_cooldown = 2.0  # Seconds to wait after motion detected
    
    def start(self):
        """
        Start the video processing loop in a separate thread
        """
        if self.running:
            return
        
        self.running = True
        self.processing_thread = Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        return self
    
    def stop(self):
        """
        Stop the video processing
        """
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
            self.processing_thread = None
    
    def _processing_loop(self):
        """
        Main processing loop
        """
        last_motion_time = 0
        face_detection_active = False
        
        while self.running:
            # Read frame
            ret, frame = self.video_stream.read()
            if not ret:
                break
            
            # Create a copy for display
            display_frame = frame.copy()
            
            # Motion detection
            motion_detected, motion_frame = self.motion_detector.detect(frame)
            
            # Update face detection state
            current_time = time.time()
            if motion_detected:
                last_motion_time = current_time
                face_detection_active = True
            elif current_time - last_motion_time > self.motion_cooldown:
                face_detection_active = False
            
            # Face detection if active
            if face_detection_active:
                # Process frame for face detection
                face_frame, results = self.face_processor.process_frame(frame)
                
                # Use face frame for display
                display_frame = face_frame
            else:
                # Use motion frame for display when no faces are being processed
                display_frame = motion_frame
            
            # Add status text
            status = "Motion Detected - Face Processing Active" if face_detection_active else "No Motion"
            cv2.putText(display_frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display frame
            cv2.imshow("Face Recognition System", display_frame)
            
            # Check for exit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Clean up
        cv2.destroyAllWindows()


# Test function
if __name__ == "__main__":
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Import required modules
    from data.video_stream import VideoStream
    from processing.motion_detector import MotionDetector
    from processing.face_processor import FaceProcessor
    
    # Create components
    stream = VideoStream(0).start()
    motion_detector = MotionDetector(threshold=20, min_area=500)
    face_processor = FaceProcessor()
    
    # Create video processor
    processor = VideoProcessor(
        video_stream=stream,
        motion_detector=motion_detector,
        face_processor=face_processor
    )
    
    try:
        # Start processing
        processor.start()
        
        # Wait for processing to finish
        while True:
            if not processor.running:
                break
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("Interrupted by user")
        
    finally:
        # Clean up
        processor.stop()
        stream.stop()