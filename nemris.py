import argparse
import glob
import hashlib
import os
import pickle
import re
import shutil
import subprocess
import time

##########
# Dictionary for reusable settings and time-saver precomputations
# Custom exit functions

_config_file_path = os.path.dirname(os.path.abspath(__file__)) + "/nemris_config.pkl"
_nemris_config = {
"aapt": "",
"backup_dir": "",
"overlays_installed": None,
"arcus_installed": None,
"md5_dict": []
}

def save_exit_ok(nemris_config, config_file_path):
    with open(config_file_path, "wb") as file:
        pickle.dump(nemris_config, file)
    
    exit(0)

def save_exit_fatal(nemris_config, config_file_path):
    with open(config_file_path, "wb") as file:
        pickle.dump(nemris_config, file)
    
    exit(1)

##########

# Greets and starts elapsed time calculations
# Returns float
def welcome():
    start_time = time.time()
    
    print("************************")
    print(" NEMRIS - APK extractor ")
    print("       2017-01-27       ")
    print(" by Death Mask Salesman ")
    print("************************")
    
    return start_time

# Resets Nemris configuration if the -r argument is provided
def reset_config(config_file_path):
    print("\n[ INFO ] Resetting Nemris configuration...", end = " ")
    
    try:
        os.unlink(config_file_path)
        print("done.")
    except FileNotFoundError:
        print("done.\n[ WARN ] The configuration file was not present.")

# Checks for the existence of the configuration file
# Returns boolean
def check_config(config_file_path):
    return os.path.exists(config_file_path)

# Loads the precomputed configuration
# Returns dictionary
def load_config(config_file_path):
    print("\n[ INFO ] Loading Nemris configuration...", end = " ")
    
    with open(config_file_path, "rb") as file:
        nemris_config = pickle.load(file)
    
    print("done.")
    
    return nemris_config

# Checks if aapt is present
# Returns boolean
def check_aapt():
    print("\n[ INFO ] Checking if aapt is present...", end = " ")
    
    aapt_exists = os.path.exists("/system/bin/aapt")
    
    print("done.")
    
    return aapt_exists

# Checks if aopt is present (support for Android Nougat)
# Returns boolean
def check_aopt():
    print("\n[ INFO ] Checking if aopt is present...", end = " ")
    
    aopt_exists = os.path.exists("/system/bin/aopt")
    
    print("done.")
    
    return aopt_exists

# Asks the user for the path where to place the extracted APKs
# Trims trailing slashes
# Returns string
def ask_for_backup_dir():
    print("\n[ INFO ] Please input the folder where to extract the APKs.")
    
    backup_dir = input("> ")
    if backup_dir.endswith("/"):
        backup_dir = backup_dir.rstrip("/")
    
    return backup_dir

# Checks if the backup directory exists and if it has at least one APK inside
# Returns boolean, boolean
def check_backup_dir(backup_dir):
    print("\n[ INFO ] Checking if the backup directory already exists...", end = " ")
    
    backup_dir_exists = os.path.exists(backup_dir)
    backup_dir_has_apks = False
    
    if backup_dir_exists:
        if glob.glob(backup_dir + "/*.apk"):
            backup_dir_has_apks = True
    
    print("done.")
    
    return backup_dir_exists, backup_dir_has_apks

# Creates the backup directory
# Returns boolean
def create_backup_dir(backup_dir):
    print("\n[ INFO ] Creating the backup directory...", end = " ")
    
    backup_dir_exists = True
    
    try:
        os.makedirs(backup_dir)
    except:
        try:
            subprocess.Popen("/system/bin/su -c 'mkdir " + backup_dir + "' && exit &", shell = True)
        except:
            backup_dir_exists = False
    
    print("done")
    
    return backup_dir_exists

