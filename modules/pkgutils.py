"""Module with functions for management of installed APK lists."""

import glob
import hashlib
import re
import subprocess

import apkutils    # needed for AndroidManifest.xml dump
import utils    # needed for sudo

# Creates a APK/path dictionary to avoid the sluggish "pm path"
def create_pkgdict():
    """Creates a dict for fast path lookup from /data/system/packages.xml; returns dict."""
    
    (out, err) = utils.sudo("cat /data/system/packages.xml")
    
    if err: return False
    
    xml_dump = [i for i in out.decode("utf-8").split("\n") if "<package name=" in i]
    pkgdict = {}
    
    for i in xml_dump:
        pkgname = re.findall("<package name=\"(.*?)\"", i)[0]
        pkgpath = re.findall("codePath=\"(.*?)\"", i)[0]
        
        # Normalizes each entry
        if not pkgpath.endswith(".apk"):
            try:
                pkgpath = glob.glob(pkgpath + "/*.apk")[0]
            except:
                continue
        
        pkgdict[pkgname] = pkgpath
    
    return pkgdict

def list_installed_pkgs(args):
    """Lists the members of a given category of packages; returns list."""
    
    prefix = "pm list packages"
    
    if args.user:
        suffix = "-3"
    elif args.system:
        suffix = "-s"
    elif args.disabled:
        suffix = "-d"
    else:
        suffix = ""
    
    pkgs = [i[8:] for i in subprocess.Popen("{0} {1}".format(prefix, suffix), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True).communicate()[0].decode("utf-8").split("\n") if i]
    
    return pkgs

def check_masquerade():
    """Checks if the Masquerade component of the Substratum engine is installed; returns bool."""
    
    system_pkgs = [i[8:] for i in subprocess.Popen("pm list packages -s", stdout = subprocess.PIPE, shell = True).communicate()[0].decode("utf-8").split("\n") if i]
    substratum_installed = True if "masquerade.substratum" in system_pkgs else False
    
    return substratum_installed

def exclude_overlays(aapt, pkgdict, pkgs):
    """Excludes Substratum overlays from the packages to extract; returns nothing."""
    
    for i in pkgs:
        pkgpath = pkgdict.get(i)
        out = apkutils.get_pkgxml(pkgpath)[0].decode("utf-8")
        
        if "Substratum_Parent" in out: pkgs.remove(i)

def exclude_arcus_variants(pkgs):
    """Excludes Arcus theme variants from the packages to extract; returns nothing."""
    
    for i in pkgs:
        if "pixkart.arcus.user" in i: pkgs.remove(i)

def check_already_extracted(pkgpath, md5sums):
    """Checks if an APK has already been extracted; returns bool, str."""
    
    pkgsum = hashlib.md5(open(pkgpath, "rb").read()).hexdigest()
    already_extracted = True if pkgsum in md5sums else False
    
    return already_extracted, pkgsum
