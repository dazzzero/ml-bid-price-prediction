# -*- coding: utf-8 -*-
"""
입찰 성공률 예측 시스템 - 예측 API 서버
Created on Fri Dec  6 10:20:06 2024

@author: user

이 파일의 목적:
- 조달청 입찰 데이터를 기반으로 머신러닝 모델을 사용하여 입찰 성공률을 예측하는 웹 API 서버
- Flask 웹 프레임워크를 사용하여 REST API 제공
- 실시간으로 입찰 정보를 입력받아 투찰률과 낙찰가를 예측
"""

# ===== 필요한 라이브러리들 import =====
import os  # 파일 경로 조작을 위한 라이브러리
import joblib  # 머신러닝 모델을 파일로 저장/불러오기 위한 라이브러리
import pandas as pd  # 데이터 분석을 위한 라이브러리 (엑셀과 비슷한 기능)
import sklearn  # 머신러닝 라이브러리
import random as rnd  # 랜덤 숫자 생성
import numpy as np  # 수치 계산을 위한 라이브러리 (행렬, 배열 연산)

# 한국어 자연어 처리를 위한 라이브러리
from kiwipiepy import Kiwi  # 한국어 형태소 분석기 (단어를 쪼개는 도구)

# 텍스트를 숫자로 변환하는 도구들
from sklearn.feature_extraction.text import TfidfVectorizer  # 텍스트를 숫자로 변환
from scipy.sparse import csr_matrix  # 메모리 효율적인 행렬 저장 방식

# 데이터 전처리 도구
from sklearn.preprocessing import StandardScaler  # 데이터를 정규화하는 도구 (0~1 사이로 맞춤)

# 머신러닝 모델들
#from sklearn.linear_model import LinearRegression  # 선형 회귀 모델 (주석처리됨)
from sklearn.neural_network import MLPRegressor  # 인공신경망 모델 (뇌의 뉴런처럼 작동)

# 웹 서버 구축을 위한 라이브러리
from flask import Flask, jsonify, g, request  # Flask: 웹 서버 만들기, jsonify: JSON 응답, g: 전역변수, request: 요청받기

# 고급 특성 엔지니어링
from advanced_feature_engineering import AdvancedFeatureEngineering


