# mixxx-helpers
Some helper libraries for managing the mixxxx library (the os DJ tool), such as batch playlist import/export, copying the library from one device to another etc.

# RootChanger
allows to change the paths to Music Files in the Mixxx Database (e.g. when you sync the files and music databases between different Machines).

Useage:
python RootChanger.py -d <source_database>.sqlite -n <target_database>.sqlite -s <source-path-to-music-library> -t <target-path-to-music-library>
 

# Playlist import & export
ImportExportPlaylists.py extracts all the playlists and crates from Mixxx as m3u playlists, or creates mixxx playlists from m3u files based on a filename matching process.

Useage for Export:
python3 /home/helge/bin/MixxxHelpers/ImportExportPlaylists.py -e -f <Folder to export to> [-d <Mixx-database if not in default location>] 

Useage for Import:
python3 /home/helge/bin/MixxxHelpers/ImportExportPlaylists.py -i -p <playlist-to--import.m3u> [-d <Mixx-database if not in default location>] 
