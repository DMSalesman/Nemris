"""Module with functions to operate on the script's configuration."""

import os
import pickle

def reset_config(path):
    """Deletes the file at path; returns bool."""
    
    status = True
    
    try:
        os.unlink(path)
    except FileNotFoundError:
        status = False
    
    return status

def check_config(path):
    """Checks if the file at path exists; returns bool."""
    
    return os.path.exists(path)

def dump_config(config, path):
    """Dumps the config dict to a file at path; returns nothing."""
    
    with open(path, "wb") as f:
        pickle.dump(config, f)

def load_config(path):
    """Loads the config dict from a file at path; returns dict."""
    
    with open(path, "rb") as f:
        config = pickle.load(f)
    
    return config
