# -*- coding: utf-8 -*-
"""
SQL Server 데이터베이스 연결 관리 클래스
"""

import os
import pyodbc
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import urllib.parse


class SqlServerConnection:
    """SQL Server 연결 클래스"""
    
    def __init__(self, host, port, database, username, password):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        self.engine = None
        self.session = None
        
    def connect(self):
        """SQL Server에 연결"""
        try:
            # pyodbc 연결 문자열
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"Encrypt=no;"
                f"TrustServerCertificate=yes;"
            )
            
            # pyodbc 연결
            self.connection = pyodbc.connect(connection_string)
            print(f"✅ SQL Server 연결 성공: {self.host}:{self.port}/{self.database}")
            
            # SQLAlchemy 엔진 생성
            params = urllib.parse.quote_plus(connection_string)
            self.engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
            
            # 세션 생성
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            return True
            
        except Exception as e:
            print(f"❌ SQL Server 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """연결 해제"""
        try:
            if self.session:
                self.session.close()
            if self.connection:
                self.connection.close()
            print("✅ SQL Server 연결 해제 완료")
        except Exception as e:
            print(f"❌ 연결 해제 실패: {e}")
    
    def execute_query(self, query, params=None):
        """쿼리 실행 (SELECT)"""
        try:
            if params:
                return pd.read_sql(query, self.connection, params=params)
            else:
                return pd.read_sql(query, self.connection)
        except Exception as e:
            print(f"❌ 쿼리 실행 실패: {e}")
            return None
    
    def execute_non_query(self, query, params=None):
        """쿼리 실행 (INSERT, UPDATE, DELETE)"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ 쿼리 실행 실패: {e}")
            self.connection.rollback()
            return 0
    
    def execute_many(self, query, params_list):
        """여러 개의 파라미터로 쿼리 실행"""
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ 배치 쿼리 실행 실패: {e}")
            self.connection.rollback()
            return 0
    
    def test_connection(self):
        """연결 테스트"""
        try:
            result = self.execute_query("SELECT 1 as test")
            if result is not None and len(result) > 0:
                print("✅ SQL Server 연결 테스트 성공")
                return True
            else:
                print("❌ SQL Server 연결 테스트 실패")
                return False
        except Exception as e:
            print(f"❌ 연결 테스트 실패: {e}")
            return False


class SqlServerManager:
    """SQL Server 데이터베이스 관리 클래스"""
    
    __instance = None
    
    def __init__(self):
        if SqlServerManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.connection = None
            SqlServerManager.__instance = self
    
    def connect(self, host, port, database, username, password):
        """SQL Server에 연결"""
        try:
            self.connection = SqlServerConnection(host, port, database, username, password)
            if self.connection.connect():
                return self.connection
            else:
                return None
        except Exception as e:
            print(f"❌ SQL Server 연결 실패: {e}")
            return None
    
    def get_connection(self):
        """연결 객체 반환"""
        return self.connection
    
    def disconnect(self):
        """연결 해제"""
        if self.connection:
            self.connection.disconnect()
            self.connection = None
    
    @classmethod
    def get_instance(cls):
        """싱글톤 인스턴스 반환"""
        if cls.__instance is None:
            cls()
        return cls.__instance