class KiwiTokenizer():
    """
    한국어 텍스트를 처리하는 클래스
    
    이 클래스의 역할:
    1. 한국어 문장을 단어 단위로 쪼개기 (형태소 분석)
    2. 의미있는 단어만 추출하기 (명사, 형용사 등)
    3. 불필요한 문자 제거하기 (괄호, 특수문자 등)
    
    예시: "서울시청 건물 신축공사" → ["서울시청", "건물", "신축", "공사"]
    """
    
    def __init__(self, saved_filenm):
        """
        KiwiTokenizer 초기화 함수
        
        Args:
            saved_filenm (str): 저장된 사전 파일명 (이전에 학습한 단어사전을 불러올 때 사용)
        """
        # 랜덤 번호 생성 (파일명에 사용)
        self.rnd_num = rnd.randint(100, 999)
        
        # 현재 작업 디렉토리 경로 설정
        self.cur_dir = os.getcwd()  # 현재 폴더 경로 가져오기
        self.data_dir = self.cur_dir+'\\data\\'  # 데이터 폴더 경로 (입찰 데이터가 있는 곳)
        
        # 결과 저장 폴더 경로 설정
        self.save_dir = self.cur_dir+'\\res\\'  # 결과 저장 폴더 (모델 파일들이 있는 곳)
        self.save_filename = saved_filenm  # 저장할 파일명
        
        # Kiwi 형태소 분석기 초기화
        self.kiwi = None
        self.kiwi = self.CreateKiwi(saved_filenm)  # Kiwi 객체 생성
    
    def save(self, filename):
        """
        학습된 단어사전을 파일로 저장하는 함수
        
        Args:
            filename (str): 저장할 파일명
            
        Returns:
            self: 자기 자신을 반환 (메서드 체이닝을 위해)
        """
        # Kiwi의 사용자 정의 단어사전을 파일로 저장
        joblib.dump(self.kiwi._user_values, self.save_dir+filename)
        return self
    
    def load(self, filename):
        """
        저장된 단어사전을 파일에서 불러오는 함수
        
        Args:
            filename (str): 불러올 파일명
            
        Returns:
            dict: 불러온 단어사전 데이터
        """
        # 저장된 단어사전 파일을 불러오기
        o = joblib.load(self.save_dir+filename)
        return o
        
    def loadDictonary(self, filename):
        """
        표준국어대사전을 불러와서 Kiwi에 추가하는 함수
        
        Args:
            filename (str): 표준국어대사전 CSV 파일명
        """
        # 표준국어대사전 CSV 파일 읽기
        self.data = pd.read_csv(self.data_dir+filename)   # 표준국어대사전.NNP.csv
        print("표준국어대사전 데이터 미리보기:")
        print(self.data[:10])  # 처음 10개 행 출력
        
        # 각 단어를 Kiwi에 고유명사(NNP)로 추가
        for i, row in enumerate(self.data.iloc):
            #print(i, row["단어"])  # 디버깅용 (주석처리)
            self.kiwi.add_user_word(row["단어"], 'NNP')  # 고유명사로 단어 추가
    
    def CreateKiwi(self, saved_filenm):
        """
        Kiwi 형태소 분석기 객체를 생성하는 함수
        
        Args:
            saved_filenm (str): 저장된 사전 파일명 (None이면 새로 생성)
            
        Returns:
            Kiwi: 형태소 분석기 객체
        """
        o = None
        if(self.kiwi is None):  # 아직 Kiwi가 생성되지 않았다면
            if(saved_filenm is None):
                # 새로운 Kiwi 객체 생성 (8개 스레드 사용)
                o = Kiwi(num_workers=8)
            else:
                # 기존에 저장된 사전이 있다면 불러와서 사용
                o = Kiwi(num_workers=8)
                o._user_values = self.load(saved_filenm)  # 저장된 단어사전 불러오기
                #o.load_user_dictionary(self.save_dir+saved_filenm)  # 다른 방식 (주석처리)
        
        return o
            
    def cleared_line(self, line):
        """
        한 줄의 텍스트를 정리하고 의미있는 단어만 추출하는 함수
        
        Args:
            line (str): 처리할 텍스트 한 줄
            
        Returns:
            str: 정리된 단어들을 공백으로 연결한 문자열
            
        예시: "서울시청(본관) 건물 신축공사" → "서울시청 건물 신축 공사"
        """
        # numpy.float64나 NaN 값 처리
        if pd.isna(line) or line is None:
            line = ''
        else:
            line = str(line).lower().replace('(', ' ').replace(')', ' ').replace('n/a', '')
        
        nm_words = []  # 의미있는 단어들을 저장할 리스트
        tokens = self.kiwi.tokenize(line)  # 형태소 분석 실행
        
        # 각 토큰(단어 조각)을 검사하여 의미있는 단어만 추출
        for token in tokens:
            # 다음 품사 태그들만 선택 (의미있는 단어들)
            # MM: 관형사, NNG: 일반명사, NNB: 의존명사, NNP: 고유명사
            # SL: 외국어, XPN: 접두사, MAG: 일반부사, SN: 숫자
            # SO: 기호, W_SERIAL: 연속된 문자
            if token.tag in ['MM', 'NNG', 'NNB', 'NNP', 'SL', 'XPN', 'MAG', 'SN', 'SO', 'W_SERIAL']:
                nm_words.append(token.form)  # 단어 형태 추가
                
        return ' '.join(nm_words)  # 단어들을 공백으로 연결하여 반환
    
    def cleared_lines_from(self, orglines):
        """
        여러 줄의 텍스트를 한번에 처리하는 함수
        
        Args:
            orglines (list): 처리할 텍스트 리스트
            
        Returns:
            list: 정리된 텍스트 리스트
        """
        lines = []
        for line in orglines:
            lines.append(self.cleared_line(line))  # 각 줄을 개별적으로 처리
        
        return lines      
    
    def get_key(self, voca, val):
        """
        사전에서 값에 해당하는 키를 찾는 함수
        
        Args:
            voca (dict): 검색할 사전
            val: 찾을 값
            
        Returns:
            str: 찾은 키 또는 "key doesn't exist"
        """
        # 사전의 모든 항목을 검사
        for key, value in voca.items():
            if val == value:
                return key  # 값이 일치하는 키 반환
    
        return "key doesn't exist"  # 찾지 못한 경우
    
    def conv_words(self, voca, vals):
        """
        값 리스트를 해당하는 키 리스트로 변환하는 함수
        
        Args:
            voca (dict): 변환할 사전
            vals (list): 변환할 값들의 리스트
            
        Returns:
            str: 변환된 키들을 공백으로 연결한 문자열
        """
        ret = []
        for val in vals:  # 각 값에 대해
            for key, value in voca.items():  # 사전에서 검색
                if val == value:
                    ret.append(key)  # 일치하는 키 추가
            
        return " ".join(ret)  # 키들을 공백으로 연결하여 반환
    
    
    def nn_only(self, orglines):
        """
        텍스트 리스트에서 명사류만 추출하는 함수 (cleared_line과 동일한 기능)
        
        Args:
            orglines (list): 처리할 텍스트 리스트
            
        Returns:
            list: 명사류만 추출된 텍스트 리스트
        """
        lines = []
        for key in orglines:
            # numpy.float64나 NaN 값 처리
            if pd.isna(key) or key is None:
                key = ''
            else:
                key = str(key).lower().replace('(', ' ').replace(')', ' ').replace('n/a', '')
            
            nm_words = []
            tokens = self.kiwi.tokenize(key)  # 형태소 분석
            #print(key, tokens)  # 디버깅용 (주석처리)
            
            # 의미있는 단어만 추출
            for token in tokens:
                if token.tag in ['MM', 'NNG', 'NNB', 'NNP', 'SL', 'XPN', 'MAG', 'SN', 'SO', 'W_SERIAL']:
                    nm_words.append(token.form)
            lines.append(' '.join(nm_words))  # 단어들을 공백으로 연결
            
        return lines


