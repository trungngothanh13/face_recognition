# src/database/__init__.py
"""
Database module for Face Recognition System
Handles all database operations including employees, faces, and attendance
"""

from .database_manager import get_database_manager, close_database_manager
from .employee_database import EmployeeDatabase
from .face_database import FaceDatabase

__all__ = [
    'get_database_manager',
    'close_database_manager', 
    'EmployeeDatabase',
    'FaceDatabase'
]