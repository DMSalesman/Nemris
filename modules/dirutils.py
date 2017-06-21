"""Module with functions to perform operations on a target directory."""

import glob
import hashlib
import os
import shutil

import utils    # needed for sudo

def ask_dir():
    """Asks user for target directory; returns str."""
    
    dir = input("[ I ] Please input the directory where to extract the APKs.\n> ")
    
    return dir if not dir.endswith("/") else dir.rstrip("/")

def check_dir(dir):
    """Checks if a directory dir exists and has at least one APK file inside; returns bool, bool."""
    
    dir_exists = os.path.exists(dir)
    
    if dir_exists:
        dir_has_apks = True if glob.glob(dir + "/*.apk") else False
    else:
        dir_has_apks = False
    
    return dir_exists, dir_has_apks

def create_dir(dir):
    """Creates a directory dir, making use of root privileges if needed; returns bool."""
    
    dir_exists = True
    
    try:
        os.makedirs(dir)
    except:
        (out, err) = utils.sudo("mkdir {0}".format(dir))
        
        if err: dir_exists = False
    
    return dir_exists

def calculate_md5(dir):
    """Calculates the MD5 of all APK files in dir; returnas list."""
    
    files = glob.glob(dir + "/*.apk")
    md5sums = [hashlib.md5(open(i, "rb").read()).hexdigest() for i in files]
    
    return md5sums

def extract(pkgpath, dest):
    """Copies an APK file pkgpath to dest, resorting to root privileges if needed; returns nothing."""
    
    try:
        shutil.copyfile(pkgpath, dest)
    except:
        sudo("cp {0} {1}".format(pkgpath, dest))
