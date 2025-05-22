# src/utils/config_loader.py
import json
import os

def load_config(config_path=None):
    """
    Load configuration from JSON file
    
    Args:
        config_path: Path to config file (default: config/system_config.json)
        
    Returns:
        dict: Configuration dictionary
    """
    if config_path is None:
        # Get the default path relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(base_dir, 'config', 'system_config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config

# Test code
if __name__ == "__main__":
    config = load_config()
    print("Configuration loaded successfully:")
    print(json.dumps(config, indent=4))