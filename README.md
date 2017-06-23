## Purpose

Nemris is a Python (3.5+) tool to be ran on Android devices, whose goal is to save the APK files of any installed apps in a folder of your choice, for future use.
-----

## Requirements

To run, Nemris requires:

* root privileges (to read `/data/system/packages.xml` and to forcefully copy to the destination directory if problems arise);
* `aapt` or `aopt` placed at `/system/bin`;
* Python 3.5 or greater.

-----

## Strengths

* Creation and maintenance of a folder containing APK files without worrying about exact duplicates, thanks to MD5 checks;
* Extraction of APKs whose name is the same;
* Awareness of the popular Substratum Theme Engine overlays and Arcus theme variants, which Nemris automatically skips;
* Discrimination between user, system and disabled apps;
* Fast retrieval of APK paths, thanks to the `/data/system/packages.xml` file;
* Caching of certain checks, to avoid calculating them unnecessarily more than once.

-----

## Weaknesses

* Older APK files in the chosen directory aren't automatically deleted, leaving that to the user;
* Nemris' configuration file (`nemris_config.pkl`) is never deleted without user intervention, and can grow bigger as you use Nemris.

-----

## Usage

Nemris requires one mandatory argument and supports three optional arguments as well. You'll be able to see a short usage message by means of:

    python nemris.py -h

Such an input will yield you:

    usage: nemris.py [-h] (-u | -s | -d | -a) [-r] [--keep-overlays]
                     [--keep-arcus]

    APK file extractor.

    optional arguments:
      -h, --help       show this help message and exit
      -u, --user       user apps
      -s, --system     system apps
      -d, --disabled   disabled apps
      -a, --all        any app
      -r, --reset      reset Nemris' configuration
      --keep-overlays  extract Substratum overlays
      --keep-arcus     extract theme variants compiled with Arcus

Take care to download both **nemris.py** and the whole **modules** folder.

Nemris expects to find said directory inside its own folder, otherwise it won't work.

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

Since the author considers that one has to have a theme in order to compile its variants, Substratum overlays and Arcus variants are skipped by default. Should you want to extract them nonetheless, use the options below.

`--keep-substratum`: extract any installed Substratum overlay;

`--keep-arcus`: extract theme variants compiled by Arcus.

**You'll be able to use these options only in combination with either the `-u/--user` or the `-a/--all` arguments**.
