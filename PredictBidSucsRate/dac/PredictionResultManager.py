# -*- coding: utf-8 -*-
"""
예측 결과 데이터베이스 저장 관리 클래스
"""

import os
import pandas as pd
from datetime import datetime
from DatabaseManager import DatabaseManager, ConnectionAttribute


class PredictionResultManager:
    """예측 결과를 데이터베이스에 저장하고 관리하는 클래스"""
    
    def __init__(self):
        self.db_manager = DatabaseManager.getInstance()
        self.db_name = "ml_c"
        self.setup_database()
    
    def setup_database(self):
        """예측 결과 데이터베이스 설정"""
        try:
            # 현재 디렉토리 경로
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 데이터베이스 연결 속성 생성
            db_attr = ConnectionAttribute.build(
                self.db_name,
                'ml_c.db',
                current_dir,
                "file://" + os.path.join(current_dir, "setup", "prediction_result.sql")
            )
            
            # 데이터베이스 연결
            self.connection = self.db_manager.use(self.db_name) if self.db_name in self.db_manager._DatabaseManager__map else None
            
            if not self.connection:
                # 새로운 연결 생성
                from DatabaseManager import Connection
                self.connection = Connection.of(db_attr)
                self.db_manager._DatabaseManager__map[self.db_name] = self.connection
            
            print(f"✅ 예측 결과 데이터베이스 연결 완료: {self.db_name}")
            
        except Exception as e:
            print(f"❌ 데이터베이스 설정 실패: {e}")
            raise e
    
    def save_prediction_results(self, result_df, model_version="v0.1.1", remarks=""):
        """
        예측 결과를 데이터베이스에 저장
        
        Args:
            result_df (pd.DataFrame): 예측 결과 데이터프레임
            model_version (str): 모델 버전
            remarks (str): 비고
        """
        try:
            print("="*80)
            print("💾 예측 결과를 데이터베이스에 저장 중...")
            print("="*80)
            
            # 데이터베이스 명령 객체 가져오기
            db_cmd = self.connection.command()
            
            # 저장할 데이터 개수
            total_rows = len(result_df)
            saved_count = 0
            
            # 각 행을 데이터베이스에 저장
            for index, row in result_df.iterrows():
                try:
                    # 데이터 준비
                    data = self._prepare_row_data(row, model_version, remarks)
                    
                    # UPSERT 쿼리 실행 (INSERT OR REPLACE)
                    upsert_query = """
                        INSERT OR REPLACE INTO ML_C (
                            입찰번호, 입찰차수, 기초금액률, 낙찰하한률, 기초금액,
                            순공사원가, 간접비, A계산여부, 순공사원가적용여부,
                            면허제한코드, 공고기관코드, 주공종명, 공고기관명, 공고기관점수,
                            공사지역, 공사지역점수, 키워드, 키워드점수,
                            공고일자, 개찰일시, 예측_URL, 업체투찰률_예측, 예가투찰률_예측,
                            참여업체수_예측, 예측일시
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    db_cmd.insert(upsert_query, data)
                    saved_count += 1
                    
                    if saved_count % 100 == 0:
                        print(f"진행률: {saved_count}/{total_rows} ({saved_count/total_rows*100:.1f}%)")
                
                except Exception as e:
                    print(f"⚠️  행 {index} 저장 실패: {e}")
                    continue
            
            print(f"✅ 데이터베이스 저장 완료: {saved_count}/{total_rows} 건")
            print("="*80)
            
            return saved_count
            
        except Exception as e:
            print(f"❌ 데이터베이스 저장 실패: {e}")
            raise e
    
    def _prepare_row_data(self, row, model_version, remarks):
        """행 데이터를 데이터베이스 저장 형식으로 준비"""
        from datetime import datetime
        
        # 현재 시간
        now = datetime.now()
        
        return (
            str(row.get('입찰번호', '')),
            str(row.get('입찰차수', '')),
            float(row.get('기초금액률', 0)),  # 새로 추가된 컬럼
            float(row.get('낙찰하한률', 0)),
            float(row.get('기초금액', 0)),
            float(row.get('순공사원가', 0)),
            float(row.get('간접비', 0)),
            str(row.get('A계산여부', '0')),  # A값여부 -> A계산여부
            str(row.get('순공사원가적용여부', '0')),  # 새로 추가된 컬럼
            str(row.get('면허제한코드', '')),
            str(row.get('공고기관코드', '')),
            str(row.get('주공종명', '')),  # 새로 추가된 컬럼
            str(row.get('공고기관명', '')),
            float(row.get('공고기관점수', 0)),
            str(row.get('공사지역', '')),
            float(row.get('공사지역점수', 0)),
            str(row.get('키워드', '')),
            float(row.get('키워드점수', 0)),
            row.get('공고일자', None),  # 새로 추가된 컬럼
            row.get('개찰일시', None),  # 새로 추가된 컬럼
            str(row.get('예측_URL', '')),  # 새로 추가된 컬럼
            float(row.get('업체투찰률_예측', 0)),  # 컬럼명 변경
            float(row.get('예가투찰률_예측', 0)),  # 컬럼명 변경
            int(row.get('참여업체수_예측', 0)),  # 컬럼명 변경
            now  # 예측일시
        )
    
    def get_prediction_results(self, limit=100, offset=0):
        """저장된 예측 결과 조회"""
        try:
            db_cmd = self.connection.command()
            query = """
                SELECT * FROM ML_C 
                ORDER BY 예측일시 DESC 
                LIMIT ? OFFSET ?
            """
            results = db_cmd.select(query, (limit, offset))
            return results
        except Exception as e:
            print(f"❌ 데이터 조회 실패: {e}")
            return None
    
    def get_prediction_count(self):
        """저장된 예측 결과 개수 조회"""
        try:
            db_cmd = self.connection.command()
            query = "SELECT COUNT(*) FROM ML_C"
            count = db_cmd.getValue(query, ())
            return count[0] if count else 0
        except Exception as e:
            print(f"❌ 데이터 개수 조회 실패: {e}")
            return 0
    
    def delete_old_predictions(self, days=30):
        """오래된 예측 결과 삭제 (기본 30일)"""
        try:
            db_cmd = self.connection.command()
            query = """
                DELETE FROM ML_C 
                WHERE 예측일시 < datetime('now', '-{} days')
            """.format(days)
            db_cmd.delete(query, ())
            print(f"✅ {days}일 이전 예측 결과 삭제 완료")
        except Exception as e:
            print(f"❌ 오래된 데이터 삭제 실패: {e}")
    
    def get_prediction_summary(self):
        """예측 결과 요약 통계 조회"""
        try:
            db_cmd = self.connection.command()
            query = """
                SELECT 
                    COUNT(*) as 총건수,
                    AVG(업체투찰률_예측) as 평균업체투찰률,
                    AVG(예가투찰률_예측) as 평균예가투찰률,
                    AVG(참여업체수_예측) as 평균참여업체수,
                    MIN(예측일시) as 최초예측일시,
                    MAX(예측일시) as 최근예측일시
                FROM ML_C
            """
            result = db_cmd.selectOne(query, ())
            return result
        except Exception as e:
            print(f"❌ 요약 통계 조회 실패: {e}")
            return None
    
    def save_prediction_with_options(self, result_df, model_version="v0.1.1", remarks="", 
                                   insert_mode="REPLACE"):
        """
        예측 결과를 다양한 옵션으로 저장
        
        Args:
            result_df (pd.DataFrame): 예측 결과 데이터프레임
            model_version (str): 모델 버전
            remarks (str): 비고
            insert_mode (str): 삽입 모드
                - "REPLACE": 기존 데이터가 있으면 교체 (UPSERT)
                - "IGNORE": 기존 데이터가 있으면 무시
                - "INSERT": 기존 데이터가 있으면 오류 발생
        """
        try:
            print("="*80)
            print(f"💾 예측 결과 저장 중... (모드: {insert_mode})")
            print("="*80)
            
            # 데이터베이스 명령 객체 가져오기
            db_cmd = self.connection.command()
            
            # 저장할 데이터 개수
            total_rows = len(result_df)
            saved_count = 0
            updated_count = 0
            ignored_count = 0
            
            # 각 행을 데이터베이스에 저장
            for index, row in result_df.iterrows():
                try:
                    # 데이터 준비
                    data = self._prepare_row_data(row, model_version, remarks)
                    
                    # 삽입 모드에 따른 쿼리 선택
                    if insert_mode == "REPLACE":
                        query = """
                            INSERT OR REPLACE INTO ML_C (
                                입찰번호, 입찰차수, 기초금액률, 낙찰하한률, 기초금액,
                                순공사원가, 간접비, A계산여부, 순공사원가적용여부,
                                면허제한코드, 공고기관코드, 주공종명, 공고기관명, 공고기관점수,
                                공사지역, 공사지역점수, 키워드, 키워드점수,
                                공고일자, 개찰일시, 예측_URL, 업체투찰률_예측, 예가투찰률_예측,
                                참여업체수_예측, 예측일시
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                    elif insert_mode == "IGNORE":
                        query = """
                            INSERT OR IGNORE INTO ML_C (
                                입찰번호, 입찰차수, 기초금액률, 낙찰하한률, 기초금액,
                                순공사원가, 간접비, A계산여부, 순공사원가적용여부,
                                면허제한코드, 공고기관코드, 주공종명, 공고기관명, 공고기관점수,
                                공사지역, 공사지역점수, 키워드, 키워드점수,
                                공고일자, 개찰일시, 예측_URL, 업체투찰률_예측, 예가투찰률_예측,
                                참여업체수_예측, 예측일시
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                    else:  # INSERT
                        query = """
                            INSERT INTO ML_C (
                                입찰번호, 입찰차수, 기초금액률, 낙찰하한률, 기초금액,
                                순공사원가, 간접비, A계산여부, 순공사원가적용여부,
                                면허제한코드, 공고기관코드, 주공종명, 공고기관명, 공고기관점수,
                                공사지역, 공사지역점수, 키워드, 키워드점수,
                                공고일자, 개찰일시, 예측_URL, 업체투찰률_예측, 예가투찰률_예측,
                                참여업체수_예측, 예측일시
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """
                    
                    # 기존 데이터 존재 여부 확인 (REPLACE 모드에서만)
                    if insert_mode == "REPLACE":
                        check_query = "SELECT COUNT(*) FROM ML_C WHERE 입찰번호 = ? AND 입찰차수 = ?"
                        existing = db_cmd.getValue(check_query, (str(row.get('입찰번호', '')), str(row.get('입찰차수', ''))))
                        if existing and existing[0] > 0:
                            updated_count += 1
                        else:
                            saved_count += 1
                    else:
                        saved_count += 1
                    
                    # 쿼리 실행
                    db_cmd.insert(query, data)
                    
                    if (saved_count + updated_count + ignored_count) % 100 == 0:
                        print(f"진행률: {saved_count + updated_count + ignored_count}/{total_rows} ({(saved_count + updated_count + ignored_count)/total_rows*100:.1f}%)")
                
                except Exception as e:
                    if insert_mode == "INSERT":
                        print(f"⚠️  행 {index} 저장 실패 (중복 데이터): {e}")
                        ignored_count += 1
                    else:
                        print(f"⚠️  행 {index} 저장 실패: {e}")
                        continue
            
            print(f"✅ 데이터베이스 저장 완료:")
            print(f"   - 새로 저장: {saved_count}건")
            if insert_mode == "REPLACE":
                print(f"   - 업데이트: {updated_count}건")
            print(f"   - 무시됨: {ignored_count}건")
            print("="*80)
            
            return saved_count + updated_count
            
        except Exception as e:
            print(f"❌ 데이터베이스 저장 실패: {e}")
            raise e