class KiwiVectorizer():
    """
    텍스트를 숫자로 변환하는 클래스 (TF-IDF 벡터화)
    
    이 클래스의 역할:
    1. 텍스트를 숫자로 변환하여 머신러닝 모델이 이해할 수 있게 만들기
    2. TF-IDF 방식 사용 (단어의 중요도를 계산하는 방법)
    3. 단어사전을 저장하고 불러오기
    
    TF-IDF란? 
    - Term Frequency-Inverse Document Frequency
    - 자주 나오는 단어일수록 높은 점수를 주되, 모든 문서에 자주 나오는 단어는 낮은 점수를 주는 방식
    """
    
    def __init__(self):
        """
        KiwiVectorizer 초기화 함수
        """
        # 랜덤 번호 생성
        self.rnd_num = rnd.randint(100, 999)
        
        # 디렉토리 경로 설정
        self.cur_dir = os.getcwd()  # 현재 작업 디렉토리
        self.data_dir = self.cur_dir+'\\data\\'  # 데이터 폴더
        self.save_dir = self.cur_dir+'\\res\\'  # 결과 저장 폴더
        
        # 메모리 효율성을 위해 파라미터 최적화
        self.vect = TfidfVectorizer(
            ngram_range=(1, 1), 
            token_pattern='(?u)\\b\\w+\\b',
            max_features=5000,  # 최대 특성 수 제한
            min_df=2,           # 최소 문서 빈도 (2회 이상 나타나는 단어만)
            max_df=0.95,        # 최대 문서 빈도 (95% 이상 문서에 나타나는 단어 제외)
            sublinear_tf=True   # TF 스케일링으로 메모리 절약
        )
    
    def load(self, filename):
        """
        저장된 단어사전과 IDF 값을 불러오는 함수
        
        Args:
            filename (str): 불러올 파일명
        """
        # 저장된 단어사전 파일 불러오기
        voca = joblib.load(self.save_dir + filename)
        self.vect.vocabulary_ = voca["vocabulary"]  # 단어사전 설정
        self.vect.idf_ = voca["idf"]  # IDF 값 설정
    
    def save(self, filename):
        """
        학습된 단어사전과 IDF 값을 파일로 저장하는 함수
        
        Args:
            filename (str): 저장할 파일명
        """
        # 단어사전과 IDF 값을 딕셔너리로 묶어서 저장
        joblib.dump({'vocabulary':self.vect.vocabulary_, 'idf':self.vect.idf_}, self.save_dir + filename)
        print("단어사전 파일("+filename+")로 저장합니다. ")
    
    def fit(self, lines):
        """
        텍스트 데이터로부터 단어사전을 학습하는 함수
        
        Args:
            lines (list): 학습할 텍스트 리스트
            
        Returns:
            TfidfVectorizer: 학습된 벡터화기
        """
        return self.vect.fit(lines)  # TF-IDF 벡터화기 학습
    
    def transform(self, lines):
        """
        텍스트를 숫자 벡터로 변환하는 함수
        
        Args:
            lines (list): 변환할 텍스트 리스트
            
        Returns:
            csr_matrix: 변환된 희소 행렬 (메모리 효율적인 행렬 형태)
        """
        # 메모리 효율성을 위해 toarray() 없이 CSR 행렬 그대로 반환
        return self.vect.transform(lines)
    
    def scores(self, lines):
        """
        텍스트의 TF-IDF 점수를 계산하는 함수
        
        Args:
            lines (list): 점수를 계산할 텍스트 리스트
            
        Returns:
            list: 각 텍스트의 TF-IDF 점수 리스트
        """
        return self.toValues(self.transform(lines))  # 변환 후 점수 계산

    def score(self, line):
        """
        단일 텍스트의 TF-IDF 점수를 계산하는 함수
        
        Args:
            line (str): 점수를 계산할 텍스트
            
        Returns:
            float: 텍스트의 TF-IDF 점수
        """
        return self.toValues(self.transform([line]))[0]  # 리스트로 변환 후 첫 번째 값 반환

    def toValues(self, csrmat:csr_matrix):
        """
        희소 행렬을 일반 숫자 리스트로 변환하는 함수
        
        Args:
            csrmat (csr_matrix): 변환할 희소 행렬
            
        Returns:
            list: 변환된 숫자 리스트
            
        설명:
        - CSR(Compressed Sparse Row) 행렬은 0이 많은 행렬을 효율적으로 저장하는 방식
        - 이 함수는 각 행의 합계를 계산하여 반환
        """
        lst = []
        safty_sz = len(csrmat.indptr)-1  # 안전한 크기 계산
        
        # 각 행에 대해 처리
        for i, n in enumerate(csrmat.indptr):
            sumval = 0  # 행의 합계 초기화
            if i<safty_sz:  # 안전 범위 내에서
                # 해당 행의 인덱스와 데이터 가져오기
                indiceVal = csrmat.indices[csrmat.indptr[i]:csrmat.indptr[i+1]]
                dataVal = csrmat.data[csrmat.indptr[i]:csrmat.indptr[i+1]]
                
                # 각 값에 대해 곱셈 후 합계 계산
                for j, va1 in enumerate(indiceVal):
                    sumval += va1 * dataVal[j]
                
                lst.append(sumval)  # 계산된 합계를 리스트에 추가
        return lst



