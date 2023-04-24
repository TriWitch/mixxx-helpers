#!/usr/bin/env python
#
# playlistport.pl - Program to import and export Mixxx playlists from an XML file.
# Apr 15, 2012 - Joe Hartley (jh@brainiac.com)
#    Based on crateport.pl by Phillip Whelan - https://github.com/pwhelan/mixxx-crateport
#
# Command line options:
#    -i, --import
#    -e, --export (default)
#    -d, --dbname <dbfilename> (default = mixx local default)
#    -p, --playlist <playlist_name> (for import only)
#    -f  --plfolder <> Folder to export playists to (default Music/Playlists/Mixxx)
#
# Note that minidom treats each newline as a separate child entity,
# so a 'pretty' XML file may need to be filtered through xmllint before it
# can be imported, like so:
#   xmllint --noblanks pretty.xml | python playlistport.py -i
# Also, this exports raw XML, so for readability you may want to pipe the output
# through xmllint like so:
#   python playlistport.py | xmllint --format

import sqlite3
import os
import sys
import xml.dom
import xml.dom.minidom
import platform
import fileinput
from optparse import OptionParser
import sys
import codecs
from datetime import datetime


import unicodedata

def generatePlaylistXML(Playlists):
    dom = xml.dom.getDOMImplementation()
    document = dom.createDocument(None, None, None)
    nPlaylists = document.createElement('Playlists')
    document.appendChild(nPlaylists)
    
    for Playlistname in Playlists:
        nPlaylist = document.createElement('Playlist')
        nPlaylists.appendChild(nPlaylist)
        nPlaylist.setAttribute('name', Playlistname)
        
        for track in Playlists[Playlistname]:
            ntrack = document.createElement('track')
            nPlaylist.appendChild(ntrack)
            for key in track.keys():
                ntrack.setAttribute(key, unicode(track[key]))
    
    return document.toxml()


def generatePlaylistsm3u(Playlists,folder):
    print Playlists.keys()," to ",folder
    
    for Playlistname in Playlists:
        if len(Playlists[Playlistname])<=5:
            print Playlistname," too short"
            continue
        
        with codecs.open(folder+"/"+Playlistname+".m3u","w",'utf-8') as newfile:
                newfile.write("#m3u generated from Mixxx DB\n")
                for track in Playlists[Playlistname]:

                    
    #                try:
    #                    print unicodedata.name(track['location'][67])
    #                except:
    #                    pass
                    newfile.write(u"# {artist} - {title}\n".format(title=(track['title']),artist=(track['artist'])))
                    newfile.write(u"{location}\n".format(location=(track['location'])))
    
    return None






def getPlaylists(conn, plname):
    cursor = conn.cursor()
    Playlists = {}

    if plname == None:
        cursor.execute("SELECT id, name FROM Playlists")
    else:
        cursor.execute("""SELECT id, name FROM Playlists WHERE name = ?
                       """, [str(plname)])    
    row = cursor.fetchone()
    while row:
        
        
        Playlists[row['name']] = []
        
        cur2 = conn.cursor()
        ## JH - the ORDER BY clause was added
        
        cur2.execute("""
            SELECT
                library.artist AS artist,
                library.title AS title,
                track_locations.location,
                track_locations.filename
            
            FROM PlaylistTracks
                INNER JOIN library
                    ON PlaylistTracks.track_id = library.id
                INNER JOIN track_locations
                    ON library.location = track_locations.id
            WHERE
                PlaylistTracks.Playlist_id = {id}
            ORDER BY PlaylistTracks.position
            
            """.format(id=row['id']))
        
        track = cur2.fetchone()
        
        while track:
            Playlists[row['name']].append(track)
            track = cur2.fetchone()
        
        row = cursor.fetchone()
    
    return Playlists

def getCrates(conn, craten ):
    cursor = conn.cursor()
    Playlists = {}

    if craten == None:
        cursor.execute("SELECT id, name FROM crates")
    else:
        cursor.execute("""SELECT id, name FROM crates WHERE name = ?
                       """, [str(craten)])    
    row = cursor.fetchone()
    while row:
        
        
        Playlists[row['name']] = []
        
        cur2 = conn.cursor()
        ## JH - the ORDER BY clause was added
        
        cur2.execute("""
            SELECT
                library.artist AS artist,
                library.title AS title,
                track_locations.location,
                track_locations.filename
            
            FROM crate_tracks
                INNER JOIN library
                    ON crate_tracks.track_id = library.id
                INNER JOIN track_locations
                    ON library.location = track_locations.id
            WHERE
                crate_tracks.crate_id = {id}

            
            """.format(id=row['id']))
        
        track = cur2.fetchone()
        
        while track:
            Playlists[row['name']].append(track)
            track = cur2.fetchone()
        
        row = cursor.fetchone()
    
    return Playlists











