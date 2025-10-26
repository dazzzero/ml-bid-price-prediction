# -*- coding: utf-8 -*-
"""
예측 데이터의 값 범위를 검사하는 스크립트
"""

import os
import sys
import pandas as pd
import numpy as np
import math

# 데이터베이스 관련 import
sys.path.append(os.path.join(os.getcwd(), 'dac'))
from SqlServerPredictionManager import SqlServerPredictionManager


def check_data_ranges():
    """예측 데이터의 값 범위를 검사"""
    print("="*80)
    print("🔍 예측 데이터 값 범위 검사")
    print("="*80)
    
    # SQL Server 연결 설정
    db_config = {
        'host': '192.168.0.218',
        'port': 1433,
        'database': 'bips',
        'username': 'bips',
        'password': 'bips1!'
    }
    
    try:
        # 예측기 생성
        from predict_sample_data import SampleDataPredictor
        predictor = SampleDataPredictor(use_sql_server=True, db_config=db_config)
        
        # 데이터 전처리
        print("📁 데이터 로드 및 전처리 중...")
        processed_data = predictor.preprocess_data("sample_prediction_data.csv")
        
        # 예측 수행
        print("🔮 예측 수행 중...")
        predictions = predictor.predict_data(processed_data)
        
        print(f"✅ 데이터 처리 완료: {len(predictions)}행")
        print("="*80)
        
        # 각 컬럼의 값 범위 검사
        decimal_columns = {
            '기초금액률': (18, 9),      # DECIMAL(18, 9)
            '낙찰하한률': (10, 7),      # DECIMAL(10, 7)
            '기초금액': (20, 2),        # DECIMAL(20, 2)
            '순공사원가': (20, 2),       # DECIMAL(20, 2)
            '간접비': (20, 2),          # DECIMAL(20, 2)
            '공고기관점수': (21, 17),     # DECIMAL(10, 8)
            '공사지역점수': (21, 17),     # DECIMAL(12, 9)
            '키워드점수': (22, 17),       # DECIMAL(10, 8)
            '업체투찰률_예측': (18, 9),   # DECIMAL(18, 9)
            '예가투찰률_예측': (18, 9),   # DECIMAL(18, 9)
        }
        
        int_columns = {
            '참여업체수_예측': 'INT'
        }
        
        print("📊 DECIMAL 컬럼 값 범위 검사:")
        print("-" * 80)
        
        for col, (max_digits, decimal_places) in decimal_columns.items():
            if col in predictions.columns:
                values = predictions[col].dropna()
                
                if len(values) > 0:
                    min_val = values.min()
                    max_val = values.max()
                    mean_val = values.mean()
                    std_val = values.std()
                    
                    # DECIMAL 범위 계산
                    max_decimal_value = 10 ** (max_digits - decimal_places) - 1
                    min_decimal_value = -max_decimal_value
                    
                    # 범위 초과 여부 확인
                    overflow_min = min_val < min_decimal_value
                    overflow_max = max_val > max_decimal_value
                    
                    print(f"🔍 {col} (DECIMAL({max_digits},{decimal_places})):")
                    print(f"   범위: {min_decimal_value} ~ {max_decimal_value}")
                    print(f"   실제: {min_val:.9f} ~ {max_val:.9f}")
                    print(f"   평균: {mean_val:.9f}, 표준편차: {std_val:.9f}")
                    
                    # TF-IDF 점수 특별 처리
                    if col in ['공고기관점수', '공사지역점수', '키워드점수']:
                        print(f"   📊 TF-IDF 점수 상세 분석:")
                        print(f"   - 0에 가까운 값: {(values < 0.000001).sum()}개")
                        print(f"   - 1보다 큰 값: {(values > 1.0).sum()}개")
                        print(f"   - 10보다 큰 값: {(values > 10.0).sum()}개")
                        print(f"   - 100보다 큰 값: {(values > 100.0).sum()}개")
                        
                        # 극값들 출력
                        extreme_low = values[values < 0.000001].head(3)
                        extreme_high = values[values > 1.0].head(3)
                        
                        if len(extreme_low) > 0:
                            print(f"   - 극소값 예시: {extreme_low.tolist()}")
                        if len(extreme_high) > 0:
                            print(f"   - 극대값 예시: {extreme_high.tolist()}")
                    
                    if overflow_min or overflow_max:
                        print(f"   ❌ 범위 초과! (최소: {overflow_min}, 최대: {overflow_max})")
                        
                        # 범위 초과하는 값들 출력
                        if overflow_min:
                            overflow_values = values[values < min_decimal_value]
                            print(f"   범위 초과 (최소): {len(overflow_values)}개")
                            print(f"   예시: {overflow_values.head(3).tolist()}")
                        
                        if overflow_max:
                            overflow_values = values[values > max_decimal_value]
                            print(f"   범위 초과 (최대): {len(overflow_values)}개")
                            print(f"   예시: {overflow_values.head(3).tolist()}")
                    else:
                        print(f"   ✅ 범위 내 정상")
                    
                    print()
        
        print("📊 INT 컬럼 값 범위 검사:")
        print("-" * 80)
        
        for col, col_type in int_columns.items():
            if col in predictions.columns:
                values = predictions[col].dropna()
                
                if len(values) > 0:
                    min_val = int(values.min())
                    max_val = int(values.max())
                    
                    # INT 범위
                    int_min = -2147483648
                    int_max = 2147483647
                    
                    overflow_min = min_val < int_min
                    overflow_max = max_val > int_max
                    
                    print(f"🔍 {col} ({col_type}):")
                    print(f"   범위: {int_min} ~ {int_max}")
                    print(f"   실제: {min_val} ~ {max_val}")
                    
                    if overflow_min or overflow_max:
                        print(f"   ❌ 범위 초과! (최소: {overflow_min}, 최대: {overflow_max})")
                    else:
                        print(f"   ✅ 범위 내 정상")
                    
                    print()
        
        # 특이값 검사
        print("🔍 특이값 검사:")
        print("-" * 80)
        
        for col in predictions.select_dtypes(include=[np.number]).columns:
            values = predictions[col].dropna()
            
            if len(values) > 0:
                # NaN, 무한대 값 검사
                nan_count = values.isna().sum()
                inf_count = np.isinf(values).sum()
                
                if nan_count > 0:
                    print(f"❌ {col}: NaN 값 {nan_count}개 발견")
                
                if inf_count > 0:
                    print(f"❌ {col}: 무한대 값 {inf_count}개 발견")
                    inf_values = values[np.isinf(values)]
                    print(f"   예시: {inf_values.head(3).tolist()}")
        
        print("="*80)
        print("✅ 데이터 범위 검사 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_data_ranges()
