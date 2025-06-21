# src/processing/video_stream.py
"""
Video stream handling for camera input
Simplified and extracted from original video_stream.py
"""
import cv2

class VideoStream:
    """Video stream handler for camera input"""
    
    def __init__(self, source=0):
        """
        Initialize the video stream
        
        Args:
            source: Camera index or video file path (0 for default webcam)
        """
        self.source = source
        self.cap = None
    
    def start(self):
        """Start the video stream"""
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise ValueError(f"Unable to open video source {self.source}")
        
        # Get video properties
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        return self
    
    def read(self):
        """
        Read a frame from the video stream
        
        Returns:
            ret (bool): True if frame read correctly, False otherwise
            frame (numpy.ndarray): The captured frame
        """
        if self.cap is None:
            raise ValueError("Stream not started. Call 'start()' first.")
        
        return self.cap.read()
    
    def stop(self):
        """Release the video stream"""
        if self.cap is not None:
            self.cap.release()
        self.cap = None
    
    def get_properties(self):
        """Get video stream properties"""
        if self.cap is None:
            return None
        
        return {
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'source': self.source
        }