def findTrack_fromFilename(conn, filename_full ):
    cursor = conn.cursor()
    
    cursor.execute(u"""
        SELECT
            l.id,
            l.filetype
            FROM library l
            INNER JOIN track_locations tl
                ON l.location = tl.id
            WHERE 
                (tl.location = ?)
        """,(filename_full.decode('utf-8'), ))
    
    track = cursor.fetchone()
    if track != None:
        #print "Found Location"
        return track
    
        
    filen=filename_full.split("/")[-1] 
    cursor.execute(u"""
        SELECT
            l.id,
            l.filetype
            FROM library l
            INNER JOIN track_locations tl
                ON l.location = tl.id
            WHERE 
                (tl.filename = ?)
        """, (filen.decode('utf-8'), ))
    if track != None:
        #print "Found Filename"
        return track
    
    title=filen.split(" - ")[-1].split(".")[-2].strip()
    artist=filen.split(" - ")[0]
    
    cursor.execute(u"""
        SELECT
            l.id,
            l.filetype
            FROM library l
            WHERE 
                (l.artist = ? AND l.title = ?)
        """, (artist.decode('utf-8'), title.decode('utf-8')))
    
    track = cursor.fetchone()
    if track != None:
        #print "Found artist+title" 
        return track
    
    
    cursor.execute(u"""
        SELECT
            l.id,
            l.filetype
            FROM library l
            WHERE 
                (l.title = ?)
        """, (title.decode('utf-8'), ))
    
    track = cursor.fetchone()
    if track != None:
        print "Found title only ",title,artist,filename 
        return track

    return None




def findTrack(conn, ntrack):
    location = ntrack.getAttribute('location')
    artist = ntrack.getAttribute('artist')
    title = ntrack.getAttribute('title')
    filename = ntrack.getAttribute('filename')
    
    cursor = conn.cursor()
    
    cursor.execute(u"""
        SELECT
            l.id,
            l.filetype
            FROM library l
            INNER JOIN track_locations tl
                ON l.location = tl.id
            WHERE 
                (tl.location = ?)
        """, (location,))
    
    track = cursor.fetchone()
    if track != None:
        return track
    
    cursor.execute(u"""
        SELECT
            l.id,
            l.filetype
            FROM library l
            INNER JOIN track_locations tl
                ON l.location = tl.id
            WHERE 
                (tl.filename = ?)
        """, (filename,))
    
    track = cursor.fetchone()
    if track != None:
        return track
    
    cursor.execute(u"""
        SELECT
            l.id,
            l.filetype
            FROM library l
            WHERE 
                (l.artist = ? AND l.title = ?)
        """, (artist, title))
    
    track = cursor.fetchone()
    if track != None:
        return track
    
    return None

def importPlaylistm3u(conn, nPlaylist, name ):
    
    ref_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print name,"@",ref_time
    cursor = conn.cursor()
    
    
    cursor.execute("SELECT id FROM Playlists WHERE name = '{name}'".format(name=name))
    Playlist = cursor.fetchone()
    print "Testing",Playlist
    if Playlist is None:
        print "Creating new Playlist:", name
        
        id_max,pos_max=cursor.execute("SELECT Max(id),Max(position) FROM Playlists").fetchone()
        
        print id_max,pos_max        
        
        cursor.execute("INSERT INTO Playlists(name,position,hidden,date_created,date_modified,locked) VALUES('{name}',{posit},0,'{date}','{date}',0)".format(name=unicode(name),id=int(id_max)+1,posit=int(pos_max)+1,date=ref_time))


    conn.commit()
    cursor.execute("SELECT id FROM Playlists WHERE name = '{name}'".format(name=name))
    Playlist = cursor.fetchone()
    
    max_PT_id, =cursor.execute("SELECT max(id) FROM PlaylistTracks").fetchone()
    max_PT_pos, =cursor.execute("SELECT max(position) FROM PlaylistTracks where Playlist_id = '{plid}'".format(plid=str(Playlist['id']))).fetchone()
    if max_PT_pos is None:
        max_PT_pos=0
        
    for ntrack in nPlaylist:

    #        print " --- ",ntrack
            try:
                track = findTrack_fromFilename(conn, ntrack)
            except Exception,e:
                print "Track Finder crashed for ",ntrack
                print e
                raise
                continue    
            
            if track is not None:
                    
                    cursor.execute("SELECT track_id,position FROM PlaylistTracks WHERE Playlist_id = '{plid}' AND track_id = '{tid}'".format(plid=str(Playlist['id']),tid=str(track['id'])))
                    dummy = cursor.fetchone()
                    
                    if dummy is not None:
                        #print "Already in List @ ",dummy
                        continue
                    
                    cursor.execute("""
                        INSERT INTO PlaylistTracks(playlist_id, track_id,position,pl_datetime_added)
                        VALUES({playlist_id}, {track_id},{position},'{pl_datetime_added}')
                    """.format(playlist_id=Playlist['id'],
                               track_id=track['id'],
                               position=int(max_PT_pos)+1,
                               pl_datetime_added = ref_time)
                               )

                    conn.commit() #Commit after each track is not nice,.. but well.

                    max_PT_pos+=1
                    
                    
            else:
                print "WARNING: Track not found :",ntrack


