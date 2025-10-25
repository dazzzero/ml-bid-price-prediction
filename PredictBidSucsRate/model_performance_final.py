# -*- coding: utf-8 -*-
"""
현재 모델의 성능을 정확히 측정하는 최종 스크립트
"""

import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import sys

def clean_numeric_data(series):
    """
    숫자 데이터를 정리하는 함수
    - 쉼표 제거
    - 문자열을 숫자로 변환
    - 변환 불가능한 값은 0으로 대체
    """
    if series.dtype == 'object':
        # 쉼표 제거하고 숫자로 변환
        cleaned = series.astype(str).str.replace(',', '').str.replace(' ', '')
        # 숫자로 변환 시도
        numeric_series = pd.to_numeric(cleaned, errors='coerce')
        # NaN 값을 0으로 대체
        return numeric_series.fillna(0)
    else:
        return series

def test_model_performance():
    print("="*80)
    print("현재 모델 성능 분석 시작")
    print("="*80)
    
    try:
        # 데이터 로드 (처음 1000개 샘플)
        print("데이터 로드 중...")
        data = pd.read_csv('data/bid_250921_30.csv', nrows=1000)
        print(f"데이터 로드 성공: {data.shape}")
        
        # 올바른 특성 컬럼 선택
        feature_columns = ['기초금액', '낙찰하한률', '참여업체수', 'A계산여부', '순공사원가적용여부', 
                          '면허제한코드', '공고기관점수', '공사지역점수', '키워드점수']
        
        # 존재하는 컬럼만 선택
        available_features = [col for col in feature_columns if col in data.columns]
        missing_features = [col for col in feature_columns if col not in data.columns]
        
        print(f"\n사용 가능한 특성 ({len(available_features)}개):")
        for col in available_features:
            print(f"  - {col}")
            
        if missing_features:
            print(f"\n누락된 특성 ({len(missing_features)}개):")
            for col in missing_features:
                print(f"  - {col}")
        
        # 특성과 타겟 분리
        X = data[available_features].copy()
        y1 = data['업체투찰률']
        y2 = data['예가투찰률'] 
        y3 = data['참여업체수']
        
        print(f"\n데이터 정보:")
        print(f"  특성 수: {X.shape[1]}")
        print(f"  샘플 수: {X.shape[0]}")
        print(f"  타겟 변수: 업체투찰률, 예가투찰률, 참여업체수")
        
        # 데이터 전처리 (문자열을 숫자로 변환)
        print(f"\n데이터 전처리 중...")
        print("  - 문자열 데이터를 숫자로 변환 중...")
        
        # 각 특성 컬럼을 정리
        for col in X.columns:
            print(f"    {col} 컬럼 처리 중...")
            X[col] = clean_numeric_data(X[col])
        
        # 타겟 변수도 정리
        y1 = clean_numeric_data(y1)
        y2 = clean_numeric_data(y2)
        y3 = clean_numeric_data(y3)
        
        # NaN 값 처리
        X = X.fillna(0)
        y1 = y1.fillna(0)
        y2 = y2.fillna(0)
        y3 = y3.fillna(0)
        
        print("  - 데이터 전처리 완료")
        
        # 데이터 타입 확인
        print(f"\n전처리 후 데이터 타입:")
        for col in X.columns:
            print(f"  {col}: {X[col].dtype}")
        
        # 모델 로드 및 성능 평가
        print(f"\n모델 성능 평가:")
        print("-"*60)
        
        models = {
            '업체투찰률': ('res/mlpregr.model1.v0.1.1.npz', y1),
            '예가투찰률': ('res/mlpregr.model2.v0.1.1.npz', y2),
            '참여업체수': ('res/mlpregr.model3.v0.1.1.npz', y3)
        }
        
        performance_results = {}
        
        for name, (file_path, y) in models.items():
            try:
                print(f"\n{name} 모델 로드 중...")
                model = joblib.load(file_path)
                print(f"{name} 모델 로드 성공")
                
                print(f"{name} 모델 예측 중...")
                # numpy 배열로 변환하여 예측
                X_array = X.values.astype(np.float64)
                y_pred = model.predict(X_array)
                print(f"{name} 모델 예측 완료")
                
                # 성능 지표 계산
                mse = mean_squared_error(y, y_pred)
                r2 = r2_score(y, y_pred)
                mae = mean_absolute_error(y, y_pred)
                rmse = np.sqrt(mse)
                
                performance_results[name] = {
                    'MSE': mse,
                    'R2': r2,
                    'MAE': mae,
                    'RMSE': rmse
                }
                
                print(f"\n{name} 모델 성능:")
                print(f"  MSE:  {mse:.6f}")
                print(f"  R2:   {r2:.6f}")
                print(f"  MAE:  {mae:.6f}")
                print(f"  RMSE: {rmse:.6f}")
                
                # 성능 해석
                if r2 > 0.8:
                    r2_interpretation = "매우 좋음"
                elif r2 > 0.6:
                    r2_interpretation = "좋음"
                elif r2 > 0.4:
                    r2_interpretation = "보통"
                else:
                    r2_interpretation = "개선 필요"
                
                print(f"  해석: R2 = {r2:.3f} ({r2_interpretation})")
                
            except Exception as e:
                print(f"ERROR: {name} 모델 오류: {e}")
                import traceback
                traceback.print_exc()
        
        # 전체 성능 요약
        if performance_results:
            print(f"\n" + "="*80)
            print("전체 성능 요약")
            print("="*80)
            
            for name, metrics in performance_results.items():
                print(f"{name:>12}: R2={metrics['R2']:.3f}, RMSE={metrics['RMSE']:.3f}")
            
            # 평균 성능 계산
            avg_r2 = np.mean([metrics['R2'] for metrics in performance_results.values()])
            avg_rmse = np.mean([metrics['RMSE'] for metrics in performance_results.values()])
            
            print(f"\n평균 성능:")
            print(f"  평균 R2:   {avg_r2:.3f}")
            print(f"  평균 RMSE: {avg_rmse:.3f}")
            
            # 성능 기준선 설정
            print(f"\n성능 기준선:")
            if avg_r2 > 0.7:
                print("  현재 성능: 우수 (R2 > 0.7)")
                print("  개선 목표: R2 > 0.8")
            elif avg_r2 > 0.5:
                print("  현재 성능: 보통 (R2 > 0.5)")
                print("  개선 목표: R2 > 0.7")
            else:
                print("  현재 성능: 개선 필요 (R2 < 0.5)")
                print("  개선 목표: R2 > 0.6")
        
        print("="*80)
        print("모델 성능 분석 완료")
        print("="*80)
        
    except Exception as e:
        print(f"ERROR: 전체 프로세스 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_performance()