# Generates the MD5 checksums of any APK file in the backup directory
# Returns list
def create_md5sums(backup_dir):
    print("\n[ INFO ] Generating MD5 checksums...", end = " ")
    
    apk_files = glob.glob(backup_dir + "/*.apk")
    md5_dict = [hashlib.md5(open(i, "rb").read()).hexdigest() for i in apk_files]
    
    print("done.")
    
    return md5_dict

# Reads the packages.xml with root privileges to build packages' paths
# Returns dictionary
def parse_packages_xml():
    print("\n[ INFO ] Generating optimized dictionary...", end = " ")
    
    raw_dump = subprocess.Popen("/system/bin/su -c 'cat /data/system/packages.xml' && exit &", stdout = subprocess.PIPE, shell = True).communicate()[0].decode("ascii").split("\n")
    refined_dump = [i for i in raw_dump if "<package name=" in i]
    
    optimized_dict = {}
    
    for i in refined_dump:
        package_name = re.findall("<package name=\"(.*?)\"", i)[0]
        package_path = re.findall("codePath=\"(.*?)\"", i)[0]
        
        if not package_path.endswith(".apk"):
            package_path = glob.glob(package_path + "/*.apk")[0]
        
        optimized_dict[package_name] = package_path
    
    print("done.")
    
    return optimized_dict

# Gets list of installed packages based on the user-supplied argument
# Returns list
def get_installed_packages(args):
    prefix = "pm list packages"
    
    if args.user:
        print("\n[ INFO ] Retrieving user apps...", end = " ")
        cmd = prefix + " -3"
    elif args.system:
        print("\n[ INFO ] Retrieving system apps...", end = " ")
        cmd = prefix + " -s"
    elif args.disabled:
        print("\n[ INFO ] Retrieving disabled apps...", end = " ")
        cmd = prefix + " -d"
    elif args.all:
        print("\n[ INFO ] Retrieving apps...", end = " ")
        cmd = prefix
    
    installed_packages = [i[8:] for i in subprocess.Popen(cmd, stdout = subprocess.PIPE, shell = True).communicate()[0].decode("ascii").split("\n") if i]
    
    print("done.")
    
    return installed_packages

# Checks for Substratum's Masquerade subsystem
# Returns boolean
def check_for_overlays():
    print("\n[ INFO ] Checking if the Masquerade overlay engine is installed...", end = " ")
    
    overlays_installed = True
    system_packages = [i[8:] for i in subprocess.Popen("pm list packages -s", stdout = subprocess.PIPE, shell = True).communicate()[0].decode("ascii").split("\n") if i]
    
    if not "masquerade.substratum" in system_packages:
        overlays_installed = False
    
    print("done.")
    
    return overlays_installed
    
# Excludes Substratum-made overlays from the apps to backup
# Returns list
def purge_overlays(aapt, optimized_dict, installed_packages):
    print("\n[ INFO ] Excluding overlays...", end = " ")
    
    purged_packages = []
    
    for i in installed_packages:
        package_path = optimized_dict.get(i)
        manifest = subprocess.Popen(aapt + " d xmltree " + package_path + " AndroidManifest.xml", stdout = subprocess.PIPE, shell = True).communicate()[0].decode("utf-8")
        
        if not "Substratum_Parent" in manifest:
            purged_packages.append(i)
    
    print("done.")
    
    return purged_packages

# Checks if Arcus has been installed
# Returns boolean
def check_for_arcus():
    print("\n[ INFO ] Checking if Arcus is present...", end = " ")
    
    arcus_installed = True
    user_packages = [i[8:] for i in subprocess.Popen(" pm list packages -3", stdout = subprocess.PIPE, shell = True).communicate()[0].decode("ascii").split("\n") if i]
    
    if not "pixkart.arcus" in user_packages:
        arcus_installed = False
    
    print("done.")
    
    return arcus_installed

# Excludes themes compiled by Arcus from the apps to backup
# Returns list
def purge_arcus_variants(installed_packages):
    print("\n[ INFO ] Excluding Arcus variants...", end = " ")
    
    purged_packages = [i for i in installed_packages if not "pixkart.arcus.user" in i]
    
    print("done.")
    
    return purged_packages

