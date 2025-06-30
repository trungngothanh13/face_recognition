# src/processing/video_stream.py
"""
Video stream handling for camera input
Improved version with better error handling and camera testing
"""
import cv2
import time

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
        self.width = 0
        self.height = 0
        self.fps = 0
    
    def test_camera(self):
        """Test if camera is available and working"""
        try:
            test_cap = cv2.VideoCapture(self.source)
            if not test_cap.isOpened():
                return False, "Camera not accessible"
            
            # Try to read a frame
            ret, frame = test_cap.read()
            test_cap.release()
            
            if not ret or frame is None:
                return False, "Cannot read frames from camera"
            
            if frame.size == 0:
                return False, "Camera returns empty frames"
            
            return True, "Camera test successful"
            
        except Exception as e:
            return False, f"Camera test failed: {str(e)}"
    
    def start(self):
        """Start the video stream with improved error handling"""
        # Test camera first
        test_result, test_message = self.test_camera()
        if not test_result:
            raise ValueError(f"Camera test failed: {test_message}")
        
        # Initialize capture
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise ValueError(f"Unable to open video source {self.source}")
        
        # Set buffer size to reduce latency
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Get actual video properties
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        print(f"✅ Camera initialized: {self.width}x{self.height} @ {self.fps} FPS")
        
        # Test initial frame read
        ret, frame = self.cap.read()
        if not ret or frame is None or frame.size == 0:
            self.cap.release()
            raise ValueError("Cannot read initial frame from camera")
        
        return self
    
    def read(self):
        """
        Read a frame from the video stream with timeout handling
        
        Returns:
            ret (bool): True if frame read correctly, False otherwise
            frame (numpy.ndarray): The captured frame
        """
        if self.cap is None:
            return False, None
        
        try:
            ret, frame = self.cap.read()
            
            # Additional validation
            if ret and frame is not None and frame.size > 0:
                return True, frame
            else:
                return False, None
                
        except Exception as e:
            print(f"Error reading frame: {e}")
            return False, None
    
    def stop(self):
        """Release the video stream"""
        if self.cap is not None:
            self.cap.release()
            print("📴 Camera released")
        self.cap = None
    
    def get_properties(self):
        """Get video stream properties"""
        if self.cap is None:
            return None
        
        return {
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'source': self.source,
            'is_opened': self.cap.isOpened()
        }
    
    def is_available(self):
        """Check if video stream is available and working"""
        return self.cap is not None and self.cap.isOpened()
    
    @staticmethod
    def list_available_cameras():
        """List all available camera indices"""
        available_cameras = []
        
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    available_cameras.append({
                        'index': i,
                        'width': width,
                        'height': height
                    })
            cap.release()
        
        return available_cameras