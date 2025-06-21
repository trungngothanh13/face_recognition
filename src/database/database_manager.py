# src/database/database_manager.py
"""
Database connection and management utilities
Centralizes database configuration and connection handling
"""
import pymongo
from pymongo import MongoClient
from datetime import datetime
import os
import json

class DatabaseManager:
    """Centralized database connection manager"""
    
    def __init__(self, connection_string="mongodb://localhost:27017/", database_name="face_recognition_db"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ismaster')
            print(f"✅ Connected to MongoDB: {self.database_name}")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def get_collection(self, collection_name):
        """Get a collection from the database"""
        if self.db is None:
            self._connect()
        return self.db[collection_name]
    
    def create_indexes(self, collection_name, indexes):
        """Create indexes for a collection"""
        collection = self.get_collection(collection_name)
        for index_spec in indexes:
            try:
                collection.create_index(**index_spec)
            except Exception as e:
                print(f"⚠️ Index creation warning for {collection_name}: {e}")
    
    def test_connection(self):
        """Test database connection"""
        try:
            if self.client is not None:
                self.client.admin.command('ismaster')
                return True
            return False
        except Exception:
            return False
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            if self.db is None:
                return {}
                
            stats = self.db.command("dbstats")
            collections = self.db.list_collection_names()
            
            collection_stats = {}
            for coll_name in collections:
                coll = self.get_collection(coll_name)
                collection_stats[coll_name] = coll.count_documents({})
            
            return {
                "database_name": self.database_name,
                "collections": collection_stats,
                "total_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0)
            }
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            print("📴 Database connection closed")

class DatabaseConfig:
    """Database configuration loader"""
    
    @staticmethod
    def load_from_config():
        """Load database configuration from config file"""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config', 'system_config.json'
            )
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            db_config = config.get('database', {})
            return {
                'connection_string': db_config.get('mongodb_uri', 'mongodb://localhost:27017/'),
                'database_name': db_config.get('database_name', 'face_recognition_db')
            }
        except Exception as e:
            print(f"⚠️ Could not load database config: {e}")
            return {
                'connection_string': 'mongodb://localhost:27017/',
                'database_name': 'face_recognition_db'
            }

# Singleton database manager instance
_db_manager = None

def get_database_manager():
    """Get the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        config = DatabaseConfig.load_from_config()
        _db_manager = DatabaseManager(
            connection_string=config['connection_string'],
            database_name=config['database_name']
        )
    return _db_manager

def close_database_manager():
    """Close the global database manager"""
    global _db_manager
    if _db_manager is not None:
        _db_manager.close()
        _db_manager = None