"""Module with functions for internal use."""

import os
import subprocess
import time

import configutils    # needed to avoid importing pickle here

def save_exit(config, path, status):
    """Exits with the specified status after saving config to nemris_config.pkl; returns nothing."""
    
    configutils.dump_config(config, path)
    
    exit(status)

def sudo(cmd):
    """Executes a command cmd as root; returns bytes, bytes."""
    
    (out, err) = subprocess.Popen("/system/bin/su -c '{0}' && exit &".format(cmd), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True).communicate()
    return out, err

def get_current_time():
    """Retrieves the current time; returns float."""
    
    return time.time()

def check_aapt_aopt():
    """Checks if aapt and aopt are present; returns tuple."""
    
    return tuple(i for i in [os.path.exists("/system/bin/aapt"), os.path.exists("/system/bin/aopt")])
