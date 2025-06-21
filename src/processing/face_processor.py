# src/processing/face_processor.py
"""
Face processing for detection and recognition
Handles both OpenCV and face_recognition library integration
"""
import cv2
import numpy as np

class ImprovedFaceProcessor:
    """Face processor that uses face_recognition if available, otherwise OpenCV"""
    
    def __init__(self):
        self.use_face_recognition = self._check_face_recognition()
        
        # Always have OpenCV as fallback
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        if self.use_face_recognition:
            print("🎯 Using face_recognition library for recognition")
        else:
            print("🎯 Using OpenCV for detection only")
    
    def _check_face_recognition(self):
        """Check if face_recognition library is available"""
        try:
            import face_recognition
            return True
        except ImportError:
            return False
    
    def detect_and_encode_faces(self, frame):
        """Detect faces and generate encodings (if face_recognition available)"""
        if self.use_face_recognition:
            return self._detect_with_face_recognition(frame)
        else:
            return self._detect_with_opencv(frame)
    
    def _detect_with_face_recognition(self, frame):
        """Use face_recognition library for detection"""
        import face_recognition
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        return face_locations, face_encodings
    
    def _detect_with_opencv(self, frame):
        """Use OpenCV for detection only"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
        
        # Convert to face_recognition format: (top, right, bottom, left)
        face_locations = []
        for (x, y, w, h) in faces:
            face_locations.append((y, x + w, y + h, x))
        
        return face_locations, []  # No encodings available
    
    def recognize_faces(self, frame, known_encodings, known_names, threshold=0.6):
        """Recognize faces in frame"""
        face_locations, face_encodings = self.detect_and_encode_faces(frame)
        
        processed_frame = frame.copy()
        recognition_results = []
        
        if self.use_face_recognition and known_encodings:
            # Use face_recognition for actual recognition
            recognition_results = self._process_recognition(
                face_locations, face_encodings, known_encodings, known_names, threshold
            )
            self._draw_recognition_results(processed_frame, recognition_results)
        else:
            # OpenCV detection only - no recognition
            recognition_results = self._process_detection_only(face_locations)
            self._draw_detection_results(processed_frame, face_locations)
        
        return processed_frame, recognition_results
    
    def _process_recognition(self, face_locations, face_encodings, known_encodings, known_names, threshold):
        """Process face recognition results"""
        import face_recognition
        
        recognition_results = []
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=threshold)
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            name = "Unknown"
            confidence = 0.0
            
            if len(distances) > 0:
                best_match_index = np.argmin(distances)
                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    confidence = 1 - distances[best_match_index]
            
            recognition_results.append((name, confidence, (top, right, bottom, left)))
        
        return recognition_results
    
    def _process_detection_only(self, face_locations):
        """Process detection-only results"""
        recognition_results = []
        
        for (top, right, bottom, left) in face_locations:
            recognition_results.append(("Unknown", 0.0, (top, right, bottom, left)))
        
        return recognition_results
    
    def _draw_recognition_results(self, frame, recognition_results):
        """Draw recognition results on frame"""
        for name, confidence, (top, right, bottom, left) in recognition_results:
            # Determine color based on recognition
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            
            # Draw rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Add label with confidence
            label = f"{name} ({confidence:.2f})" if name != "Unknown" else "Unknown"
            cv2.putText(frame, label, (left, top-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def _draw_detection_results(self, frame, face_locations):
        """Draw detection-only results on frame"""
        for (top, right, bottom, left) in face_locations:
            # Draw rectangle for detected face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 255), 2)
            cv2.putText(frame, "Face Detected", (left, top-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)