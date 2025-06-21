# src/processing/face_enrollment.py
import cv2
import numpy as np
import time
from datetime import datetime
import face_recognition

class EnhancedFaceProcessor:
    """Enhanced face processor using the face_recognition library"""
    
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        
    def detect_and_encode_faces(self, frame):
        """
        Detect faces and generate encodings
        
        Args:
            frame: Video frame (BGR format from OpenCV)
            
        Returns:
            face_locations: List of face locations
            face_encodings: List of face encodings
            processed_frame: Frame with face boxes drawn
        """
        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Draw rectangles around faces
        processed_frame = frame.copy()
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(processed_frame, (left, top), (right, bottom), (0, 255, 0), 2)
            # cv2.putText(processed_frame, "Face Detected", (left, top-10), 
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return face_locations, face_encodings, processed_frame
    
    def recognize_faces(self, frame, known_encodings, known_names, threshold=0.6):
        """
        Recognize faces in a frame against known faces
        
        Args:
            frame: Video frame
            known_encodings: List of known face encodings
            known_names: List of corresponding names
            threshold: Recognition threshold
            
        Returns:
            processed_frame: Frame with recognition results
            recognition_results: List of (name, confidence, location) tuples
        """
        face_locations, face_encodings, processed_frame = self.detect_and_encode_faces(frame)
        recognition_results = []
        
        # Process each detected face
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare with known faces
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=threshold)
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            name = "Unknown"
            confidence = 0.0
            
            if len(distances) > 0:
                best_match_index = np.argmin(distances)
                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    confidence = 1 - distances[best_match_index]
            
            # Draw results
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(processed_frame, (left, top), (right, bottom), color, 2)
            
            # Add label with confidence
            label = f"{name} ({confidence:.2f})" if name != "Unknown" else "Unknown"
            cv2.putText(processed_frame, label, (left, top-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            recognition_results.append((name, confidence, (top, right, bottom, left)))
        
        return processed_frame, recognition_results


class FaceEnrollment:
    """Handle face enrollment process"""
    
    def __init__(self, face_database, video_stream_class):
        self.face_db = face_database
        self.video_stream_class = video_stream_class
        self.face_processor = EnhancedFaceProcessor()
    
    def enroll_person(self, person_name, num_samples=5, sample_delay=2.0):
        """
        Enroll a person's face by capturing multiple samples
        
        Args:
            person_name: Name of the person to enroll
            num_samples: Number of face samples to capture
            sample_delay: Delay between samples in seconds
            
        Returns:
            bool: True if enrollment successful, False otherwise
        """
        print(f"🎯 Starting face enrollment for: {person_name}")
        print(f"📸 Will capture {num_samples} samples with {sample_delay}s delay between each")
        print("📋 Instructions:")
        print("   - Look directly at the camera")
        print("   - Keep your face well-lit")
        print("   - Move slightly between samples for variety")
        print("   - Press 'q' to quit early")
        print("\n⏰ Starting in 3 seconds...")
        time.sleep(3)
        
        # Initialize video stream
        stream = self.video_stream_class(0).start()
        time.sleep(1.0)  # Let camera warm up
        
        enrolled_encodings = []
        sample_count = 0
        last_sample_time = 0
        
        try:
            while sample_count < num_samples:
                ret, frame = stream.read()
                if not ret:
                    break
                
                # Detect faces and get encodings
                face_locations, face_encodings, processed_frame = self.face_processor.detect_and_encode_faces(frame)
                
                # Add sample counter and instructions to frame
                cv2.putText(processed_frame, f"Enrolling: {person_name}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(processed_frame, f"Samples: {sample_count}/{num_samples}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                current_time = time.time()
                
                # Check if we can capture a sample
                if (len(face_encodings) == 1 and  # Exactly one face
                    current_time - last_sample_time > sample_delay):
                    
                    # Capture the sample
                    enrolled_encodings.append(face_encodings[0])
                    sample_count += 1
                    last_sample_time = current_time
                    
                    # Visual feedback
                    cv2.putText(processed_frame, f"CAPTURED! Sample {sample_count}", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    print(f"✅ Captured sample {sample_count}/{num_samples}")
                    
                elif len(face_encodings) == 0:
                    cv2.putText(processed_frame, "No face detected", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                elif len(face_encodings) > 1:
                    cv2.putText(processed_frame, "Multiple faces - show only one", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Show the frame
                cv2.imshow("Face Enrollment", processed_frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            stream.stop()
            cv2.destroyAllWindows()
        
        # Save enrolled faces to database
        if enrolled_encodings:
            print(f"\n💾 Saving {len(enrolled_encodings)} samples to database...")
            for i, encoding in enumerate(enrolled_encodings):
                face_id = self.face_db.add_face(
                    name=person_name,
                    face_encoding=encoding,
                    additional_info={
                        "sample_number": i + 1,
                        "total_samples": len(enrolled_encodings),
                        "enrollment_session": datetime.now().isoformat()
                    }
                )
                print(f"   ✅ Saved sample {i + 1} with ID: {face_id}")
            
            print(f"🎉 Successfully enrolled {person_name} with {len(enrolled_encodings)} samples!")
            return True
        else:
            print(f"❌ No valid face samples captured for {person_name}")
            return False
    
    def test_recognition(self, recognition_threshold=0.6):
        """
        Test face recognition with enrolled faces
        
        Args:
            recognition_threshold: Minimum confidence for recognition
        """
        print("🧪 Testing face recognition...")
        print("📋 Instructions:")
        print("   - Look at the camera")
        print("   - The system will try to recognize you")
        print("   - Press 'q' to quit")
        
        # Load all enrolled faces
        all_faces = self.face_db.get_all_faces()
        known_names = [face[0] for face in all_faces]
        known_encodings = [face[1] for face in all_faces]
        
        print(f"📚 Loaded {len(known_names)} face samples from database")
        
        # Initialize video stream
        stream = self.video_stream_class(0).start()
        time.sleep(1.0)
        
        try:
            while True:
                ret, frame = stream.read()
                if not ret:
                    break
                
                # Recognize faces
                processed_frame, results = self.face_processor.recognize_faces(
                    frame, known_encodings, known_names, recognition_threshold
                )
                
                # Record recognition events
                for name, confidence, location in results:
                    if name != "Unknown" and confidence > recognition_threshold:
                        self.face_db.record_recognition_event(
                            name=name,
                            confidence=confidence,
                            location=location
                        )
                
                # Show frame
                cv2.imshow("Face Recognition Test", processed_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            stream.stop()
            cv2.destroyAllWindows()
        
        print("✅ Recognition test completed!")
    
    def get_enrollment_stats(self):
        """Get enrollment statistics"""
        face_count = self.face_db.faces_collection.count_documents({})
        event_count = self.face_db.events_collection.count_documents({})
        
        # Get unique names
        pipeline = [{"$group": {"_id": "$name"}}]
        unique_people = list(self.face_db.faces_collection.aggregate(pipeline))
        people_count = len(unique_people)
        
        stats = {
            "total_face_samples": face_count,
            "unique_people": people_count,
            "recognition_events": event_count
        }
        
        return stats
    
    def list_enrolled_people(self):
        """List all enrolled people with their sample counts"""
        pipeline = [
            {"$group": {"_id": "$name", "sample_count": {"$sum": 1}, "last_enrollment": {"$max": "$created_at"}}}
        ]
        
        people = list(self.face_db.faces_collection.aggregate(pipeline))
        return people


# Convenience function for quick enrollment
def quick_enroll(person_name, num_samples=5):
    """
    Quick enrollment function for notebook use
    
    Args:
        person_name: Name of person to enroll
        num_samples: Number of samples to capture
        
    Returns:
        bool: Success status
    """
    from ..database.video_stream import VideoStream
    from ..database.face_database import FaceDatabase
    
    # Create components
    face_db = FaceDatabase()
    enrollment = FaceEnrollment(face_db, VideoStream)
    
    try:
        # Run enrollment
        success = enrollment.enroll_person(person_name, num_samples)
        
        if success:
            # Show stats
            stats = enrollment.get_enrollment_stats()
            print(f"\n📊 Updated Database Stats:")
            print(f"   - Total face samples: {stats['total_face_samples']}")
            print(f"   - Unique people: {stats['unique_people']}")
            print(f"   - Recognition events: {stats['recognition_events']}")
        
        return success
        
    finally:
        face_db.close()


def quick_test():
    """Quick recognition test function for notebook use"""
    from ..database.video_stream import VideoStream
    from ..database.face_database import FaceDatabase
    
    # Create components
    face_db = FaceDatabase()
    enrollment = FaceEnrollment(face_db, VideoStream)
    
    try:
        # Run test
        enrollment.test_recognition()
        
        # Show recent events
        recent_events = face_db.get_recent_events(limit=5)
        print(f"\n📊 Recent recognition events: {len(recent_events)}")
        
        for i, event in enumerate(recent_events, 1):
            timestamp = event['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"   {i}. {event['name']} (confidence: {event['confidence']:.2f}) at {timestamp}")
        
    finally:
        face_db.close()