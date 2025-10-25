# -*- coding: utf-8 -*-
"""
고급 특성 엔지니어링 모듈
낙찰금액 예측 정확도 향상을 위한 고급 특성 생성

@author: user
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

class AdvancedFeatureEngineering:
    """
    고급 특성 엔지니어링 클래스
    기존 특성들을 조합하여 새로운 의미있는 특성들을 생성
    """
    
    def __init__(self):
        self.poly_features = None
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.pca = None
        self.kmeans = None
        
    def create_interaction_features(self, df):
        """
        특성 간 상호작용 특성 생성
        
        Args:
            df (DataFrame): 입력 데이터
            
        Returns:
            DataFrame: 상호작용 특성이 추가된 데이터
        """
        print("🔧 상호작용 특성 생성 중...")
        
        # 1. 금액 관련 상호작용 특성
        if '기초금액' in df.columns and '낙찰하한률' in df.columns:
            df['기초금액_낙찰하한률'] = df['기초금액'] * df['낙찰하한률']
            df['기초금액_제곱'] = df['기초금액'] ** 2
            df['낙찰하한률_제곱'] = df['낙찰하한률'] ** 2
            
        # 2. 참여업체수와 금액의 상호작용
        if '참여업체수' in df.columns and '기초금액' in df.columns:
            df['참여업체수_기초금액'] = df['참여업체수'] * df['기초금액']
            df['참여업체수_제곱'] = df['참여업체수'] ** 2
            
        # 3. 면허제한코드와 금액의 상호작용
        if '면허제한코드' in df.columns and '기초금액' in df.columns:
            df['면허제한코드_기초금액'] = df['면허제한코드'] * df['기초금액']
            
        # 4. 텍스트 점수들의 상호작용
        text_columns = ['공고기관점수', '공사지역점수', '키워드점수']
        for i, col1 in enumerate(text_columns):
            for col2 in text_columns[i+1:]:
                if col1 in df.columns and col2 in df.columns:
                    df[f'{col1}_{col2}'] = df[col1] * df[col2]
                    
        print(f"✅ 상호작용 특성 생성 완료: {len([col for col in df.columns if '_' in col])}개")
        return df
    
    def create_ratio_features(self, df):
        """
        비율 특성 생성
        
        Args:
            df (DataFrame): 입력 데이터
            
        Returns:
            DataFrame: 비율 특성이 추가된 데이터
        """
        print("🔧 비율 특성 생성 중...")
        
        # 1. 금액 비율 특성
        if '기초금액' in df.columns and '낙찰하한률' in df.columns:
            df['낙찰하한가_비율'] = df['기초금액'] * df['낙찰하한률'] / df['기초금액']
            
        # 2. 참여업체수 관련 비율
        if '참여업체수' in df.columns:
            df['참여업체수_로그'] = np.log1p(df['참여업체수'])  # 로그 변환
            
        # 3. 금액 로그 변환
        if '기초금액' in df.columns:
            df['기초금액_로그'] = np.log1p(df['기초금액'])
            
        print("✅ 비율 특성 생성 완료")
        return df
    
    def create_time_features(self, df):
        """
        시간 관련 특성 생성 (입찰번호에서 날짜 추출)
        
        Args:
            df (DataFrame): 입력 데이터
            
        Returns:
            DataFrame: 시간 특성이 추가된 데이터
        """
        print("🔧 시간 특성 생성 중...")
        
        if '입찰번호' in df.columns:
            # 입찰번호에서 날짜 패턴 추출 (예: 20241201 형태)
            def extract_date_from_bid_number(bid_number):
                try:
                    # 숫자만 추출
                    numbers = re.findall(r'\d+', str(bid_number))
                    for num in numbers:
                        if len(num) >= 8:  # YYYYMMDD 형태
                            year = int(num[:4])
                            month = int(num[4:6])
                            day = int(num[6:8])
                            if 2020 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                                return datetime(year, month, day)
                except:
                    pass
                return None
            
            df['입찰날짜'] = df['입찰번호'].apply(extract_date_from_bid_number)
            
            # 날짜가 추출된 경우에만 시간 특성 생성
            if df['입찰날짜'].notna().any():
                df['입찰년도'] = df['입찰날짜'].dt.year
                df['입찰월'] = df['입찰날짜'].dt.month
                df['입찰일'] = df['입찰날짜'].dt.day
                df['입찰요일'] = df['입찰날짜'].dt.dayofweek
                df['입찰분기'] = df['입찰날짜'].dt.quarter
                
                # 계절 특성
                df['계절'] = df['입찰월'].apply(lambda x: 
                    '봄' if x in [3,4,5] else
                    '여름' if x in [6,7,8] else
                    '가을' if x in [9,10,11] else '겨울')
                
                # 계절을 숫자로 변환
                season_map = {'봄': 1, '여름': 2, '가을': 3, '겨울': 4}
                df['계절_숫자'] = df['계절'].map(season_map)
                
        print("✅ 시간 특성 생성 완료")
        return df
    
    def create_clustering_features(self, df, n_clusters=5):
        """
        클러스터링 기반 특성 생성
        
        Args:
            df (DataFrame): 입력 데이터
            n_clusters (int): 클러스터 개수
            
        Returns:
            DataFrame: 클러스터 특성이 추가된 데이터
        """
        print(f"🔧 클러스터링 특성 생성 중... (클러스터 수: {n_clusters})")
        
        # 클러스터링에 사용할 특성들
        cluster_features = ['기초금액', '낙찰하한률', '참여업체수']
        available_features = [col for col in cluster_features if col in df.columns]
        
        if len(available_features) >= 2:
            # 결측값 처리
            cluster_data = df[available_features].fillna(df[available_features].mean())
            
            # 정규화
            cluster_data_scaled = self.scaler.fit_transform(cluster_data)
            
            # K-means 클러스터링
            self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            df['클러스터'] = self.kmeans.fit_predict(cluster_data_scaled)
            
            # 클러스터 중심까지의 거리
            distances = self.kmeans.transform(cluster_data_scaled)
            for i in range(n_clusters):
                df[f'클러스터_{i}_거리'] = distances[:, i]
                
        print("✅ 클러스터링 특성 생성 완료")
        return df
    
    def create_polynomial_features(self, df, degree=2):
        """
        다항식 특성 생성
        
        Args:
            df (DataFrame): 입력 데이터
            degree (int): 다항식 차수
            
        Returns:
            DataFrame: 다항식 특성이 추가된 데이터
        """
        print(f"🔧 다항식 특성 생성 중... (차수: {degree})")
        
        # 다항식 특성에 사용할 기본 특성들
        poly_features = ['기초금액', '낙찰하한률', '참여업체수']
        available_features = [col for col in poly_features if col in df.columns]
        
        if len(available_features) >= 2:
            # 결측값 처리
            poly_data = df[available_features].fillna(df[available_features].mean())
            
            # 다항식 특성 생성
            self.poly_features = PolynomialFeatures(degree=degree, include_bias=False)
            poly_data_transformed = self.poly_features.fit_transform(poly_data)
            
            # 새로운 특성명 생성
            feature_names = self.poly_features.get_feature_names_out(available_features)
            
            # 원본 특성 제외하고 추가
            for i, name in enumerate(feature_names):
                if name not in available_features:  # 원본 특성이 아닌 경우만
                    df[f'poly_{name}'] = poly_data_transformed[:, i]
                    
        print("✅ 다항식 특성 생성 완료")
        return df
    
    def create_categorical_features(self, df):
        """
        카테고리 특성 생성 (텍스트 데이터의 고급 특성)
        
        Args:
            df (DataFrame): 입력 데이터
            
        Returns:
            DataFrame: 카테고리 특성이 추가된 데이터
        """
        print("🔧 카테고리 특성 생성 중...")
        
        text_columns = ['키워드', '공고기관명', '공사지역']
        
        for col in text_columns:
            if col in df.columns:
                # 텍스트 길이
                df[f'{col}_길이'] = df[col].astype(str).str.len()
                
                # 단어 개수
                df[f'{col}_단어수'] = df[col].astype(str).str.split().str.len()
                
                # 특수문자 개수
                df[f'{col}_특수문자수'] = df[col].astype(str).str.count(r'[^가-힣a-zA-Z0-9\s]')
                
                # 숫자 개수
                df[f'{col}_숫자수'] = df[col].astype(str).str.count(r'\d')
                
                # 대문자 비율
                df[f'{col}_대문자비율'] = df[col].astype(str).str.count(r'[A-Z]') / df[f'{col}_길이'].replace(0, 1)
                
        print("✅ 카테고리 특성 생성 완료")
        return df
    
    def create_text_advanced_features(self, df):
        """
        텍스트 데이터의 고급 특성 생성
        
        Args:
            df (DataFrame): 입력 데이터
            
        Returns:
            DataFrame: 고급 텍스트 특성이 추가된 데이터
        """
        print("🔧 고급 텍스트 특성 생성 중...")
        
        text_columns = ['키워드', '공고기관명', '공사지역']
        
        for col in text_columns:
            if col in df.columns:
                # 텍스트 길이
                df[f'{col}_길이'] = df[col].astype(str).str.len()
                
                # 단어 개수
                df[f'{col}_단어수'] = df[col].astype(str).str.split().str.len()
                
                # 특수문자 개수
                df[f'{col}_특수문자수'] = df[col].astype(str).str.count(r'[^가-힣a-zA-Z0-9\s]')
                
                # 숫자 개수
                df[f'{col}_숫자수'] = df[col].astype(str).str.count(r'\d')
                
                # 대문자 비율
                df[f'{col}_대문자비율'] = df[col].astype(str).str.count(r'[A-Z]') / df[f'{col}_길이'].replace(0, 1)
                
        print("✅ 고급 텍스트 특성 생성 완료")
        return df
    
    def create_statistical_features(self, df):
        """
        통계적 특성 생성
        
        Args:
            df (DataFrame): 입력 데이터
            
        Returns:
            DataFrame: 통계적 특성이 추가된 데이터
        """
        print("🔧 통계적 특성 생성 중...")
        
        # 숫자형 컬럼들에 대한 통계 특성 생성
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in df.columns:
                # 평균과의 차이
                df[f'{col}_평균차이'] = df[col] - df[col].mean()
                
                # 표준편차로 나눈 값 (Z-score)
                if df[col].std() > 0:
                    df[f'{col}_zscore'] = (df[col] - df[col].mean()) / df[col].std()
                
                # 중앙값과의 차이
                df[f'{col}_중앙값차이'] = df[col] - df[col].median()
                
                # 사분위수 범위 내 위치
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                if q3 > q1:
                    df[f'{col}_iqr_위치'] = (df[col] - q1) / (q3 - q1)
                
        print("✅ 통계적 특성 생성 완료")
        return df
    
    def select_best_features(self, X, y, k=20, method='f_regression'):
        """
        최적 특성 선택
        
        Args:
            X (DataFrame): 입력 특성
            y (Series): 타겟 변수
            k (int): 선택할 특성 개수
            method (str): 선택 방법 ('f_regression' 또는 'mutual_info')
            
        Returns:
            DataFrame: 선택된 특성들
        """
        print(f"🔧 최적 특성 선택 중... (방법: {method}, 개수: {k})")
        
        # 결측값 처리
        X_clean = X.fillna(X.mean())
        
        # 특성 선택기 설정
        if method == 'f_regression':
            self.feature_selector = SelectKBest(score_func=f_regression, k=k)
        else:
            self.feature_selector = SelectKBest(score_func=mutual_info_regression, k=k)
        
        # 특성 선택 실행
        X_selected = self.feature_selector.fit_transform(X_clean, y)
        
        # 선택된 특성명 가져오기
        selected_features = X_clean.columns[self.feature_selector.get_support()].tolist()
        
        print(f"✅ 최적 특성 선택 완료: {len(selected_features)}개 특성 선택")
        print(f"선택된 특성: {selected_features}")
        
        return pd.DataFrame(X_selected, columns=selected_features)
    
    def apply_pca(self, X, n_components=0.95):
        """
        PCA를 적용하여 차원 축소
        
        Args:
            X (DataFrame): 입력 특성
            n_components (float): 설명 분산 비율
            
        Returns:
            DataFrame: PCA 변환된 특성들
        """
        print(f"🔧 PCA 적용 중... (설명 분산: {n_components})")
        
        # 결측값 처리
        X_clean = X.fillna(X.mean())
        
        # PCA 적용
        self.pca = PCA(n_components=n_components)
        X_pca = self.pca.fit_transform(X_clean)
        
        # 새로운 특성명 생성
        pca_columns = [f'PC{i+1}' for i in range(X_pca.shape[1])]
        
        print(f"✅ PCA 완료: {X_pca.shape[1]}개 주성분 생성")
        print(f"설명 분산 비율: {self.pca.explained_variance_ratio_.sum():.3f}")
        
        return pd.DataFrame(X_pca, columns=pca_columns)
    
    def create_all_features(self, df, target_column='업체투찰률'):
        """
        모든 고급 특성을 한번에 생성
        
        Args:
            df (DataFrame): 입력 데이터
            target_column (str): 타겟 변수명
            
        Returns:
            DataFrame: 모든 특성이 추가된 데이터
        """
        print("🚀 고급 특성 엔지니어링 시작...")
        
        # 1. 기본 특성 생성
        df = self.create_interaction_features(df)
        df = self.create_ratio_features(df)
        df = self.create_categorical_features(df)
        df = self.create_statistical_features(df)
        df = self.create_time_features(df)
        df = self.create_text_advanced_features(df)
        
        # 2. 클러스터링 특성 생성
        df = self.create_clustering_features(df)
        
        # 3. 다항식 특성 생성
        df = self.create_polynomial_features(df)
        
        print(f"✅ 고급 특성 엔지니어링 완료!")
        print(f"총 특성 개수: {len(df.columns)}개")
        
        return df

# 사용 예시
if __name__ == "__main__":
    # 예시 데이터로 테스트
    sample_data = {
        '기초금액': [100000000, 200000000, 150000000],
        '낙찰하한률': [0.85, 0.87, 0.86],
        '참여업체수': [5, 8, 6],
        '면허제한코드': [6000, 7000, 6500],
        '공고기관점수': [0.5, 0.7, 0.6],
        '공사지역점수': [0.3, 0.4, 0.35],
        '키워드점수': [0.2, 0.3, 0.25],
        '입찰번호': ['20241201001', '20241202002', '20241203003'],
        '키워드': ['건물 신축공사', '도로 포장공사', '교량 건설공사'],
        '공고기관명': ['서울시청', '부산시청', '대구시청'],
        '공사지역': ['서울시', '부산시', '대구시']
    }
    
    df = pd.DataFrame(sample_data)
    
    # 고급 특성 엔지니어링 적용
    feature_engineer = AdvancedFeatureEngineering()
    df_enhanced = feature_engineer.create_all_features(df)
    
    print("\n📊 특성 엔지니어링 결과:")
    print(f"원본 특성: {len(sample_data)}개")
    print(f"향상된 특성: {len(df_enhanced.columns)}개")
    print(f"새로 추가된 특성: {len(df_enhanced.columns) - len(sample_data)}개")

