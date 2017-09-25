"""Module with functions to perform operations on a target directory."""

import glob
import os
import re
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
    """Calculates the MD5 of all APK files in dir; returns list."""
    
    files = glob.glob(dir + "/*.apk")
    md5sums = [utils.compute_md5sum(i) for i in files]
    
    return md5sums

def handle_duplicate_names(dest):
    """Adjusts the dest of APKs with the same pkgname; returns str."""
    
    if os.path.isfile(dest):
        prefix = os.path.dirname(dest)
        suffix = os.path.basename(dest).rstrip(".apk")
        
        c = re.findall("-([\d].*?)$", suffix)
        
        if not c:
            c = 1
        else:
            suffix = suffix[: -len(c[0])]
        
        while True:
            dest = "{0}/{1}-{2}.apk".format(prefix, suffix, c)
            
            c += 1
            
            if not os.path.isfile(dest): break
    
    return dest

def extract(pkgpath, dest):
    """Copies an APK file pkgpath to dest, resorting to root privileges if needed; returns nothing."""
    
    dest = handle_duplicate_names(dest)
    
    try:
        shutil.copyfile(pkgpath, dest)
    except:
        utils.sudo("cp {0} {1}".format(pkgpath, dest))
        utils.sudo("chmod 660 {0}".format(dest))
        utils.sudo("chown media_rw.media_rw {0}".format(dest))
