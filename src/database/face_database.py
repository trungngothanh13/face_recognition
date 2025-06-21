# src/database/face_database.py
"""
Face database operations
Handles face encodings storage and recognition events
"""
import numpy as np
from datetime import datetime
import pickle

from .database_manager import get_database_manager

class FaceDatabase:
    """Face database operations"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        
        # Get collections
        self.faces_collection = self.db_manager.get_collection("faces")
        self.events_collection = self.db_manager.get_collection("recognition_events")
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes"""
        face_indexes = [
            {"keys": "name"},
            {"keys": "employee_id", "sparse": True}
        ]
        
        event_indexes = [
            {"keys": "timestamp"},
            {"keys": "name"}
        ]
        
        self.db_manager.create_indexes("faces", face_indexes)
        self.db_manager.create_indexes("recognition_events", event_indexes)
    
    def add_face(self, name, face_encoding, additional_info=None):
        """Add a face to the database"""
        face_doc = {
            "name": name,
            "encoding": face_encoding.tolist(),  # Convert numpy array to list
            "created_at": datetime.now()
        }
        
        # Add additional info if provided
        if additional_info and isinstance(additional_info, dict):
            face_doc.update(additional_info)
        
        result = self.faces_collection.insert_one(face_doc)
        return result.inserted_id
    
    def get_all_faces(self):
        """Get all faces from the database"""
        faces = []
        
        for face_doc in self.faces_collection.find():
            encoding = np.array(face_doc["encoding"])
            name = face_doc["name"]
            faces.append((name, encoding))
        
        return faces
    
    def get_faces_by_name(self, name):
        """Get all faces for a given name"""
        faces = []
        
        for face_doc in self.faces_collection.find({"name": name}):
            face_id = face_doc["_id"]
            encoding = np.array(face_doc["encoding"])
            faces.append((face_id, encoding))
        
        return faces
    
    def record_recognition_event(self, name, confidence, frame_path=None, location=None):
        """Record a face recognition event"""
        event_doc = {
            "name": name,
            "confidence": float(confidence),
            "timestamp": datetime.now()
        }
        
        # Add optional fields
        if frame_path:
            event_doc["frame_path"] = frame_path
        
        if location:
            event_doc["location"] = {
                "top": int(location[0]),
                "right": int(location[1]),
                "bottom": int(location[2]),
                "left": int(location[3])
            }
        
        result = self.events_collection.insert_one(event_doc)
        return result.inserted_id
    
    def get_recent_events(self, limit=100):
        """Get recent recognition events"""
        import pymongo
        events = list(self.events_collection.find().sort("timestamp", pymongo.DESCENDING).limit(limit))
        return events
    
    def export_face_encodings(self, output_path):
        """Export face encodings to a pickle file"""
        try:
            faces = self.get_all_faces()
            
            # Split into names and encodings
            names = [face[0] for face in faces]
            encodings = [face[1] for face in faces]
            
            # Create data dictionary
            data = {
                "names": names,
                "encodings": encodings,
                "exported_at": datetime.now()
            }
            
            # Save to pickle file
            with open(output_path, 'wb') as f:
                pickle.dump(data, f)
            
            return True
        
        except Exception as e:
            print(f"Error exporting face encodings: {e}")
            return False
    
    def import_face_encodings(self, input_path, replace=False):
        """Import face encodings from a pickle file"""
        try:
            # Load data from pickle file
            with open(input_path, 'rb') as f:
                data = pickle.load(f)
            
            # Check data format
            if not all(key in data for key in ["names", "encodings"]):
                raise ValueError("Invalid data format in pickle file")
            
            # Clear existing faces if replace is True
            if replace:
                self.faces_collection.delete_many({})
            
            # Import faces
            count = 0
            for name, encoding in zip(data["names"], data["encodings"]):
                self.add_face(name, encoding)
                count += 1
            
            return count
        
        except Exception as e:
            print(f"Error importing face encodings: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        # Database manager handles connection closure
        pass