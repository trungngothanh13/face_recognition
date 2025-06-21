# src/processing/__init__.py
"""
Processing module for Face Recognition System
Contains video processing, face detection, and motion detection
"""

from .video_stream import VideoStream
from .motion_detector import MotionDetector
from .face_processor import ImprovedFaceProcessor

# Keep existing imports for backward compatibility
try:
    from .face_enrollment import FaceEnrollment, quick_enroll, quick_test
    from .integrated_system import IntegratedSystem, quick_integrated_system
    
    __all__ = [
        'VideoStream',
        'MotionDetector',
        'ImprovedFaceProcessor',
        'FaceEnrollment',
        'quick_enroll',
        'quick_test',
        'IntegratedSystem', 
        'quick_integrated_system'
    ]
except ImportError:
    # If some modules are not available
    __all__ = [
        'VideoStream',
        'MotionDetector', 
        'ImprovedFaceProcessor'
    ]