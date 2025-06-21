# src/ui/__init__.py
"""
User Interface module for Face Recognition System
Contains all GUI components and dialogs
"""

from .main_window import MainWindow
from .video_panel import VideoPanel
from .info_tabs import InfoTabs
from .dialogs import EmployeeDialog

__all__ = [
    'MainWindow',
    'VideoPanel', 
    'InfoTabs',
    'EmployeeDialog'
]