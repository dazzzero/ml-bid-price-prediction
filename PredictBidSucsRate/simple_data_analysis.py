# -*- coding: utf-8 -*-
"""
간단한 데이터 품질 분석 스크립트
필수 패키지만 사용하여 데이터 상태 분석

@author: user
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def analyze_data_simple():
    """간단한 데이터 품질 분석"""
    print("🔍 간단한 데이터 품질 분석 시작...")
    
    # 데이터 파일 로드
    data_file = 'data/sample_prediction_data.csv'
    print(f"📁 데이터 파일 로드: {data_file}")
    
    try:
        # CSV 파일 읽기
        data = pd.read_csv(data_file, encoding='utf-8', header=0)
        print(f"✅ 데이터 로드 완료: {data.shape[0]}행, {data.shape[1]}열")
        
        # 기본 정보
        print(f"\n📊 기본 정보:")
        print(f"  - 총 행 수: {len(data):,}")
        print(f"  - 총 열 수: {len(data.columns)}")
        print(f"  - 메모리 사용량: {data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # 컬럼 정보
        print(f"\n📋 컬럼 목록:")
        for i, col in enumerate(data.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # 데이터 타입
        print(f"\n🔢 데이터 타입:")
        dtype_counts = data.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  - {dtype}: {count}개")
        
        # 결측값 분석
        print(f"\n❌ 결측값 분석:")
        missing_data = data.isnull().sum()
        total_missing = missing_data.sum()
        print(f"  - 총 결측값: {total_missing:,}개")
        print(f"  - 결측값 비율: {total_missing / (len(data) * len(data.columns)) * 100:.2f}%")
        
        if total_missing > 0:
            print(f"  - 결측값이 있는 컬럼들:")
            for col, count in missing_data[missing_data > 0].items():
                print(f"    * {col}: {count}개 ({count/len(data)*100:.2f}%)")
        
        # 숫자형 컬럼 통계
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print(f"\n📈 숫자형 컬럼 기본 통계:")
            stats_df = data[numeric_cols].describe()
            print(stats_df.round(4))
        
        # 이상치 분석 (간단한 방법)
        print(f"\n🚨 이상치 분석 (Z-score > 3):")
        outlier_summary = {}
        for col in numeric_cols:
            if col in data.columns and data[col].notna().sum() > 0:
                # Z-score 계산
                z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                outliers = z_scores > 3
                outlier_count = outliers.sum()
                outlier_percentage = (outlier_count / data[col].notna().sum()) * 100
                outlier_summary[col] = {'count': outlier_count, 'percentage': outlier_percentage}
                
                if outlier_count > 0:
                    print(f"  - {col}: {outlier_count}개 ({outlier_percentage:.2f}%)")
        
        # 타겟 변수 분석
        target_cols = ['업체투찰률', '예가투찰률', '참여업체수']
        print(f"\n🎯 타겟 변수 분석:")
        for col in target_cols:
            if col in data.columns:
                print(f"  - {col}:")
                print(f"    * 평균: {data[col].mean():.4f}")
                print(f"    * 중앙값: {data[col].median():.4f}")
                print(f"    * 표준편차: {data[col].std():.4f}")
                print(f"    * 최솟값: {data[col].min():.4f}")
                print(f"    * 최댓값: {data[col].max():.4f}")
                print(f"    * 결측값: {data[col].isnull().sum()}개")
                
                # 범위 검증
                if col in ['업체투찰률', '예가투찰률']:
                    invalid_range = ((data[col] < 0) | (data[col] > 1)).sum()
                    if invalid_range > 0:
                        print(f"    * ⚠️ 범위 초과 (0-1): {invalid_range}개")
        
        # 데이터 품질 개선 제안
        print(f"\n💡 데이터 품질 개선 제안:")
        
        # 결측값 처리 제안
        if total_missing > 0:
            print(f"\n1️⃣ 결측값 처리:")
            print(f"   - {total_missing}개의 결측값 발견")
            print(f"   - 권장: 평균값 또는 중앙값으로 대체")
        
        # 이상치 처리 제안
        total_outliers = sum([info['count'] for info in outlier_summary.values()])
        if total_outliers > 0:
            print(f"\n2️⃣ 이상치 처리:")
            print(f"   - {total_outliers}개의 이상치 발견")
            print(f"   - 권장: IQR 방법으로 제한 또는 제거")
        
        # 데이터 정규화 제안
        print(f"\n3️⃣ 데이터 정규화:")
        print(f"   - 권장: StandardScaler 또는 RobustScaler 사용")
        print(f"   - 이유: 서로 다른 스케일의 변수들을 동일한 범위로 조정")
        
        # 특성 선택 제안
        print(f"\n4️⃣ 특성 선택:")
        print(f"   - 상관관계가 높은 특성들 제거")
        print(f"   - 중요도가 낮은 특성들 제거")
        print(f"   - 도메인 지식 기반 특성 생성")
        
        return data, outlier_summary
        
    except Exception as e:
        print(f"❌ 데이터 분석 실패: {e}")
        return None, None

def suggest_quick_improvements(data):
    """빠른 데이터 개선 방안 제시"""
    print(f"\n🚀 빠른 데이터 개선 방안:")
    
    # 1. 결측값을 평균값으로 대체
    print(f"\n1️⃣ 결측값 처리 (평균값 대체):")
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if data[col].isnull().sum() > 0:
            mean_val = data[col].mean()
            data[col].fillna(mean_val, inplace=True)
            print(f"   - {col}: {data[col].isnull().sum()}개 → 0개")
    
    # 2. 이상치 제한 (IQR 방법)
    print(f"\n2️⃣ 이상치 제한 (IQR 방법):")
    for col in numeric_cols:
        Q1 = data[col].quantile(0.25)
        Q3 = data[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 이상치 개수 계산
        outliers_before = ((data[col] < lower_bound) | (data[col] > upper_bound)).sum()
        
        # 이상치 제한
        data[col] = data[col].clip(lower=lower_bound, upper=upper_bound)
        
        if outliers_before > 0:
            print(f"   - {col}: {outliers_before}개 이상치 제한")
    
    # 3. 타겟 변수 범위 정제
    print(f"\n3️⃣ 타겟 변수 범위 정제:")
    target_cols = ['업체투찰률', '예가투찰률', '참여업체수']
    for col in target_cols:
        if col in data.columns:
            if col in ['업체투찰률', '예가투찰률']:
                data[col] = data[col].clip(lower=0, upper=1)
                print(f"   - {col}: 0-1 범위로 제한")
            elif col == '참여업체수':
                data[col] = data[col].clip(lower=1)
                print(f"   - {col}: 1 이상으로 제한")
    
    return data

def main():
    """메인 함수"""
    print("🚀 간단한 데이터 품질 분석 시작")
    print("=" * 50)
    
    # 데이터 분석
    data, outlier_summary = analyze_data_simple()
    
    if data is not None:
        print(f"\n" + "=" * 50)
        print(f"🔧 빠른 개선 적용")
        print(f"=" * 50)
        
        # 빠른 개선 적용
        improved_data = suggest_quick_improvements(data.copy())
        
        # 개선된 데이터 저장
        output_file = 'data/bid_result_quick_improved.csv'
        improved_data.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n💾 개선된 데이터 저장: {output_file}")
        
        print(f"\n✅ 데이터 품질 분석 및 개선 완료!")
        print(f"다음 단계: 개선된 데이터로 모델 재학습")
    else:
        print(f"❌ 데이터 분석 실패")

if __name__ == "__main__":
    main()
