"""Module with fumctions to extract and process info from APK files."""

import re
import subprocess

def get_pkginfo(aapt, path):
    """Uses aapt to extract info from the APK at path; returns bytes, bytes."""
    
    (out, err) = subprocess.Popen("{0} d badging {1}".format(aapt, path), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True).communicate()
    
    return out, err
def get_pkgxml(aapt, path):
    """Uses aapt to extract info from the APK's AndroidManifest.xml; returns bytes, bytes."""
    
    (out, err) = subprocess.Popen("{0} d xmltree {1} AndroidManifest.xml".format(aapt, path), stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True).communicate()
    
    return out, err

def get_pkgname(pkginfo):
    """Extracts the APK label from pkginfo; returns string, string."""
    
    displayed_name = ""
    name = ""
    
    try:
        displayed_name = re.findall("application-label:\'(.*?)\'", pkginfo)[0]
        name = "".join(displayed_name.split()).replace("/", "")
    except:
        try:
            displayed_name = re.findall("application-label-en(-GB|-US):\'(.*?)\'", pkginfo)[0][1]
            name = "".join(displayed_name.split()).replace("/", "")
        except:
            try:
                displayed_name = re.findall("application: label=\'(.*?)\'", pkginfo)[0]
                name = "".join(displayed_name.split()).replace("/", "")
            except:
                displayed_name = re.findall("package: name=\'(.*?)\'", pkginfo)[0]
                name = displayed_name
    
    # If everything else fails, fall back to package name
    if not displayed_name:
        displayed_name = re.findall("package: name=\'(.*?)\'", pkginfo)[0]
        name = displayed_name
    
    return displayed_name, name

def get_pkgver(pkginfo):
    """Extracts the APK version from pkginfo; returns string."""
    
    try:
        pkgver = re.findall("versionName=\'(.*?)\'", pkginfo)[0]
        pkgver = "".join(pkgver.split()).replace("/", "")
    except:
        pkgver = "None"
    
    return pkgver
