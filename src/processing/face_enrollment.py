# src/processing/face_enrollment.py
import cv2
import numpy as np
import time
from datetime import datetime
import face_recognition

class FaceEnrollment:
    """Handle face enrollment process"""
    
    def __init__(self, face_database, video_stream_class):
        self.face_db = face_database
        self.video_stream_class = video_stream_class
    
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
        print(f"Starting face enrollment for: {person_name}")
        print(f"Will capture {num_samples} samples with {sample_delay}s delay between each")
        print("Press 'q' to quit early")
        print("\n⏰ Starting...")
        
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
                face_locations, face_encodings, processed_frame = self.detect_and_encode_faces(frame)
                
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