# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 14:56:59 2021

@author: USER
"""

import os
import sqlite3


class PreferenceConfiguration:
    __dbname = "preference.db"
    __dbpath = os.path.dirname( os.path.abspath( __file__ ) )

    @classmethod
    def dbPath(cls):
        return cls.__dbpath

    @classmethod
    def dbName(cls):
        return cls.__dbName
    
    @classmethod
    def connectionString(cls):
        return cls.__dbpath+'\\'+cls.__dbname
    

class PreferenceTable:
    __con = None
    __cur = None
    __table = ""
    
    def __init__(self, tableName):
        self.__table = tableName
        self.__con = sqlite3.connect(PreferenceConfiguration.connectionString()) 
        self.__cur = self.__con.cursor()

    def getValue(self, key):
        if self.isValid():
            self.__cur.execute("SELECT value FROM " + self.tableName() + " WHERE key=?", (key,)) 
            val, = self.__cur.fetchone()

            if val==None:
                return ""
            else:
                return val
        else:
            return ""
    
    def isExistsKey(self, key):
        if self.isValid():
            self.__cur.execute("SELECT value FROM " + self.tableName() + " WHERE key=?", (key,)) 
            found = self.__cur.fetchone()

            if found != None:
                return 1
            else:
                return 0
        else:
            return -1        

    def setValue(self, key, val):
        if self.isExistsKey(key)==1:
            self.__cur.execute("UPDATE " + self.tableName() + " SET value=? WHERE key=?", (val, key)) 
            self.__con.commit()
        else:
            self.__cur.execute("INSERT INTO " + self.tableName() + " (key,value) VALUES (?,?)", (key,val)) 
            self.__con.commit()
        
    def tableName(self):
        return self.__table
    
    def isValid(self):
        if(self.__cur != None and self.__table != ""):
            return True
        else:
            return False
    
    def createIfNotExists(self):
        if self.isValid():
            self.__cur.execute("CREATE TABLE IF NOT EXISTS '"+ self.__table +"' (key TEXT NOT NULL, value TEXT NOT NULL)")
            
    
    
"""
class PreferenceAttributes:
    db = PreferenceTable("attributes")

    def getVlaue(self, key):
        return self.db.getValue(key)
    
    
    def setValue(self, key, val):
        self.db.update(key, val)
        print("PreferenceAttributes:setValue" + key + " = " + val)
"""        


class Preference:
    __instance = None
    
    attributes = PreferenceTable("attributes")
    #account = PreferenceTable("account")
    
    
    def __init__(self):
        if Preference.__instance != None:
            raise Exception("This class is a singletom!")
        else:
            Preference.__instance = self
            self.attributes.createIfNotExists()
            #self.account.createIfNotExists()

    
    def getValue(self, key):
        return self.attributes.getValue(key)

    def setValue(self, key, val):
        self.attributes.setValue(key,val)

    @classmethod
    def getInstance(cls):
        if cls.__instance == None:
            Preference()
        
        return cls.__instance


      