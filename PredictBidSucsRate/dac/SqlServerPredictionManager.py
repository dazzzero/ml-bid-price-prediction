# -*- coding: utf-8 -*-
"""
SQL Server용 예측 결과 저장 관리 클래스
"""

import os
import pandas as pd
from datetime import datetime
from SqlServerManager import SqlServerManager


class SqlServerPredictionManager:
    """SQL Server용 예측 결과 저장 및 관리 클래스"""
    
    def __init__(self, host, port, database, username, password, table_name='ML_C'):
        self.db_manager = SqlServerManager.get_instance()
        self.connection = self.db_manager.connect(host, port, database, username, password)
        self.table_name = table_name
        
        if not self.connection:
            raise Exception("SQL Server 연결에 실패했습니다.")
        
        # 테이블 생성 확인
        self.create_table_if_not_exists()
    
    def create_table_if_not_exists(self):
        """테이블이 없으면 생성"""
        try:
            create_table_sql = f"""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{self.table_name}' AND xtype='U')
            CREATE TABLE {self.table_name} (
                입찰번호 VARCHAR(50) NOT NULL,
                입찰차수 VARCHAR(10) NOT NULL,
                기초금액률 DECIMAL(18, 9),
                낙찰하한률 DECIMAL(10, 7),
                기초금액 DECIMAL(20, 2),
                순공사원가 DECIMAL(20, 2),
                간접비 DECIMAL(20, 2),
                A계산여부 VARCHAR(10) DEFAULT '0',
                순공사원가적용여부 VARCHAR(10) DEFAULT '0',
                면허제한코드 VARCHAR(200),
                공고기관코드 VARCHAR(50),
                주공종명 VARCHAR(200),
                공고기관명 VARCHAR(200),
                공고기관점수 DECIMAL(15, 15) DEFAULT 0.000000000000000 NOT NULL,
                공사지역 VARCHAR(400),
                공사지역점수 DECIMAL(15, 15) DEFAULT 0.000000000000000 NOT NULL,
                키워드 VARCHAR(1000),
                키워드점수 DECIMAL(15, 15) DEFAULT 0.000000000000000 NOT NULL,
                공고일자 DATETIME,
                개찰일시 DATETIME,
                예측_URL VARCHAR(4000) NOT NULL,
                업체투찰률_예측 DECIMAL(18, 9),
                예가투찰률_예측 DECIMAL(18, 9),
                참여업체수_예측 INT,
                등록일시 DATETIME NOT NULL DEFAULT GETDATE(),
                예측일시 DATETIME,
                PRIMARY KEY (입찰번호, 입찰차수)
            )
            """
            
            self.connection.execute_non_query(create_table_sql)
            print(f"✅ {self.table_name} 테이블 생성/확인 완료")
            
        except Exception as e:
            print(f"❌ 테이블 생성 실패: {e}")
            raise e
    
    def save_prediction_results(self, result_df, model_version="v0.1.1", remarks="", insert_mode="REPLACE"):
        """
        예측 결과를 SQL Server에 저장
        
        Args:
            result_df (pd.DataFrame): 예측 결과 데이터프레임
            model_version (str): 모델 버전
            remarks (str): 비고
            insert_mode (str): 삽입 모드 (REPLACE, IGNORE, INSERT)
        """
        try:
            print("="*80)
            print(f"💾 SQL Server에 예측 결과 저장 중... (모드: {insert_mode})")
            print("="*80)
            
            # 저장할 데이터 개수
            total_rows = len(result_df)
            saved_count = 0
            updated_count = 0
            ignored_count = 0
            
            # 각 행을 데이터베이스에 저장
            for index, row in result_df.iterrows():
                try:
                    # 데이터 검증 및 준비
                    data = self._prepare_row_data(row, model_version, remarks)
                    
                    # 데이터 검증 로그 (디버깅용)
                    if index < 5:  # 처음 5개 행만 로그 출력
                        print(f"행 {index} 데이터 검증:")
                        print(f"  입찰번호: {data[0]}")
                        print(f"  기초금액률: {data[2]} (범위: -999999999.999999999 ~ 999999999.999999999)")
                        print(f"  낙찰하한률: {data[3]} (범위: -999.9999999 ~ 999.9999999)")
                        print(f"  공고기관점수: {data[13]} (TF-IDF, 범위: 0 ~ 0.999999999999999)")
                        print(f"  공사지역점수: {data[15]} (TF-IDF, 범위: 0 ~ 0.999999999999999)")
                        print(f"  키워드점수: {data[17]} (TF-IDF, 범위: 0 ~ 0.999999999999999)")
                        print(f"  업체투찰률_예측: {data[21]} (범위: -999999999.999999999 ~ 999999999.999999999)")
                        print(f"  예가투찰률_예측: {data[22]} (범위: -999999999.999999999 ~ 999999999.999999999)")
                        print(f"  참여업체수_예측: {data[23]} (범위: -2147483648 ~ 2147483647)")
                        print("---")
                    
                    if insert_mode == "REPLACE":
                        # MERGE 문 사용 (UPSERT)
                        query = f"""
                        MERGE {self.table_name} AS target
                        USING (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) 
                        AS source (입찰번호, 입찰차수, 기초금액률, 낙찰하한률, 기초금액, 순공사원가, 간접비, A계산여부, 
                                  순공사원가적용여부, 면허제한코드, 공고기관코드, 주공종명, 공고기관명, 공고기관점수,
                                  공사지역, 공사지역점수, 키워드, 키워드점수, 공고일자, 개찰일시, 예측_URL,
                                  업체투찰률_예측, 예가투찰률_예측, 참여업체수_예측, 예측일시)
                        ON target.입찰번호 = source.입찰번호 AND target.입찰차수 = source.입찰차수
                        WHEN MATCHED THEN
                            UPDATE SET 
                                기초금액률 = source.기초금액률,
                                낙찰하한률 = source.낙찰하한률,
                                기초금액 = source.기초금액,
                                순공사원가 = source.순공사원가,
                                간접비 = source.간접비,
                                A계산여부 = source.A계산여부,
                                순공사원가적용여부 = source.순공사원가적용여부,
                                면허제한코드 = source.면허제한코드,
                                공고기관코드 = source.공고기관코드,
                                주공종명 = source.주공종명,
                                공고기관명 = source.공고기관명,
                                공고기관점수 = source.공고기관점수,
                                공사지역 = source.공사지역,
                                공사지역점수 = source.공사지역점수,
                                키워드 = source.키워드,
                                키워드점수 = source.키워드점수,
                                공고일자 = source.공고일자,
                                개찰일시 = source.개찰일시,
                                예측_URL = source.예측_URL,
                                업체투찰률_예측 = source.업체투찰률_예측,
                                예가투찰률_예측 = source.예가투찰률_예측,
                                참여업체수_예측 = source.참여업체수_예측,
                                예측일시 = source.예측일시
                        WHEN NOT MATCHED THEN
                            INSERT (입찰번호, 입찰차수, 기초금액률, 낙찰하한률, 기초금액, 순공사원가, 간접비, A계산여부,
                                   순공사원가적용여부, 면허제한코드, 공고기관코드, 주공종명, 공고기관명, 공고기관점수,
                                   공사지역, 공사지역점수, 키워드, 키워드점수, 공고일자, 개찰일시, 예측_URL,
                                   업체투찰률_예측, 예가투찰률_예측, 참여업체수_예측, 예측일시)
                            VALUES (source.입찰번호, source.입찰차수, source.기초금액률, source.낙찰하한률, 
                                   source.기초금액, source.순공사원가, source.간접비, source.A계산여부,
                                   source.순공사원가적용여부, source.면허제한코드, source.공고기관코드, 
                                   source.주공종명, source.공고기관명, source.공고기관점수,
                                   source.공사지역, source.공사지역점수, source.키워드, source.키워드점수,
                                   source.공고일자, source.개찰일시, source.예측_URL,
                                   source.업체투찰률_예측, source.예가투찰률_예측, source.참여업체수_예측, source.예측일시);
                        """
                        
                        # 기존 데이터 존재 여부 확인
                        check_query = f"SELECT COUNT(*) FROM {self.table_name} WHERE 입찰번호 = ? AND 입찰차수 = ?"
                        existing = self.connection.execute_query(check_query, (str(row.get('입찰번호', '')), str(row.get('입찰차수', ''))))
                        if existing is not None and len(existing) > 0 and existing.iloc[0, 0] > 0:
                            updated_count += 1
                        else:
                            saved_count += 1
                    
                    elif insert_mode == "IGNORE":
                        # INSERT 시 중복 무시
                        query = f"""
                        IF NOT EXISTS (SELECT 1 FROM {self.table_name} WHERE 입찰번호 = ? AND 입찰차수 = ?)
                        INSERT INTO {self.table_name} (입찰번호, 입찰차수, 기초금액률, 낙찰하한률, 기초금액, 순공사원가, 간접비, A계산여부,
                                        순공사원가적용여부, 면허제한코드, 공고기관코드, 주공종명, 공고기관명, 공고기관점수,
                                        공사지역, 공사지역점수, 키워드, 키워드점수, 공고일자, 개찰일시, 예측_URL,
                                        업체투찰률_예측, 예가투찰률_예측, 참여업체수_예측, 예측일시)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        data = (str(row.get('입찰번호', '')), str(row.get('입찰차수', ''))) + data
                        saved_count += 1
                    
                    else:  # INSERT
                        query = f"""
                        INSERT INTO {self.table_name} (입찰번호, 입찰차수, 기초금액률, 낙찰하한률, 기초금액, 순공사원가, 간접비, A계산여부,
                                        순공사원가적용여부, 면허제한코드, 공고기관코드, 주공종명, 공고기관명, 공고기관점수,
                                        공사지역, 공사지역점수, 키워드, 키워드점수, 공고일자, 개찰일시, 예측_URL,
                                        업체투찰률_예측, 예가투찰률_예측, 참여업체수_예측, 예측일시)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                        saved_count += 1
                    
                    # 쿼리 실행
                    affected_rows = self.connection.execute_non_query(query, data)
                    
                    if (saved_count + updated_count + ignored_count) % 100 == 0:
                        print(f"진행률: {saved_count + updated_count + ignored_count}/{total_rows} ({(saved_count + updated_count + ignored_count)/total_rows*100:.1f}%)")
                
                except Exception as e:
                    if insert_mode == "INSERT":
                        print(f"⚠️  행 {index} 저장 실패 (중복 데이터): {e}")
                        ignored_count += 1
                    else:
                        print(f"⚠️  행 {index} 저장 실패: {e}")
                        continue
            
            print(f"✅ SQL Server 저장 완료 ({self.table_name}):")
            print(f"   - 새로 저장: {saved_count}건")
            if insert_mode == "REPLACE":
                print(f"   - 업데이트: {updated_count}건")
            print(f"   - 무시됨: {ignored_count}건")
            print("="*80)
            
            return saved_count + updated_count
            
        except Exception as e:
            print(f"❌ SQL Server 저장 실패: {e}")
            raise e
    
    def _prepare_row_data(self, row, model_version, remarks):
        """행 데이터를 데이터베이스 저장 형식으로 준비"""
        import math
        
        # 현재 시간
        now = datetime.now()
        
        def safe_decimal(value, max_digits, decimal_places, is_tfidf=False):
            """DECIMAL 타입에 안전한 값으로 변환"""
            try:
                val = float(value) if value is not None else 0.0
                
                # NaN이나 무한대 값 처리
                if math.isnan(val) or math.isinf(val):
                    return 0.0
                
                # TF-IDF 점수 특별 처리 (DECIMAL(15,15) 사용)
                if is_tfidf:
                    # DECIMAL(15,15)는 0.000000000000001 ~ 0.999999999999999 범위
                    # TF-IDF 점수는 보통 0~1 사이이므로 그대로 사용 가능
                    if val < 0:
                        val = 0.0
                    elif val > 0.999999999999999:  # DECIMAL(15,15) 최대값
                        val = 0.999999999999999
                else:
                    # 일반 DECIMAL 값 처리
                    max_value = 10 ** (max_digits - decimal_places) - 1
                    min_value = -max_value
                    val = max(min_value, min(max_value, val))
                
                return val
            except (ValueError, TypeError):
                return 0.0
        
        def safe_int(value):
            """INT 타입에 안전한 값으로 변환"""
            try:
                val = int(float(value)) if value is not None else 0
                # INT 범위 제한 (-2,147,483,648 ~ 2,147,483,647)
                return max(-2147483648, min(2147483647, val))
            except (ValueError, TypeError):
                return 0
        
        return (
            str(row.get('입찰번호', '')),
            str(row.get('입찰차수', '')),
            safe_decimal(row.get('기초금액률', 0), 18, 9),  # DECIMAL(18, 9)
            safe_decimal(row.get('낙찰하한률', 0), 10, 7),  # DECIMAL(10, 7)
            safe_decimal(row.get('기초금액', 0), 20, 2),     # DECIMAL(20, 2)
            safe_decimal(row.get('순공사원가', 0), 20, 2),    # DECIMAL(20, 2)
            safe_decimal(row.get('간접비', 0), 20, 2),        # DECIMAL(20, 2)
            str(row.get('A계산여부', '0')),
            str(row.get('순공사원가적용여부', '0')),
            str(row.get('면허제한코드', '')),
            str(row.get('공고기관코드', '')),
            str(row.get('주공종명', '')),
            str(row.get('공고기관명', '')),
            safe_decimal(row.get('공고기관점수', 0), 15, 15, is_tfidf=True),  # DECIMAL(15, 15) - TF-IDF
            str(row.get('공사지역', '')),
            safe_decimal(row.get('공사지역점수', 0), 15, 15, is_tfidf=True),  # DECIMAL(15, 15) - TF-IDF
            str(row.get('키워드', '')),
            safe_decimal(row.get('키워드점수', 0), 15, 15, is_tfidf=True),    # DECIMAL(15, 15) - TF-IDF
            row.get('공고일자', None),
            row.get('개찰일시', None),
            str(row.get('예측_URL', '')),
            safe_decimal(row.get('업체투찰률_예측', 0), 18, 9), # DECIMAL(18, 9)
            safe_decimal(row.get('예가투찰률_예측', 0), 18, 9), # DECIMAL(18, 9)
            safe_int(row.get('참여업체수_예측', 0)),           # INT
            now
        )
    
    def get_prediction_results(self, limit=100, offset=0):
        """저장된 예측 결과 조회"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                ORDER BY 예측일시 DESC 
                OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """
            results = self.connection.execute_query(query, (offset, limit))
            return results
        except Exception as e:
            print(f"❌ 데이터 조회 실패: {e}")
            return None
    
    def get_prediction_count(self):
        """저장된 예측 결과 개수 조회"""
        try:
            query = f"SELECT COUNT(*) as count FROM {self.table_name}"
            result = self.connection.execute_query(query)
            return result.iloc[0, 0] if result is not None and len(result) > 0 else 0
        except Exception as e:
            print(f"❌ 데이터 개수 조회 실패: {e}")
            return 0
    
    def get_prediction_summary(self):
        """예측 결과 요약 통계 조회"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as 총건수,
                    AVG(업체투찰률_예측) as 평균업체투찰률,
                    AVG(예가투찰률_예측) as 평균예가투찰률,
                    AVG(참여업체수_예측) as 평균참여업체수,
                    MIN(예측일시) as 최초예측일시,
                    MAX(예측일시) as 최근예측일시
                FROM {self.table_name}
            """
            result = self.connection.execute_query(query)
            if result is not None and len(result) > 0:
                return result.iloc[0].tolist()
            return None
        except Exception as e:
            print(f"❌ 요약 통계 조회 실패: {e}")
            return None
    
    def search_by_bid_number(self, bid_number):
        """입찰번호로 검색"""
        try:
            query = f"""
                SELECT * FROM {self.table_name} 
                WHERE 입찰번호 LIKE ? 
                ORDER BY 예측일시 DESC
            """
            results = self.connection.execute_query(query, (f'%{bid_number}%',))
            return results
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return None
    
    def delete_old_predictions(self, days=30):
        """오래된 예측 결과 삭제"""
        try:
            query = f"""
                DELETE FROM {self.table_name} 
                WHERE 예측일시 < DATEADD(day, -?, GETDATE())
            """
            affected_rows = self.connection.execute_non_query(query, (days,))
            print(f"✅ {days}일 이전 예측 결과 {affected_rows}건 삭제 완료")
            return affected_rows
        except Exception as e:
            print(f"❌ 오래된 데이터 삭제 실패: {e}")
            return 0