# Checks if an APK is already present in the backup directory
# Returns boolean, string
def check_already_extracted(package_path, md5_dict):
    md5 = hashlib.md5(open(package_path, "rb").read()).hexdigest()
    already_extracted = False
    
    if md5 in md5_dict:
        already_extracted = True
    
    return already_extracted, md5

# Gets a full dump of the package's info
# Returns tuple
def get_package_info(aapt, package_path):
    return subprocess.Popen(aapt + " d badging " + package_path, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True).communicate()

# Gets application name from dumped app info. Falls back to package name if no application name
# Elaborates a package_name for file naming (trims spaces and slashes) and a displayed_name for graceful output
# Returns string, string
def get_package_name(package_info):
    displayed_name = ""
    package_name = ""
    
    try:
        displayed_name = re.findall("application-label:\'(.*?)\'", package_info)[0]
        package_name = "".join(displayed_name.split()).replace("/", "")
    except:
        try:
            displayed_name = re.findall("application-label-en(-GB|-US):\'(.*?)\'", package_info)[0][1]
            package_name = "".join(displayed_name.split()).replace("/", "")
        except:
            try:
                displayed_name = re.findall("application: label=\'(.*?)\'", package_info)[0]
                package_name = "".join(displayed_name.split()).replace("/", "")
            except:
                displayed_name = re.findall("package: name=\'(.*?)\'", package_info)[0]
                package_name = displayed_name
    
    if not displayed_name:
        displayed_name = re.findall("package: name=\'(.*?)\'", package_info)[0]
        package_name = displayed_name
    
    return displayed_name, package_name

# Gets application version from dumped app info. Falls back to "None" if no app version
# package_version has trimmed slashes and spaces
# Returns string
def get_package_version(package_info):
    try:
        package_version = re.findall("versionName=\'(.*?)\'", package_info)[0]
        package_version = "".join(package_version.split()).replace("/", "")
    except:
        package_version = "None"
    
    return package_version

# Launches a series of function to see if the APK has already been extracted and to get app name and version
# If the APK needs to be extracted, its MD5 gets appended to the already present MD5 list
# Returns list
def extract_apk(aapt, package_name, package_path, backup_dir, md5_dict):
    (package_info, err) = get_package_info(aapt, package_path)
    package_info = package_info.decode("utf-8")
    
    (displayed_name, package_name) = get_package_name(package_info)
    package_version = get_package_version(package_info)
    (already_extracted, md5) = check_already_extracted(package_path, md5_dict)
    
    if already_extracted:
        print("[ INFO ] %s has already been backed up." %displayed_name)
    else:
        print("[ INFO ] Backing up %s..." %displayed_name, end = " ")
        
        try:
            shutil.copyfile(package_path, backup_dir + "/" + package_name + "_" + package_version + ".apk")
        except:
            subprocess.Popen("/system/bin/su -c 'cp " + package_path + " " + backup_dir + "/" + package_name + "_" + package_version + ".apk' && exit &", shell = True)
        
        md5_dict.append(md5)
        
        print("done.")
    
    return md5_dict

# Communicates elapsed time and politely says goodbye
def goodbye(start_time):
    elapsed_time = time.time() - start_time
    
    print("\n[ INFO ] Operations completed in %.0f hours, %.0f minutes and %.0f seconds." %(elapsed_time / 60 / 60, elapsed_time / 60 % 60, elapsed_time % 60))
    print("[ INFO ] Goodbye!")

##########
# Command-line arguments definition and parsing
_ap = argparse.ArgumentParser(description = "APK file extractor.")
_apps = _ap.add_mutually_exclusive_group(required = True)

_apps.add_argument("-u", "--user", action = "store_true", help = "user apps")
_apps.add_argument("-s", "--system", action = "store_true", help = "system apps")
_apps.add_argument("-d", "--disabled", action = "store_true", help = "disabled apps")
_apps.add_argument("-a", "--all", action = "store_true", help = "any app")

