#!/usr/bin/env python
#
# Command line options:
#    -d, --import db
#    -n, --export db copy
#    -s, folder to change
#    -t, folder to change to
#

import sqlite3
import os
import sys
import platform
from optparse import OptionParser

import shutil


def replaceText(conn,table,field,to_find,to_replace):
    "Just replace the text to_find with to_replace in each field of the table provided"
    
    cursor = conn.cursor()
    
    cursor.execute("""
        update {table_name} set 
                    {field} = replace({field}, '{to_find}', '{to_replace}')
        ;
        """.format(table_name=table,field=field,to_find=to_find,to_replace=to_replace))    
    return None



def replaceRootFolder(conn, source_folder, target_folder):
    "Mixx has root folder name in four tables"
    replaceText(conn,table="LibraryHashes",field="directory_path",to_find=source_folder,to_replace=target_folder)
    replaceText(conn,table="directories",field="directory",to_find=source_folder,to_replace=target_folder)
    replaceText(conn,table="track_locations",field="location",to_find=source_folder,to_replace=target_folder)
    replaceText(conn,table="track_locations",field="directory",to_find=source_folder,to_replace=target_folder)



def main():
    home = os.path.expanduser('~')
    uname = platform.uname()
    if uname[0] == 'Darwin':
        cfgdir = home + '/Library/Application Support/Mixxx'
    elif uname[0] == 'Linux':
        cfgdir = home + '/.mixxx'
    
    defdb = cfgdir + '/mixxxdb.sqlite'

    opt = OptionParser(description='Transfer Databases between Mixxx-Applications')
    opt.add_option('-s', '--source', dest='source_folder')
    opt.add_option('-t', '--target', dest='target_folder')
    opt.add_option('-d', '--dbname', dest='dbname', default=defdb)
    opt.add_option('-n', '--newdb', dest='dbtarget', default=defdb+"_conv.sqlite")
    
    (options, args) = opt.parse_args()
    
    if options.source_folder is None:
        print "No source folder specified for replacement(-s)"
        exit()
        
    if options.source_folder.endswith("/"):  options.source_folder=options.source_folder[:-1]
        
    if options.target_folder is None:
        print "No target folder specified for the replacement(-t)"
        exit()
        
    if options.target_folder.endswith("/"):  options.target_folder=options.target_folder[:-1]
    
    shutil.copyfile(options.dbname, options.dbtarget)
    
    conn = sqlite3.connect(options.dbtarget)
    conn.row_factory = sqlite3.Row
    replaceRootFolder(conn,options.source_folder,options.target_folder)
    
     
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
    

