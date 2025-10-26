# -*- coding: utf-8 -*-
"""
예측 결과 데이터베이스 조회 및 관리 스크립트
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 데이터베이스 관련 import
sys.path.append(os.path.join(os.getcwd(), 'dac'))
from PredictionResultManager import PredictionResultManager


class PredictionResultQuery:
    """예측 결과 조회 및 관리 클래스"""
    
    def __init__(self):
        try:
            self.db_manager = PredictionResultManager()
            print("✅ 데이터베이스 연결 완료")
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            sys.exit(1)
    
    def show_summary(self):
        """예측 결과 요약 통계 출력"""
        print("="*80)
        print("📊 예측 결과 요약 통계")
        print("="*80)
        
        summary = self.db_manager.get_prediction_summary()
        if summary:
            print(f"총 저장 건수: {summary[0]:,}건")
            print(f"평균 업체투찰률: {summary[1]:.3f}")
            print(f"평균 예가투찰률: {summary[2]:.3f}")
            print(f"평균 참여업체수: {summary[3]:.1f}")
            print(f"최초 예측일시: {summary[4]}")
            print(f"최근 예측일시: {summary[5]}")
        else:
            print("저장된 데이터가 없습니다.")
        print("="*80)
    
    def show_recent_predictions(self, limit=10):
        """최근 예측 결과 조회"""
        print("="*80)
        print(f"📋 최근 {limit}건 예측 결과")
        print("="*80)
        
        results = self.db_manager.get_prediction_results(limit=limit)
        if results:
            # 컬럼명 정의 (ML_CST 테이블 구조에 맞춤)
            columns = [
                '입찰번호', '입찰차수', '기초금액률', '낙찰하한률', '기초금액', '순공사원가',
                '간접비', 'A계산여부', '순공사원가적용여부', '면허제한코드', '공고기관코드',
                '주공종명', '공고기관명', '공고기관점수', '공사지역', '공사지역점수',
                '키워드', '키워드점수', '공고일자', '개찰일시', '예측_URL',
                '업체투찰률_예측', '예가투찰률_예측', '참여업체수_예측',
                '등록일시', '예측일시'
            ]
            
            df = pd.DataFrame(results, columns=columns)
            
            # 주요 컬럼만 선택하여 출력
            display_columns = ['입찰번호', '입찰차수', '기초금액', '업체투찰률_예측', 
                             '예가투찰률_예측', '참여업체수_예측', 'A계산여부', '예측일시']
            
            available_columns = [col for col in display_columns if col in df.columns]
            print(df[available_columns].to_string(index=False))
        else:
            print("저장된 데이터가 없습니다.")
        print("="*80)
    
    def export_to_excel(self, output_file=None, limit=1000):
        """예측 결과를 엑셀 파일로 내보내기"""
        if not output_file:
            output_file = f"prediction_results_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        print("="*80)
        print(f"📤 예측 결과 내보내기 중... (최대 {limit}건)")
        print("="*80)
        
        results = self.db_manager.get_prediction_results(limit=limit)
        if results:
            # 컬럼명 정의 (ML_CST 테이블 구조에 맞춤)
            columns = [
                '입찰번호', '입찰차수', '기초금액률', '낙찰하한률', '기초금액', '순공사원가',
                '간접비', 'A계산여부', '순공사원가적용여부', '면허제한코드', '공고기관코드',
                '주공종명', '공고기관명', '공고기관점수', '공사지역', '공사지역점수',
                '키워드', '키워드점수', '공고일자', '개찰일시', '예측_URL',
                '업체투찰률_예측', '예가투찰률_예측', '참여업체수_예측',
                '등록일시', '예측일시'
            ]
            
            df = pd.DataFrame(results, columns=columns)
            
            # 엑셀 파일로 저장
            output_path = os.path.join('res', 'predict_result', output_file)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            df.to_excel(
                output_path,
                sheet_name='예측결과',
                na_rep='NaN',
                float_format="%.6f",
                header=True,
                index=False,
                freeze_panes=(1, 0)
            )
            
            print(f"✅ 내보내기 완료: {output_path}")
            print(f"📊 내보낸 데이터: {len(df)}건")
        else:
            print("저장된 데이터가 없습니다.")
        print("="*80)
    
    def delete_old_data(self, days=30):
        """오래된 데이터 삭제"""
        print("="*80)
        print(f"🗑️  {days}일 이전 데이터 삭제 중...")
        print("="*80)
        
        # 삭제 전 현재 데이터 개수 확인
        before_count = self.db_manager.get_prediction_count()
        print(f"삭제 전 데이터 개수: {before_count:,}건")
        
        # 데이터 삭제
        self.db_manager.delete_old_predictions(days)
        
        # 삭제 후 데이터 개수 확인
        after_count = self.db_manager.get_prediction_count()
        deleted_count = before_count - after_count
        
        print(f"삭제 후 데이터 개수: {after_count:,}건")
        print(f"삭제된 데이터: {deleted_count:,}건")
        print("="*80)
    
    def search_by_bid_number(self, bid_number):
        """입찰번호로 검색"""
        print("="*80)
        print(f"🔍 입찰번호 '{bid_number}' 검색 결과")
        print("="*80)
        
        try:
            db_cmd = self.db_manager.connection.command()
            query = "SELECT * FROM ML_C WHERE 입찰번호 LIKE ? ORDER BY 예측일시 DESC"
            results = db_cmd.select(query, (f'%{bid_number}%',))
            
            if results:
                columns = [
                    '입찰번호', '입찰차수', '기초금액률', '낙찰하한률', '기초금액', '순공사원가',
                    '간접비', 'A계산여부', '순공사원가적용여부', '면허제한코드', '공고기관코드',
                    '주공종명', '공고기관명', '공고기관점수', '공사지역', '공사지역점수',
                    '키워드', '키워드점수', '공고일자', '개찰일시', '예측_URL',
                    '업체투찰률_예측', '예가투찰률_예측', '참여업체수_예측',
                    '등록일시', '예측일시'
                ]
                
                df = pd.DataFrame(results, columns=columns)
                print(df.to_string(index=False))
            else:
                print("검색 결과가 없습니다.")
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
        print("="*80)


def main():
    """메인 실행 함수"""
    print("="*80)
    print("🔍 예측 결과 조회 및 관리 시스템")
    print("="*80)
    
    try:
        query_manager = PredictionResultQuery()
        
        while True:
            print("\n📋 메뉴를 선택하세요:")
            print("1. 요약 통계 보기")
            print("2. 최근 예측 결과 보기")
            print("3. 엑셀 파일로 내보내기")
            print("4. 입찰번호로 검색")
            print("5. 오래된 데이터 삭제")
            print("0. 종료")
            
            choice = input("\n선택: ").strip()
            
            if choice == '1':
                query_manager.show_summary()
            elif choice == '2':
                limit = input("조회할 건수 (기본 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                query_manager.show_recent_predictions(limit)
            elif choice == '3':
                limit = input("내보낼 건수 (기본 1000): ").strip()
                limit = int(limit) if limit.isdigit() else 1000
                query_manager.export_to_excel(limit=limit)
            elif choice == '4':
                bid_number = input("검색할 입찰번호: ").strip()
                if bid_number:
                    query_manager.search_by_bid_number(bid_number)
            elif choice == '5':
                days = input("삭제할 일수 (기본 30): ").strip()
                days = int(days) if days.isdigit() else 30
                confirm = input(f"{days}일 이전 데이터를 삭제하시겠습니까? (y/N): ").strip().lower()
                if confirm == 'y':
                    query_manager.delete_old_data(days)
            elif choice == '0':
                print("프로그램을 종료합니다.")
                break
            else:
                print("잘못된 선택입니다.")
    
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
