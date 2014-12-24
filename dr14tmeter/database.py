# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011  Simone Riva
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sqlite3 

class dr_database :
    
    def __init__(self):
        None
        
    def dr14_db_structure(self):
        db = """
            create table track (
                Id integer primary key autoincrement ,
                Title varchar(60) ,
                date integer ,
                sha1 char(40) not null unique
            ) ;
            
            create table DR (
                DR integer unique not null ,
            ) ;
                        
            create table Genre (
                Id integer primary key autoincrement ,
                Name varchar(40) 
            ) ;
            
            create table Artist (
                Id integer primary key autoincrement ,
                Name varchar(60)
            )
            
            create table Album (
                Id integer primary key autoincrement ,
                DR integer not null ,
                Title varchar(100) ,
                foreign key ( IdArtist ) references Artist( Id )
            )
            
        """