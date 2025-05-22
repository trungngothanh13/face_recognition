# src/data/database.py
from pymongo import MongoClient

def get_database():
    """
    Connect to MongoDB and return the database object
    """
    # Connection string - update with your MongoDB details if needed
    connection_string = "mongodb://localhost:27017/"
    
    # Create a connection using MongoClient
    client = MongoClient(connection_string)
    
    # Create or get the database
    db = client['face_recognition_db']
    
    return db

def test_connection():
    """
    Test the MongoDB connection
    """
    try:
        db = get_database()
        # Check connection by listing collections
        collections = db.list_collection_names()
        print(f"Successfully connected to MongoDB. Collections: {collections}")
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False

if __name__ == "__main__":
    test_connection()