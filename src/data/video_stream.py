# src/data/video_stream.py
import cv2

class VideoStream:
    def __init__(self, source=0):
        """
        Initialize the video stream
        
        Args:
            source: Camera index or video file path (0 for default webcam)
        """
        self.source = source
        self.cap = None
    
    def start(self):
        """
        Start the video stream
        """
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
        """
        Release the video stream
        """
        if self.cap is not None:
            self.cap.release()
        self.cap = None

# Test code
if __name__ == "__main__":
    # Create a video stream using the default webcam
    stream = VideoStream().start()
    
    try:
        print(f"Stream started: {stream.width}x{stream.height} @ {stream.fps}fps")
        
        # Display the stream for 10 seconds
        while True:
            ret, frame = stream.read()
            if not ret:
                break
            
            # Display the frame
            cv2.imshow('Video Stream Test', frame)
            
            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        # Clean up
        stream.stop()
        cv2.destroyAllWindows()
        print("Stream stopped")