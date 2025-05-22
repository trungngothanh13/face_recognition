import pymongo
from pymongo import MongoClient
import numpy as np
from datetime import datetime
import os
import pickle

class FaceDatabase:
    def __init__(self, connection_string="mongodb://localhost:27017/", database_name="face_recognition_db"):
        """
        Initialize the face database connection
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.faces_collection = self.db["faces"]
        self.events_collection = self.db["recognition_events"]
        
        # Create indexes if they don't exist
        self.faces_collection.create_index("name")
        self.events_collection.create_index("timestamp")
    
    def add_face(self, name, face_encoding, additional_info=None):
        """
        Add a face to the database
        
        Args:
            name: Person's name
            face_encoding: numpy array of face encoding
            additional_info: Any additional information (dict)
            
        Returns:
            face_id: ID of the inserted face
        """
        # Create face document
        face_doc = {
            "name": name,
            "encoding": face_encoding.tolist(),  # Convert numpy array to list
            "created_at": datetime.now()
        }
        
        # Add additional info if provided
        if additional_info and isinstance(additional_info, dict):
            face_doc.update(additional_info)
        
        # Insert into database
        result = self.faces_collection.insert_one(face_doc)
        
        return result.inserted_id
    
    def get_all_faces(self):
        """
        Get all faces from the database
        
        Returns:
            faces: List of tuples (name, encoding)
        """
        faces = []
        
        for face_doc in self.faces_collection.find():
            # Convert list back to numpy array
            encoding = np.array(face_doc["encoding"])
            name = face_doc["name"]
            faces.append((name, encoding))
        
        return faces
    
    def get_faces_by_name(self, name):
        """
        Get all faces for a given name
        
        Args:
            name: Person's name
            
        Returns:
            faces: List of tuples (face_id, encoding)
        """
        faces = []
        
        for face_doc in self.faces_collection.find({"name": name}):
            face_id = face_doc["_id"]
            encoding = np.array(face_doc["encoding"])
            faces.append((face_id, encoding))
        
        return faces
    
    def record_recognition_event(self, name, confidence, frame_path=None, location=None):
        """
        Record a face recognition event
        
        Args:
            name: Recognized person's name
            confidence: Recognition confidence
            frame_path: Path to saved frame image (optional)
            location: Face location in the frame (optional)
            
        Returns:
            event_id: ID of the inserted event
        """
        # Create event document
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
        
        # Insert into database
        result = self.events_collection.insert_one(event_doc)
        
        return result.inserted_id
    
    def get_recent_events(self, limit=100):
        """
        Get recent recognition events
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            events: List of events
        """
        events = list(self.events_collection.find().sort("timestamp", pymongo.DESCENDING).limit(limit))
        return events
    
    def export_face_encodings(self, output_path):
        """
        Export face encodings to a pickle file
        
        Args:
            output_path: Path to save the pickle file
            
        Returns:
            success: True if export successful
        """
        try:
            # Get all faces
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
        """
        Import face encodings from a pickle file
        
        Args:
            input_path: Path to the pickle file
            replace: If True, remove existing faces first
            
        Returns:
            count: Number of faces imported
        """
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
        """
        Close the database connection
        """
        if self.client:
            self.client.close()


# Test function
if __name__ == "__main__":
    # Create database connection
    db = FaceDatabase()
    
    # Print counts
    face_count = db.faces_collection.count_documents({})
    event_count = db.events_collection.count_documents({})
    
    print(f"Connected to MongoDB. Found {face_count} faces and {event_count} recognition events.")
    
    # Close connection
    db.close()