def importPlaylistXML(conn, dPlaylist):
    cursor = conn.cursor()
    nPlaylists = dPlaylist.documentElement
    print(dPlaylist.documentElement) 
    if nPlaylists.tagName != 'Playlists':
        raise Exception('Not a Playlists XML File')
    
    for nPlaylist in nPlaylists.childNodes:
        if nPlaylist.tagName != 'Playlist':
            raise Exception('Not a Playlist')
        
        try:
            cursor.execute("INSERT INTO Playlists(name) VALUES(?)", 
                (nPlaylist.getAttribute('name'),))
            print "Creating new Playlist:", nPlaylist.getAttribute('name')
        except sqlite3.IntegrityError:
            print "Already Created:", nPlaylist.getAttribute('name')
        
        cursor.execute("SELECT id FROM Playlists WHERE name = ?", 
            (nPlaylist.getAttribute('name'),))
        Playlist = cursor.fetchone()
        
        for ntrack in nPlaylist.childNodes:
            if nPlaylist.tagName != 'Playlist':
                raise Exception('Not a Playlist')
            track = findTrack(conn, ntrack)

            if track != None:
                try:
                    print "Adding a Track"
                    cursor.execute("""
                        INSERT INTO PlaylistTracks(Playlist_id, track_id)
                        VALUES(?, ?)
                    """, (str(Playlist['id']), track['id']))
                except sqlite3.IntegrityError:
                    print "Track already in Playlist"

def main():
    home = os.path.expanduser('~')
    uname = platform.uname()
    if uname[0] == 'Darwin':
        cfgdir = home + '/Library/Application Support/Mixxx'
    elif uname[0] == 'Linux':
        cfgdir = home + '/.mixxx'
    
    defdb = cfgdir + '/mixxxdb.sqlite'

    opt = OptionParser(description='Import and Export Playlists from Mixxx')
    opt.add_option('-i', '--import', dest='export', action='store_false')
    opt.add_option('-e', '--export', dest='export', action='store_true')
    opt.add_option('-d', '--dbname', dest='dbname', default=defdb)
    opt.add_option('-p', '--playlist', dest='plname', default=None)
    opt.add_option('-f', '--plfolder', dest='plfolder', default = '~/Music/Playlist/Mixxx')
    
    (options, args) = opt.parse_args()

    if options.export == None: options.export = True;    
    conn = sqlite3.connect(options.dbname)
    conn.row_factory = sqlite3.Row
    
    if options.export == True:
        output = open(args[0], "w")  if len(args) > 0 else sys.stdout
        Playlists = getPlaylists(conn, options.plname)
        generatePlaylistsm3u(Playlists,folder=options.plfolder)
        Crates = getCrates(conn, options.plname)
        generatePlaylistsm3u(Crates,folder=options.plfolder+"/Crates")
        #output.write(generatePlaylistXML(Playlists).encode('utf8') + "\n")
    else:
        #input = open(args[0], "r") if len(args) > 0 else sys.stdin
        #Playlists = xml.dom.minidom.parse(input)
        #importPlaylistXML(conn, Playlists)
        nList=[line.rstrip() for line in open(options.plname, "r").readlines() if not line.startswith("#") and len(line)>5]
        importPlaylistm3u(conn, nList, options.plname.split("/")[-1].replace(".m3u",""))
        
        
        conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
    

