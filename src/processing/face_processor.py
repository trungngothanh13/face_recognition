# Update src/processing/face_processor.py
import cv2
import numpy as np
import os
import time
from datetime import datetime

class FaceProcessor:
    def __init__(self, detection_model="hog"):
        """
        Initialize the face processor
        
        Args:
            detection_model: Face detection model to use ('hog' or 'cnn')
        """
        self.detection_model = detection_model
        
        # Initialize face database
        self.known_face_encodings = []
        self.known_face_names = []
        
        # Load face detector from OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def process_frame(self, frame, detect_only=True):
        """
        Process a video frame to detect faces
        
        Args:
            frame: Video frame to process
            detect_only: If True, only detect faces without recognition
            
        Returns:
            processed_frame: Frame with detection results
            results: List of tuples (name, location) for each face
        """
        # Create a copy of the frame for drawing
        output_frame = frame.copy()
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Initialize results
        results = []
        
        # Process each face
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(output_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Add label
            name = "Unknown"
            cv2.putText(output_frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Add to results
            results.append((name, (y, x + w, y + h, x)))
        
        return output_frame, results


# Test function
if __name__ == "__main__":
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Import video stream class
    from data.video_stream import VideoStream
    
    # Create video stream
    stream = VideoStream(0).start()
    
    # Create face processor
    processor = FaceProcessor()
    
    try:
        while True:
            # Read frame
            ret, frame = stream.read()
            if not ret:
                break
            
            # Process frame
            processed_frame, results = processor.process_frame(frame)
            
            # Display number of faces detected
            cv2.putText(
                processed_frame, 
                f"Faces: {len(results)}", 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1, 
                (0, 0, 255), 
                2
            )
            
            # Display result
            cv2.imshow("Face Detection", processed_frame)
            
            # Break on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        # Clean up
        stream.stop()
        cv2.destroyAllWindows()