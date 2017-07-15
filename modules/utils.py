"""Module with functions for internal use."""

import os
import subprocess
import time

import configutils    # needed to avoid importing pickle here

def save_exit(config, path, status):
    """Exits with the specified status after saving config to nemris_config.pkl; returns nothing."""
    
    configutils.dump_config(config, path)
    
    exit(status)

def check_nougat():
    """Check if the device falls into the Nougat API level range; returns bool."""
    
    (out, err) = subprocess.Popen("/system/bin/getprop ro.build.version.sdk", stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True).communicate()
    
    if err:
        supported = False
    else:
        api = int(out.decode("utf-8").rstrip("\n"))
        supported = True if api >= 24 and api <= 25 else False
    
    return supported

def sudo(cmd):
    """Executes a command cmd as root; returns bytes, bytes."""
    
    (out, err) = subprocess.Popen("/system/bin/su -c '{0}' && exit &".format(cmd), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True).communicate()
    
    if err:
        (out, err) = subprocess.Popen("/system/xbin/su -c '{0}' && exit &".format(cmd), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True).communicate()
    
    return out, err

def get_current_time():
    """Retrieves the current time; returns float."""
    
    return time.time()

def check_aapt_aopt():
    """Checks if aapt and aopt are present; returns tuple."""
    
    return tuple(i for i in [os.path.exists("/system/bin/aapt"), os.path.exists("/system/bin/aopt"), os.path.exists("/data/data/com.termux/files/usr/bin/aapt")])
