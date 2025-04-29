import os
import json
from datetime import datetime
from typing import Any, Dict

def ensure_log_dir(log_dir: str = "logs") -> str:
    """Ensure the log directory exists and return its path"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

def save_to_log(data: Dict[str, Any], prefix: str = "output", log_dir: str = "logs") -> str:
    """
    Save data to a JSON file in the log directory with timestamp
    
    Args:
        data: The data to save
        prefix: Prefix for the filename
        log_dir: Directory to save logs in
        
    Returns:
        Path to the saved file
    """
    # Ensure log directory exists
    log_dir = ensure_log_dir(log_dir)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.json"
    filepath = os.path.join(log_dir, filename)
    
    # Save data as JSON
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filepath 