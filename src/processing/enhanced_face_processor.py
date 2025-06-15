# Replace your entire src/processing/enhanced_face_processor.py with this code

import cv2
import numpy as np
import os
import time
from datetime import datetime

class EnhancedFaceProcessor:
    def __init__(self, detection_model="combined"):
        """
        Initialize the enhanced face processor (Clean version - no DNN, no advanced tracking)
        
        Args:
            detection_model: Detection method ('opencv', 'dlib', 'combined')
        """
        self.detection_model = detection_model
        
        print(f"Initializing Enhanced Face Processor with {detection_model} mode...")
        
        # Initialize OpenCV Haar Cascade
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
            print("✅ OpenCV Haar cascades loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading OpenCV cascades: {e}")
            raise
        
        # Initialize dlib detector (optional)
        self.dlib_available = False
        if detection_model in ['dlib', 'combined']:
            try:
                import dlib
                self.dlib_detector = dlib.get_frontal_face_detector()
                self.dlib_available = True
                print("✅ dlib face detector loaded successfully!")
            except ImportError:
                print("⚠️ dlib not available - install with: pip install dlib")
            except Exception as e:
                print(f"⚠️ dlib error: {e}")
        
        # Face quality thresholds
        self.min_face_size = 60
        self.max_face_size = 400
        self.min_quality_score = 0.2
        
        # Simple tracking variables (no advanced tracking)
        self.last_faces = []
        self.face_id_counter = 0
        
        print(f"Available methods: OpenCV=✅, dlib={'✅' if self.dlib_available else '❌'}")
        print("Enhanced Face Processor ready!")
    
    def detect_faces_opencv(self, frame):
        """
        Detect faces using OpenCV Haar cascades
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect frontal faces
        frontal_faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50),
            maxSize=(300, 300)
        )
        
        # Detect profile faces
        profile_faces = self.profile_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50),
            maxSize=(300, 300)
        )
        
        # Combine detections
        faces = []
        for (x, y, w, h) in frontal_faces:
            faces.append((x, y, w, h, 0.8))  # confidence score
        
        for (x, y, w, h) in profile_faces:
            faces.append((x, y, w, h, 0.7))  # lower confidence for profile
        
        return faces
    
    def detect_faces_dlib(self, frame):
        """
        Detect faces using dlib HOG detector
        """
        if not self.dlib_available:
            return []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = self.dlib_detector(gray, 1)
        
        faces = []
        for detection in detections:
            x = detection.left()
            y = detection.top()
            w = detection.width()
            h = detection.height()
            
            # Estimate confidence based on face size
            size_score = min(w * h / (100 * 100), 1.0)
            confidence = 0.6 + (size_score * 0.3)
            
            faces.append((x, y, w, h, confidence))
        
        return faces
    
    def assess_face_quality(self, frame, face_box):
        """
        Assess the quality of a detected face
        """
        x, y, w, h = face_box
        
        # Extract face region
        if y < 0 or x < 0 or y + h > frame.shape[0] or x + w > frame.shape[1]:
            return 0.0
        
        face_region = frame[y:y+h, x:x+w]
        if face_region.size == 0:
            return 0.0
        
        try:
            # Convert to grayscale
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            
            # Size score
            face_area = w * h
            ideal_area = 120 * 120
            size_score = max(0, 1.0 - abs(face_area - ideal_area) / ideal_area)
            
            # Sharpness score
            laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 500.0, 1.0)
            
            # Brightness score
            mean_brightness = np.mean(gray_face)
            brightness_score = 1.0 - abs(mean_brightness - 127) / 127
            
            # Combine scores
            quality = (size_score * 0.4 + sharpness_score * 0.4 + brightness_score * 0.2)
            return max(0, min(1, quality))
            
        except Exception as e:
            print(f"Error in quality assessment: {e}")
            return 0.5  # Default quality
    
    def remove_overlapping_faces(self, faces):
        """
        Remove overlapping face detections
        """
        if len(faces) <= 1:
            return faces
        
        # Sort by confidence
        faces = sorted(faces, key=lambda x: x[4], reverse=True)
        
        filtered_faces = []
        for face in faces:
            x1, y1, w1, h1, conf1 = face
            
            # Check overlap with existing faces
            overlap = False
            for existing in filtered_faces:
                x2, y2, w2, h2, conf2 = existing
                
                # Calculate overlap
                xi1 = max(x1, x2)
                yi1 = max(y1, y2)
                xi2 = min(x1 + w1, x2 + w2)
                yi2 = min(y1 + h1, y2 + h2)
                
                if xi2 > xi1 and yi2 > yi1:
                    intersection = (xi2 - xi1) * (yi2 - yi1)
                    union = w1 * h1 + w2 * h2 - intersection
                    iou = intersection / union if union > 0 else 0
                    
                    if iou > 0.3:  # 30% overlap threshold
                        overlap = True
                        break
            
            if not overlap:
                filtered_faces.append(face)
        
        return filtered_faces
    
    def process_frame(self, frame, detect_only=True):
        """
        Process a video frame to detect faces
        
        Args:
            frame: Video frame to process
            detect_only: If True, only detect faces without recognition
            
        Returns:
            processed_frame: Frame with detection results
            results: List of tuples (name, location, quality, confidence) for each face
        """
        # Create output frame
        output_frame = frame.copy()
        results = []
        
        try:
            # Collect detections from different methods
            all_faces = []
            
            if self.detection_model in ['opencv', 'combined']:
                opencv_faces = self.detect_faces_opencv(frame)
                all_faces.extend(opencv_faces)
            
            if self.detection_model in ['dlib', 'combined'] and self.dlib_available:
                dlib_faces = self.detect_faces_dlib(frame)
                all_faces.extend(dlib_faces)
            
            # Remove overlapping detections
            unique_faces = self.remove_overlapping_faces(all_faces)
            
            # Process each face
            for i, face_data in enumerate(unique_faces):
                x, y, w, h, confidence = face_data
                
                # Ensure coordinates are valid
                x = max(0, x)
                y = max(0, y)
                w = min(w, frame.shape[1] - x)
                h = min(h, frame.shape[0] - y)
                
                # Skip if face is too small or too large
                if w < self.min_face_size or h < self.min_face_size:
                    continue
                if w > self.max_face_size or h > self.max_face_size:
                    continue
                
                # Assess face quality
                quality = self.assess_face_quality(frame, (x, y, w, h))
                
                # Skip very low quality faces
                if quality < self.min_quality_score:
                    continue
                
                # Determine color based on quality
                if quality > 0.7:
                    color = (0, 255, 0)  # Green for high quality
                elif quality > 0.4:
                    color = (0, 255, 255)  # Yellow for medium quality
                else:
                    color = (0, 165, 255)  # Orange for low quality
                
                # Draw rectangle
                cv2.rectangle(output_frame, (x, y), (x + w, y + h), color, 2)
                
                # Add label
                name = "Unknown"
                label = f"{name} (C:{confidence:.2f} Q:{quality:.2f})"
                
                # Put text with background
                (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(output_frame, (x, y - text_height - 10), (x + text_width, y), color, -1)
                cv2.putText(output_frame, label, (x, y - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                
                # Add to results (format: name, location, quality, confidence)
                results.append((name, (y, x + w, y + h, x), quality, confidence))
            
            # Add status information
            methods_used = []
            if self.detection_model in ['opencv', 'combined']:
                methods_used.append("OpenCV")
            if self.detection_model in ['dlib', 'combined'] and self.dlib_available:
                methods_used.append("dlib")
            
            status = f"Methods: {'+'.join(methods_used)} | Faces: {len(results)}"
            cv2.putText(output_frame, status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
        except Exception as e:
            print(f"Error in process_frame: {e}")
            # Return original frame with error message
            cv2.putText(output_frame, f"Error: {str(e)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return output_frame, results


# Test function
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from data.video_stream import VideoStream
    
    print("Testing Simple Enhanced Face Processor")
    
    # Test processor creation
    processor = EnhancedFaceProcessor(detection_model="combined")
    
    # Test with video
    stream = VideoStream(0).start()
    
    try:
        print("Starting video test... Press 'q' to quit")
        
        for i in range(100):
            ret, frame = stream.read()
            if not ret:
                break
            
            processed_frame, results = processor.process_frame(frame)
            cv2.imshow("Simple Enhanced Detection", processed_frame)
            
            if results:
                print(f"Frame {i}: Found {len(results)} faces")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        stream.stop()
        cv2.destroyAllWindows()
        print("Test completed!")