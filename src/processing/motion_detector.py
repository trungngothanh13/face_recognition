# Create a new file: src/processing/motion_detector.py
import cv2
import numpy as np

class MotionDetector:
    def __init__(self, threshold=25, min_area=500):
        """
        Initialize the motion detector using frame differencing
        
        Args:
            threshold: Threshold for detecting motion
            min_area: Minimum contour area to be considered as motion
        """
        self.threshold = threshold
        self.min_area = min_area
        self.prev_frame = None
        self.motion_detected = False
    
    def detect(self, frame):
        """
        Detect motion in the frame
        
        Args:
            frame: Current video frame
            
        Returns:
            motion_detected: True if motion is detected, False otherwise
            processed_frame: Frame with motion highlighted
        """
        # Make a copy of the frame for drawing
        output_frame = frame.copy()
        
        # Convert to grayscale and apply Gaussian blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # If first frame, save it and return
        if self.prev_frame is None:
            self.prev_frame = gray
            return False, output_frame
        
        # Compute absolute difference between current and previous frame
        frame_diff = cv2.absdiff(self.prev_frame, gray)
        
        # Apply threshold
        thresh = cv2.threshold(frame_diff, self.threshold, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate threshold image to fill in holes
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours in the threshold image
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Reset motion flag
        self.motion_detected = False
        
        # Check each contour
        for contour in contours:
            if cv2.contourArea(contour) < self.min_area:
                continue
            
            # Motion detected
            self.motion_detected = True
            
            # Draw rectangle around contour
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(output_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Update previous frame
        self.prev_frame = gray
        
        # Draw motion status text
        status = "Motion Detected" if self.motion_detected else "No Motion"
        cv2.putText(output_frame, status, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return self.motion_detected, output_frame


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
    
    # Create motion detector
    detector = MotionDetector(threshold=20, min_area=500)
    
    try:
        while True:
            # Read frame
            ret, frame = stream.read()
            if not ret:
                break
            
            # Detect motion
            motion, processed_frame = detector.detect(frame)
            
            # Display result
            cv2.imshow("Motion Detection", processed_frame)
            
            # Break on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        # Clean up
        stream.stop()
        cv2.destroyAllWindows()