_ap.add_argument("-r", "--reset", action = "store_true", required = False, help = "reset Nemris configuration")
_ap.add_argument("--keep-substratum", action = "store_true", required = False, help = "extract Substratum overlays")
_ap.add_argument("--keep-arcus", action = "store_true", required = False, help = "extract Arcus theme variants")

_args = _ap.parse_args()

# Only allow Substratum overlays / Arcus variants to be extracted when either user or all apps are to be extracted
if (_args.keep_substratum and not _args.user) and (_args.keep_substratum and not _args.all):
    _ap.error("one of the arguments  -u/--user -a/--all is required when using --keep-substratum")
elif (_args.keep_arcus and not _args.user) and (_args.keep_arcus and not _args.all):
    _ap.error("one of the arguments -u/--user -a/--all is required when using --keep-arcus")

##########
# "Main" part of the script. Launches everything else
_start_time = welcome()

# Resets the configuration if "-r" is provided
if _args.reset:
    reset_config(_config_file_path)
else:
    if check_config(_config_file_path):
        _nemris_config = load_config(_config_file_path)

# Checks for aapt/aopt if not checked beforehand. Handles aapt aliasing
if not _nemris_config.get("aapt"):
    _aapt_exists = check_aapt()
    
    if not _aapt_exists:
        print("[ WARN ] aapt not found.")
        _aopt_exists = check_aopt()
        
        if not _aopt_exists:
            print("[ FATAL ] aopt not found. Aborting.")
            save_exit_error(_nemris_config, _config_file_path)
        
        _nemris_config["aapt"] = "/system/bin/aopt" 
    else:
        _nemris_config["aapt"] = "/system/bin/aapt"

# Memorizes user-supplied backup directory if not specified beforehand
if not _nemris_config.get("backup_dir"):
    _nemris_config["backup_dir"] = ask_for_backup_dir()

(_backup_dir_exists, _backup_dir_has_apks) = check_backup_dir(_nemris_config.get("backup_dir"))

# Handles creation of the backup directory and eventual failure
if not _backup_dir_exists:
    _backup_dir_exists = create_backup_dir(_nemris_config.get("backup_dir"))
    
    if not _backup_dir_exists:
        print("[ FATAL ] Failed to create backup directory. Aborting.")
        save_exit_fatal(_nemris_config, _config_file_path)

# Calculates MD5 hashes if not already present
if _backup_dir_has_apks:
    if not _nemris_config.get("md5_dict"):
        _nemris_config["md5_dict"] = create_md5sums(_nemris_config.get("backup_dir"))

_optimized_dict = parse_packages_xml()

_installed_packages = get_installed_packages(_args)

# Determines whether to ignore Substratum overlays
if not _args.keep_substratum:
    if _nemris_config.get("overlays_installed") == None:
        _nemris_config["overlays_installed"] = check_for_overlays()

    if _nemris_config.get("overlays_installed"):
        _purged_packages = purge_overlays(_nemris_config.get("aapt"), _optimized_dict, _installed_packages)
    else:
        _purged_packages = _installed_packages
else:
    _purged_packages = _installed_packages

# Determines when to ignore Arcus variants
if not _args.keep_arcus:
    if _nemris_config.get("arcus_installed") == None:
        _nemris_config["arcus_installed"] = check_for_arcus()
    
    if _nemris_config.get("arcus_installed"):
        purged_packages = purge_arcus_variants(_purged_packages)
    
    print()
else:
    print()

for _i in _purged_packages:
    _nemris_config["md5_dict"] = extract_apk(_nemris_config.get("aapt"), _i, _optimized_dict.get(_i), _nemris_config.get("backup_dir"), _nemris_config.get("md5_dict"))

goodbye(_start_time)

##########
# Saves the configuration and ends
save_exit_ok(_nemris_config, _config_file_path)