class BidPricePredict():
    """
    입찰 가격 예측을 담당하는 메인 클래스
    
    이 클래스의 역할:
    1. 학습된 머신러닝 모델들을 불러오기
    2. 입찰 정보를 입력받아 투찰률과 낙찰가 예측
    3. 텍스트 데이터(키워드, 기관명, 지역)를 숫자로 변환
    4. 예측 결과를 반환
    
    사용하는 모델들:
    - 모델1: 업체 투찰률 예측 (업체들이 얼마나 낮은 가격으로 입찰할지)
    - 모델2: 예가 투찰률 예측 (예정가 대비 얼마나 낮은 가격으로 입찰할지)  
    - 모델3: 참여 업체 수 예측 (몇 개 업체가 참여할지)
    """
    
    def __init__(self):
        """
        BidPricePredict 초기화 함수
        - 설정 파일 읽기
        - 학습된 모델들 불러오기
        - 텍스트 처리 도구들 초기화
        """
        # 디렉토리 경로 설정
        self.cur_dir = os.getcwd()  # 현재 작업 디렉토리
        self.data_dir = self.cur_dir+'\\data\\'  # 데이터 폴더
        self.save_dir = self.cur_dir+'\\res\\'  # 결과 저장 폴더
        
        # 주석처리된 대체 경로들 (개발 시 사용)
        #self.cur_dir = 'D:\\workspace\\python'
        #self.data_dir = self.cur_dir+'\\res\\조달청낙찰가예측\\'
        
        # 설정 파일 읽기
        self.config_path = os.path.join(self.save_dir, 'config.csv')  # 설정 파일 경로
        self.config = pd.read_csv(self.config_path)  # 설정 파일 읽기
        
        # 설정값들 추출
        self.server_ip = "0.0.0.0"  # 서버 IP 주소 (모든 인터페이스)
        self.server_port = int(self.config["PORT"].iloc[0])  # 서버 포트 번호
        self.avg_diffrt = float(self.config["AVG_DIFF_RT"].iloc[0])  # 평균 차이 비율
        
        # 디버그 모드 설정
        debg = str(self.config["DEBUG_MODE"].iloc[0])
        self.debug_mode = False
        if debg=="Y":  # 설정에서 디버그 모드가 Y이면
            self.debug_mode = True
        
        
        # 주석처리된 파일 경로들 (개발 시 사용)
        #self.krdic_path = os.path.join(self.data_dir, '표준국어대사전.NNP.csv')
        #self.tokenizer_path = os.path.join(self.data_dir, 'mlpregr.tokenizer.v0.1.1.npz')
        #self.vectorizer_path = os.path.join(self.data_dir, 'mlpregr.vectorizer.v0.1.1.npz')        
        
        # 학습된 모델 파일들의 경로 설정
        self.model_path1 = os.path.join(self.save_dir, 'mlpregr.model1.v0.1.1.npz')  # 업체 투찰률 예측 모델
        self.model_path2 = os.path.join(self.save_dir, 'mlpregr.model2.v0.1.1.npz')  # 예가 투찰률 예측 모델
        self.model_path3 = os.path.join(self.save_dir, 'mlpregr.model3.v0.1.1.npz')  # 참여 업체 수 예측 모델
        self.scaler_path = os.path.join(self.save_dir, 'x_fited_scaler.v2.npz')  # 데이터 정규화 도구
        
        # 학습된 모델들을 메모리로 불러오기
        self.model1 = joblib.load(self.model_path1)  # 투찰률예측모델(업체투찰률)
        self.model2 = joblib.load(self.model_path2)  # 투찰률예측모델(예가투찰하한률)
        self.model3 = joblib.load(self.model_path3)  # 참여업체예측모델
        self.scaler = joblib.load(self.scaler_path)  # 데이터 정규화 도구
        
        # 텍스트 처리 도구들 초기화
        self.tokenizer = KiwiTokenizer('mlpregr.tokenizer.v0.1.1.npz')  # 한국어 형태소 분석기
        #self.tokenizer.loadDictonary('표준국어대사전.NNP.csv')  # 표준국어대사전 로드 (주석처리)
        
        self.vectorizer = KiwiVectorizer()  # 텍스트를 숫자로 변환하는 도구
        self.vectorizer.load('mlpregr.vectorizer.v0.1.1.npz')  # 학습된 단어사전 불러오기
        
        # 고급 특성 엔지니어링 도구 초기화
        self.feature_eng = AdvancedFeatureEngineering()
        
    
    ###########################################################
    # 예측 관련 함수들
    ###########################################################
    
    def WinningPriceSamples(self, bssamt, diffrt, a):
        """
        낙찰가 샘플들을 생성하는 함수
        
        Args:
            bssamt (int): 기초금액 (입찰의 기준 금액)
            diffrt (float): 차이 비율 (예측 오차 범위)
            a (float): 예측된 투찰률
            
        Returns:
            list: 다양한 낙찰가 샘플 리스트
            
        설명:
        - 예측된 투찰률을 기준으로 다양한 시나리오의 낙찰가를 계산
        - 차이 비율을 적용하여 상한/하한 범위의 가격들을 생성
        """
        prices = []  # 낙찰가 샘플들을 저장할 리스트
        rates = [1.0, 0.5, 0, -0.5, -1.0]  # 차이 비율 적용 계수들 (상한부터 하한까지)
        
        # 각 비율에 대해 낙찰가 계산
        for v in rates:
            # 낙찰가 = 기초금액 × (예측투찰률 + (차이비율 × 계수))
            price = round(int(bssamt) * (a+(diffrt*v)) ,0)
            prices.append(price)
            
        return prices
                
    
    def convertScore(self, line):
        """
        텍스트를 TF-IDF 점수로 변환하는 함수
        
        Args:
            line (str): 점수로 변환할 텍스트 (키워드, 기관명, 지역명 등)
            
        Returns:
            float: 텍스트의 TF-IDF 점수
            
        설명:
        - 텍스트를 형태소 분석하여 의미있는 단어만 추출
        - 추출된 단어들을 TF-IDF 방식으로 점수화
        - 머신러닝 모델이 이해할 수 있는 숫자로 변환
        """
        nns = self.tokenizer.nn_only([line])  # 텍스트에서 명사류만 추출
        pt = self.vectorizer.scores(nns)  # TF-IDF 점수 계산
        return pt[0]  # 첫 번째(유일한) 점수 반환
       
    
    def PredictWinningPriceOfBidding(self, params):
        """
        입찰 정보를 입력받아 투찰률과 참여업체 수를 예측하는 핵심 함수
        
        Args:
            params (list): 입찰 정보 리스트
                - params[0]: 기초금액 (bssamt)
                - params[1]: 낙찰하한률 (lowerrt)
                - params[2]: 참여업체수 (companycnt)
                - params[3]: A계산여부 (a)
                - params[4]: 순공사원가적용여부 (orgamt)
                - params[5]: 면허제한코드 (limitlic)
                - params[6]: 공고기관점수 (insttpt)
                - params[7]: 공사지역점수 (areapt)
                - params[8]: 키워드점수 (keywordpt)
        
        Returns:
            list: [업체투찰률예측, 예가투찰률예측, 참여업체수예측]
        """
        # 입력 파라미터들을 적절한 데이터 타입으로 변환
        bssamt = int(params[0])      # 기초금액
        lowerrt = float(params[1])   # 낙찰하한률
        companycnt = int(params[2])  # 참여업체수
        a = int(params[3])           # A계산여부
        orgamt = int(params[4])      # 순공사원가적용여부
        limitlic = int(params[5])    # 면허제한코드
        insttpt = float(params[6])   # 공고기관점수
        areapt = float(params[7])    # 공사지역점수
        keywordpt = float(params[8]) # 키워드점수
        
        # ===== 학습 시와 동일한 특성 엔지니어링 적용 =====
        # 기본 특성들을 데이터프레임으로 변환
        basic_features = pd.DataFrame({
            '기초금액': [bssamt],
            '낙찰하한률': [lowerrt],
            '참여업체수': [companycnt],
            'A계산여부': [a],
            '순공사원가적용여부': [orgamt],
            '면허제한코드': [limitlic],
            '공고기관점수': [insttpt],
            '공사지역점수': [areapt],
            '키워드점수': [keywordpt]
        })
        
        # 학습 시와 동일한 고급 특성 엔지니어링 적용
        enhanced_features = self.feature_eng.create_interaction_features(basic_features)
        enhanced_features = self.feature_eng.create_ratio_features(enhanced_features)
        enhanced_features = self.feature_eng.create_categorical_features(enhanced_features)
        enhanced_features = self.feature_eng.create_statistical_features(enhanced_features)
        
        # NaN 값 처리
        enhanced_features = enhanced_features.fillna(0)
        
        # 학습 시 사용한 기본 컬럼만 선택 (스케일러 호환성을 위해)
        # 학습 시 사용한 컬럼: [기초금액, 낙찰하한률, 참여업체수, A계산여부, 순공사원가적용여부, 면허제한코드, 공고기관점수, 공사지역점수, 키워드점수]
        required_columns = ['기초금액', '낙찰하한률', '참여업체수', 'A계산여부', '순공사원가적용여부', '면허제한코드', '공고기관점수', '공사지역점수', '키워드점수']
        
        # 기본 컬럼만 사용 (스케일러가 이 순서를 기대함)
        x_test_data = enhanced_features[required_columns].values.tolist()
        
        # 입력 데이터를 정규화 (학습 시 사용한 동일한 스케일러 사용)
        x_test = self.scaler.transform(x_test_data).tolist()
        #print(x_test)  # 디버깅용 출력 (주석처리)
    
        # 3개의 머신러닝 모델로 예측 수행
        predrt1 = self.model1.predict(x_test)  # 업체투찰률예측 (업체들이 얼마나 낮은 가격으로 입찰할지)
        predrt2 = self.model2.predict(x_test)  # 예가투찰률예측 (예정가 대비 얼마나 낮은 가격으로 입찰할지)
        predrt3 = self.model3.predict(x_test)  # 업체수예측 (몇 개 업체가 참여할지)
        
        # 주석처리된 이전 버전의 결과 계산
        #resultAmt = round(int(params[0]) * float(predrt[0]) * limitrt,0)
        #return resultAmt
        
        # 예측 결과를 리스트로 반환 (float 타입으로 변환)
        return [ float(predrt1[0]), float(predrt2[0]), float(predrt3[0]) ]
    

