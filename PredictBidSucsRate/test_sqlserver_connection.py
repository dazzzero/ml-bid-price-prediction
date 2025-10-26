# -*- coding: utf-8 -*-
"""
SQL Server 연결 테스트 스크립트
"""

import os
import sys

# 데이터베이스 관련 import
sys.path.append(os.path.join(os.getcwd(), 'dac'))
from SqlServerManager import SqlServerManager


def test_sqlserver_connection():
    """SQL Server 연결 테스트"""
    print("="*80)
    print("🔧 SQL Server 연결 테스트")
    print("="*80)
    
    # 연결 정보
    host = '192.168.0.218'
    port = 1433
    database = 'bips'
    username = 'bips'
    password = 'bips1!'
    
    print(f"연결 정보:")
    print(f"  호스트: {host}")
    print(f"  포트: {port}")
    print(f"  데이터베이스: {database}")
    print(f"  사용자: {username}")
    print("="*80)
    
    try:
        # SQL Server 매니저 생성
        db_manager = SqlServerManager.get_instance()
        
        # 연결 시도
        print("📡 SQL Server 연결 시도 중...")
        connection = db_manager.connect(host, port, database, username, password)
        
        if connection:
            print("✅ SQL Server 연결 성공!")
            
            # 연결 테스트
            print("\n🔍 연결 테스트 수행 중...")
            if connection.test_connection():
                print("✅ 연결 테스트 성공!")
                
                # 서버 정보 조회
                print("\n📊 서버 정보 조회 중...")
                try:
                    # 현재 시간 조회
                    time_query = "SELECT GETDATE() as current_time"
                    time_result = connection.execute_query(time_query)
                    if time_result is not None and len(time_result) > 0:
                        print(f"현재 서버 시간: {time_result.iloc[0, 0]}")
                    
                    # SQL Server 버전 조회
                    version_query = "SELECT @@VERSION as sql_version"
                    version_result = connection.execute_query(version_query)
                    if version_result is not None and len(version_result) > 0:
                        version_text = version_result.iloc[0, 0]
                        print(f"SQL Server 버전: {version_text[:100]}...")
                    
                    # 데이터베이스 정보 조회
                    db_query = "SELECT DB_NAME() as database_name, USER_NAME() as user_name"
                    db_result = connection.execute_query(db_query)
                    if db_result is not None and len(db_result) > 0:
                        print(f"현재 데이터베이스: {db_result.iloc[0, 0]}")
                        print(f"현재 사용자: {db_result.iloc[0, 1]}")
                    
                    print("\n✅ 모든 테스트 완료!")
                    print("SQL Server 연결이 정상적으로 작동합니다.")
                    
                except Exception as e:
                    print(f"⚠️  서버 정보 조회 실패: {e}")
                
            else:
                print("❌ 연결 테스트 실패!")
            
            # 연결 해제
            print("\n🔌 연결 해제 중...")
            db_manager.disconnect()
            print("✅ 연결 해제 완료")
            
        else:
            print("❌ SQL Server 연결 실패!")
            print("다음을 확인해주세요:")
            print("1. SQL Server가 실행 중인지 확인")
            print("2. 네트워크 연결 상태 확인")
            print("3. 방화벽 설정 확인")
            print("4. 연결 정보가 올바른지 확인")
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n가능한 해결 방법:")
        print("1. pyodbc 라이브러리 설치: pip install pyodbc")
        print("2. SQL Server ODBC 드라이버 설치")
        print("3. 네트워크 연결 확인")
        print("4. SQL Server 서비스 상태 확인")
    
    print("="*80)


if __name__ == "__main__":
    test_sqlserver_connection()

