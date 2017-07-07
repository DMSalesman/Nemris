"""Core of the Nemris tool, APK extractor."""

import argparse
import os

# Custom modules necessary for Nemris to work
from modules import apkutils
from modules import configutils
from modules import dirutils
from modules import pkgutils
from modules import utils

##########

# Path of the configuratipn file and default configuration dict
config_path = os.path.dirname(os.path.abspath(__file__)) + "/nemris_config.pkl"
config = {
"aapt": "",
"dir": "",
"substratum": None,
"md5sums": []
}

##########

# Commandline args handling
ap = argparse.ArgumentParser(description = "APK file extractor.")
apps = ap.add_mutually_exclusive_group(required = True)

apps.add_argument("-u", "--user", action = "store_true", help = "user apps")
apps.add_argument("-s", "--system", action = "store_true", help = "system apps")
apps.add_argument("-d", "--disabled", action = "store_true", help = "disabled apps")
apps.add_argument("-a", "--all", action = "store_true", help = "any app")

ap.add_argument("-r", "--reset", action = "store_true", required = False, help = "reset Nemris' configuration")
ap.add_argument("--keep-overlays", action = "store_true", required = False, help = "extract Substratum overlays")
ap.add_argument("--keep-arcus", action = "store_true", required = False, help = "extract theme variants compiled with Arcus")

args = ap.parse_args()

##########

if not args.user:
    if not args.all:
        if args.keep_overlays or args.keep_arcus:
            ap.error("one of the arguments  -u/--user -a/--all is required when using --keep-overlays or --keep-arcus")

print("************************")
print(" NEMRIS - APK extractor ")
print("       2017-07-07       ")
print(" by Death Mask Salesman ")
print("************************")

start_time = utils.get_current_time()    # store current time for computing elapsed time

if args.reset:
    print("[ I ] Resetting configuration...", end = " ", flush = True)
    
    if configutils.reset_config(config_path):
        print("done.\n")
    else:
        print("done.\n[ W ] The configuration was not present.\n")
else:
    if configutils.check_config(config_path):
        print("[ I ] Loading configuration...", end = " ", flush = True)
        
        config = configutils.load_config(config_path)
        
        print("done.\n")

# Checks for aapt and aopt (as fallback on Nougat)
if not config.get("aapt"):
    print("[ I ] Checking if either aapt or aopt is present.. ", end = " ", flush = True)
    
    aapt_aopt_exist = utils.check_aapt_aopt()
    
    print("done.\n")
    
    if aapt_aopt_exist[0]:
        config["aapt"] = "/system/bin/aapt"
    elif aapt_aopt_exist[1]:
        config["aapt"] = "/system/bin/aopt"
    elif aapt_aopt_exist[2]:
        config["aapt"] = "/data/data/com.termux/files/usr/bin/aapt"
    else:
        print("[ F ] Neither aapt nor aopt is installed. Aborting.")
        
        utils.save_exit(config, config_path, 1)

# Prompts user to set target dir
if not config.get("dir"): config["dir"] = dirutils.ask_dir()

(dir_exists, dir_has_apks) = dirutils.check_dir(config.get("dir"))

if not dir_exists:
    print("[ I ] Creating \"{0}\"...".format(config.get("dir")), end = " ", flush = True)
    
    dir_exists = dirutils.create_dir(config.get("dir"))
    
    print("done.\n")
    
    if not dir_exists:
        print("[ F ] Unable to create \"{0}\". Aborting.".format(config.get("dir")))
        
        utils.save_exit(config, config_path, 1)

# Creates a MD5 list to speed up subsequent executions
if not config.get("md5sums"):
    if dir_has_apks:
        print("\n[ I ] Generating MD5 checksums...", end = " ", flush = True)
        
        config["md5sums"] = dirutils.calculate_md5(config.get("dir"))
        
        print("done.\n")

# Creates an optimized APK/path dictionary to avoid the sluggish "pm path"
print("[ I ] Creating paths dictionary...", end = " ", flush = True)

pkgdict = pkgutils.create_pkgdict()

print("done.\n")

pkgs = pkgutils.list_installed_pkgs(args)

if not args.keep_overlays:
    if config.get("substratum") == None:
        config["substratum"] = pkgutils.check_substratum()
    
    if config.get("substratum"):
        print("[ I ] Excluding Substratum overlays...", end = " ", flush = True)
        
        pkgutils.exclude_overlays(config.get("aapt"), pkgdict, pkgs)
        
        print("done.\n")

if not args.keep_arcus and not config.get("substratum"):
    print("[ I ] Excluding Arcus theme variants...", end = " ", flush = True)
    
    pkgutils.exclude_arcus_variants(pkgs)
    
    print("done.\n")

extracted = 0
ignored = 0

# Extract APKs to the target directory and append MD5 checksums to MD5 list
for i in pkgs:
    pkgpath = pkgdict.get(i)
    
    (out, err) = apkutils.get_pkginfo(config.get("aapt"), pkgpath)    # filter stderr to avoid unneccessary gibberish by aapt
    pkginfo = out.decode("utf-8")
    
    (displayedname, name) = apkutils.get_pkgname(pkginfo)
    pkgver = apkutils.get_pkgver(pkginfo)
    (already_extracted, pkgsum) = pkgutils.check_already_extracted(pkgpath, config.get("md5sums"))
    
    if already_extracted:
        print("[ I ] {0}: ignored.".format(displayedname))
        
        ignored += 1
    else:
        print("[ I ] {0}: extracting...".format(displayedname), end = " ", flush = True)
        dest = "{0}/{1}_{2}.apk".format(config.get("dir"), name, pkgver)
        
        dirutils.extract(pkgpath, dest)
        
        config["md5sums"].append(pkgsum)
        extracted += 1
        
        print("done.")

elapsed_time = utils.get_current_time() - start_time

print("\n[ I ] Operations completed in {0:.0f} hours, {1:.0f} minutes and {2:.0f} seconds.".format(elapsed_time / 60 / 60, elapsed_time / 60 % 60, elapsed_time % 60))
print("[ I ] Extracted: {0} | Ignored: {1}".format(extracted, ignored))
print("[ I ] Goodbye!")

utils.save_exit(config, config_path, 0)
