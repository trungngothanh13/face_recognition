# Enhanced src/utils/config_loader.py
import json
import os

def load_config(config_path=None):
    """
    Load configuration from JSON file with validation
    
    Args:
        config_path: Path to config file (default: config/system_config.json)
        
    Returns:
        dict: Configuration dictionary
    """
    if config_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(base_dir, 'config', 'system_config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Validate required sections
    required_sections = ['video', 'motion_detection', 'face_detection', 'database']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")
    
    return config

def get_face_detection_config(config):
    """Get face detection specific configuration"""
    return config.get('face_detection', {})

def get_performance_config(config):
    """Get performance specific configuration"""
    return config.get('performance', {})

def get_logging_config(config):
    """Get logging specific configuration"""
    return config.get('logging', {})