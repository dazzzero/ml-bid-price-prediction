# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 18:21:31 2021

@author: USER

ex)
db = DatabaseManager.getInstance().use("etrade").command()
db.selectOne(query, param)
db.getValue(query, param)
db.select(query, param) //배열
db.update(query, param)
db.insert(query, param)
db.delete(query, param)
"""
import os
import sqlite3


class ConnectionAttribute:

    def __init__(self):
        self.__name = "None"
        self.__dbName = ""
        self.__dbPath = ""
        self.__connectionString = ""
        self.__setup_sql = ""        
    
    def setName(self, v):
        self.__name = v;
        
    def getName(self):
        return self.__name
    
    def setDbName(self,v):
        self.__dbName = v
        
    def setDbPath(self,v):
        self.__dbPath = v
        
    def getDbName(self):
        return self.__dbName
    
    def getDbPath(self):
        return self.__dbPath
    
    def getConnectionString(self):    
        return self.__dbPath+'\\'+self.__dbName
    
    def setSetupSql(self, sql):
        if sql[:7]=="file://":
           with open(sql[7:], "r") as f:
               data = f.read()
        else:
            data = sql
            
        self.__setup_sql = data
    
    def getSetupSql(self):
        return self.__setup_sql
        
    
    @classmethod
    def build(cls, name, dbname, path, setup_sql):
        attr = ConnectionAttribute()
        attr.setName(name)
        attr.setDbName(dbname)
        attr.setDbPath(path)
        attr.setSetupSql(setup_sql)
        return attr
    


  
        
class SqlCommand:
    
    def __init__(self, con):
        self.__conn = con
        self.cursor = None
        
    def getConnection(self):
        return self.__conn.getConnection()
    
    def select(self, query, param):
        print('select')
        c = self.getConnection().cursor().execute(query, param)
        rows = c.fetchall()
        if rows != None and len(rows) > 0:
            return rows
        else:
            return None

    def selectOne(self, query, param):
        print('select')
        c = self.getConnection().cursor().execute(query, param)
        row = c.fetchone()
        if row != None and len(row) > 0:
            return row
        else:
            return None
        
        
    def update(self, query, param):
        print('update')
        self.executeNoResult(query, param)
        
        
    def delete(self, query, param):
        print('delete')
        self.executeNoResult(query, param)

        
    def insert(self, query, param):
        print('insert')        
        self.executeNoResult(query, param)      

    def getValue(self, query, param):
        print('getValue')
        val, = self.getConnection().cursor().execute(query, param)
        if val != None and len(val) > 0:
            return val
        else:
            return None        
    
    def execute(self, query, param):
        print('execute ' + query)
        result = self.getConnection().cursor().execute(query, param)
        if result != None:
            return result
        else:
            return None
        
    def executeNoResult(self, query, param):
        print('execute')
        self.getConnection().cursor().execute(query, param)
        self.getConnection().commit()             
        
    def comit(self):
        print('commit')
        self.getConnection().commit()        
    
    def tableInfo(self, tablename):
        sql = "PRAGMA table_info('"+tablename+"')"
        param = ()
        return self.select(sql, param)
    
    def tableList(self):
        sql = "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table', 'view') ORDER BY 1;"
        param = ()
        return self.select(sql, param)

class Connection:
   
    def __init__(self):
        print('Connection::__init__')
        self.__attr = ConnectionAttribute()
        self.__conn = None
        self.__dbfile= None       
    
    @classmethod
    def of(cls, attr):
        con = Connection()
        con.connect(attr)
                        
        return con
  
    def connect(self, attr):
        self.disconnect()
        self.__attr = attr
        self.__dbfile= self.__attr.getConnectionString()
        
        if(os.path.exists(self.__dbfile)):
            self.__conn = sqlite3.connect(self.__dbfile)
            self.__is_open = True
        else:
            self.__is_open = False
    
    def disconnect(self):
        if self.isValidConnection():
            self.__conn.close()
            self.__conn = None
            self.__is_open = False
            
    def isOpen(self):
        return self.__is_open

    def isValidConnection(self):
        return (self.__conn !=None and self.isOpen())

    def getConnection(self):
        return self.__conn
    
    def cursor(self):
        if self.isValidConnection():
            return self.__conn.cursor()
        else:
            raise Exception('Connection::cursor() 연결된 DB가 없습니다. ')
    
    def attributes(self):
        return self.__attr;
    
    def getName(self):
        return self.__attr.getName()
    
    def command(self):
        if self.isValidConnection():
            return SqlCommand(self)
        else:
            raise Exception('Connection::command() 유효한 DB컨넥션이 아닙니다. ')
            
    def createIfNotExists(self):
        if self.isValidConnection():
            sql = self.attributes().getSetupSql()
            sqls = sql.split(';')
            param = ()
            
            if (sql != "" and len(sqls)>1):
                cmd = self.command()
                for s in sqls:
                    cmd.execute(s, param)
                    
                cmd.comit()
        else:
            raise Exception('Connection::command() 유효한 DB컨넥션이 아닙니다[1]. ')
        
    
    


class DatabaseManager:
    __instance = None
    default_local_path = os.path.dirname( os.path.abspath( __file__ ) )
    #attributes = PreferenceTable("attributes")
    
    
    def __init__(self):
        if DatabaseManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.__map = {}                
            DatabaseManager.__instance = self
            
            # 1. 기본 연결 DB            
            con = Connection.of(ConnectionAttribute.build(
                                                        'image_search_result'
                                                        , 'image_search_result.db'
                                                        , self.default_local_path
                                                        , "file://" + self.default_local_path + "\\setup\\image_search_result.sql"
                                                        ))
            
            self.__map[con.getName()] = con
            
            # 2. 예측 결과 DB
            con2 = Connection.of(ConnectionAttribute.build(
                                                        'prediction_result'
                                                        , 'prediction_result.db'
                                                        , self.default_local_path
                                                        , "file://" + self.default_local_path + "\\setup\\prediction_result.sql"
                                                        ))
            
            self.__map[con2.getName()] = con2
            
            # 테이블이 존재하지 않는다면 초기화
            self.createIfNotExists()
        
    
    def use(self, dbName):
        if dbName in self.__map:
            return self.__map.get(dbName)
        else:
            raise Exception('존재하지 않은 데이타베이스입니다. ')

    def createIfNotExists(self):
        print('createIfNotExists')
        
        #iterator 로 순회하면서 해당 함수를 호출해줌
        it = iter(self.__map.keys())
        while True:
            try:
                key = next(it)
                v = self.__map.get(key)
                v.createIfNotExists()
            except StopIteration:
                break        
        

    @classmethod
    def getInstance(cls):
        if cls.__instance == None:
            DatabaseManager()
        
        return cls.__instance