# ===== Flask 웹 서버 설정 =====
app = Flask(__name__)  # Flask 애플리케이션 생성
app.ml = BidPricePredict()  # 머신러닝 예측 객체를 앱에 연결



@app.before_request
def authenticate():
    """
    모든 요청 전에 실행되는 함수 (인증 처리)
    
    설명:
    - 웹 요청이 들어올 때마다 먼저 실행됨
    - 사용자 인증 정보가 있으면 사용, 없으면 'Anonymous'로 설정
    """
    # request.authorization username이 있는 경우 g.user에 할당
    g.user = 'Anonymous' if not request.authorization else request.authorization['username']

@app.route('/version')
def ApiVersion():
    """
    API 버전 정보를 반환하는 엔드포인트
    
    Returns:
        JSON: API 버전과 설명 정보
    """
    return jsonify({'version': 1.2, 'description':'예가투찰률과 업체투찰률 예측기능 제공.' })

@app.route('/api')
def ApiList():
    """
    사용 가능한 API 메서드 목록을 반환하는 엔드포인트
    
    Returns:
        JSON: 사용 가능한 API 메서드들의 리스트
    """
    return jsonify({'methods':[ "predict(bssamt, lowerrt, companycnt, a, orgamt, limitlic, instt, area, keyword)"
                                ,"score(keyword)"
                               ] })


