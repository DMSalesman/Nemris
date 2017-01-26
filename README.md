## Purpose

Nemris is a Python (3.5+) tool to be ran on Android devices, whose goal is to save the APK files of any installed apps in a folder of your choice, for future use.

**Root privileges are needed in order to run Nemris. Not compatible with systemless root.**

-----

## Strengths

* Creation and maintenance of a folder containing APK files without worrying about exact duplicates, thanks to MD5 checks;
* Awareness of the popular Substratum Theme Engine overlays and Arcus theme variants, which Nemris automatically skips;
* Discrimination between user, system and disabled apps;
* Compatibility with both **aapt** and **aopt**, needed to retrieve app banes and versions;
* Fast retrieval of APK paths, thanks to the **packages.xml** file, which needs root permissions to be read;
* Caching of certain checks, to avoid calculating them unnecessarily more than once.

-----

## Weaknesses

* Older APK files in the chosen directory aren't automatically deleted, leaving that to the user;
* No fancy handling of most errors. If Nemris fails, you'll see it loud and clear.

-----

## Usage

Nemris requires one mandatory argument and supports three optional arguments as well. You'll be able to see a short usage message by means of:

    python nemris.py -h

Such an input will yield you:

    usage: nemris.py [-h] (-u | -s | -d | -a) [-r] [--keep-substratum] [--keep-arcus]
    
    APK file extractor.
    
    optional arguments:
      -h, --help         show this help message and exit
      -u, --user         user apps
      -s, --system       system apps
      -d, --disabled     disabled apps
      -a, --all          any app
      -r, --reset        reset Nemris configuration
      --keep-substratum  extract Substratum overlays
      --keep-arcus       extract Arcus theme variants

-----

## Command-line arguments

### App typology

The arguments `-u`, `-s`, `-d` and `-a` identify the typology of apps to extract. Only one of them may be specified.

`-u/--user`: apps installed by the user, either from the Play Store or sideloaded, and residing inside **/data/app**;

`-s/--system`: apps included inside the Android distribution, usually residing inside **/system/app**, **/system/priv-app** and **/system/framework**;

`-d/--disabled`: apps frozen either via `pm disable` or via some application. Apps under this category might be both user and system apps;

`-a/--all`: any application on the device, from all of the above categories.

### Configuration reset

By design, to reduce the elapsed time in subsequent launches, Nemris will cache the results of certain checks and calculations, saving them inside a file called **nemris_config.pkl** in the same directory as the main script.

By specifying the `-r/--reset` argument, you'll be able to delete this file, thus making Nemris behave as in its first launch.

### Substratum overlays and Arcus variants

Since you need to have a theme installed in order to use any overlays/variants, Nemris saves time and storage by ignoring them during the extraction phase. Should you need to extract them nonetheless, you can make use of the arguments below.

`--keep-substratum`: extract any installed Substratum overlay;

`--keep-arcus`: extract theme variants compiled by Arcus.

You can also use both arguments at the same time, but **you'll be able to use them only in combination with either the `-u/--user` or the `-a/--all` arguments**.