@app.route('/api/score')
def KeywordScore():
    """
    키워드의 TF-IDF 점수를 계산하는 API 엔드포인트
    
    URL 예시: /api/score?keyword=서울시청 건물 신축공사
    
    Returns:
        JSON: 키워드와 해당 점수
    """
    keyword = request.args.get('keyword', 0)  # URL 파라미터에서 키워드 추출
    pt = app.ml.convertScore(keyword)  # 키워드를 TF-IDF 점수로 변환
    return jsonify({'score': pt, 'keyword':keyword })  # 결과를 JSON으로 반환


@app.route('/api/predict')
def Predict():
    """
    입찰 정보를 입력받아 투찰률과 낙찰가를 예측하는 메인 API 엔드포인트
    
    URL 파라미터:
        - bssamt: 기초금액
        - lowerrt: 낙찰하한률
        - companycnt: 참여업체수
        - a: A계산여부
        - orgamt: 순공사원가적용여부
        - limitlic: 면허제한코드
        - instt: 공고기관명
        - area: 공사지역
        - keyword: 키워드
    
    URL 예시: /api/predict?bssamt=100000000&lowerrt=0.87&companycnt=5&a=1&orgamt=0&limitlic=6000&instt=서울시청&area=서울시&keyword=건물 신축공사
    
    Returns:
        JSON: 예측된 투찰률, 낙찰가, 참여업체수 등의 정보
    """
    # URL 파라미터들에서 입찰 정보 추출
    bssamt = request.args.get('bssamt', 0)      # 기초금액
    lowerrt = request.args.get('lowerrt', 0)    # 낙찰하한률
    companycnt = request.args.get('companycnt', 0)  # 참여업체수
    a = request.args.get('a', 0)                # A계산여부
    orgamt = request.args.get('orgamt', 0)      # 순공사원가적용여부
    limitlic = request.args.get('limitlic', 0)  # 면허제한코드
    instt  = request.args.get('instt', 0)       # 공고기관명
    area = request.args.get('area', 0)          # 공사지역
    keyword = request.args.get('keyword', 0)    # 키워드
    
    # 텍스트 데이터들을 TF-IDF 점수로 변환
    insttpt = app.ml.convertScore(instt)    # 공고기관명을 점수로 변환
    areapt = app.ml.convertScore(area)      # 공사지역을 점수로 변환
    keywordpt = app.ml.convertScore(keyword)  # 키워드를 점수로 변환
    
    # 주석처리된 이전 버전의 변수들
    #is_a = int(a) > 0 and 1 or 0
    #is_org = int(orgamt) > 0 and 1 or 0    
  
    # 주석처리된 이전 버전의 예측 호출
    #predrts = app.ml.PredictWinningPriceOfBidding([bssamt, lowerrt, companycnt, is_a, is_org])
    
    # 머신러닝 모델로 예측 수행
    predrts = app.ml.PredictWinningPriceOfBidding([bssamt, lowerrt, companycnt, a, orgamt, limitlic, insttpt, areapt, keywordpt])

    # 예측 결과 분리
    comlowrt = predrts[0]    # 업체 투찰률 예측값
    planlowrt = predrts[1]   # 예가 투찰률 예측값
    compcnt = predrts[2]     # 참여 업체 수 예측값
    
    # 주석처리된 이전 버전의 계산
    #min_predrt = float(planlowrt-app.ml.avg_diffrt)
    #max_predrt = float(comlowrt+app.ml.avg_diffrt)
    
    # 예측된 낙찰가 계산
    comPredictedAmt = round(int(bssamt) * comlowrt,0)    # 업체 투찰률 기반 낙찰가
    planPredictedAmt = round(int(bssamt) * planlowrt,0)  # 예가 투찰률 기반 낙찰가
    
    # 다양한 시나리오의 낙찰가 샘플 생성
    diffrt = app.ml.avg_diffrt  # 평균 차이 비율
    prices = app.ml.WinningPriceSamples(bssamt, diffrt, comlowrt) + app.ml.WinningPriceSamples(bssamt, diffrt, planlowrt)
    
    # 결과를 JSON으로 반환
    return jsonify({
        'planLowerRatio':planlowrt,           # 예가 투찰률
        'comLowerRatio': comlowrt,            # 업체 투찰률
        'avgDiffRatio':app.ml.avg_diffrt,     # 평균 차이 비율
        'planPredictedAmt':planPredictedAmt,  # 예가 투찰률 기반 낙찰가
        'comPredictedAmt':comPredictedAmt,    # 업체 투찰률 기반 낙찰가
        'predictedAmountsInScope':prices,     # 다양한 시나리오의 낙찰가들
        'companyCount':compcnt                # 예측된 참여 업체 수
    })



if __name__ == "__main__":
    """
    메인 실행 부분
    
    설명:
    - 이 파일이 직접 실행될 때만 웹 서버가 시작됨
    - 설정 파일에서 읽은 IP와 포트로 서버 실행
    - 디버그 모드는 설정 파일의 DEBUG_MODE 값에 따라 결정
    """
    app.run(debug=app.ml.debug_mode, host=app.ml.server_ip, port=app.ml.server_port)

        
