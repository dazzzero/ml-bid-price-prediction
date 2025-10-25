# -*- coding: utf-8 -*-
"""
샘플 데이터 예측 스크립트
사용자가 제공한 sample_prediction_data.csv를 사용하여 예측을 수행합니다.
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
import random as rnd
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from kiwipiepy import Kiwi

# KiwiTokenizer 클래스 (bid.ml.train.py에서 복사)
class KiwiTokenizer():
    def __init__(self, saved_filenm):
        self.rnd_num = rnd.randint(100, 999)
        self.cur_dir = os.getcwd()
        self.data_dir = self.cur_dir+'\\data\\'
        self.save_dir = self.cur_dir+'\\res\\'
        self.save_filename = saved_filenm
        self.kiwi = None
        self.kiwi = self.CreateKiwi(saved_filenm)
    
    def save(self, filename):
        filepath = os.path.join(self.save_dir, filename)
        joblib.dump(self.kiwi._user_values, filepath)
        return self
    
    def load(self, filename):
        filepath = os.path.join(self.save_dir, filename)
        o = joblib.load(filepath)
        return o
        
    def loadDictonary(self, filename):
        self.data = pd.read_csv(self.data_dir+filename)
        print(self.data[:10])
        for i, row in enumerate(self.data.iloc):
            self.kiwi.add_user_word(row["단어"], 'NNP')
    
    def CreateKiwi(self, saved_filenm):
        o = None
        if(self.kiwi is None):
            if(saved_filenm is None):
                o = Kiwi(num_workers=8)
            else:
                o = Kiwi(num_workers=8)
                o._user_values = self.load(self.save_dir+saved_filenm)
        return o
            
    def cleared_line(self, line):
        if pd.isna(line) or line is None:
            line = ''
        else:
            line = str(line).lower().replace('(', ' ').replace(')', ' ').replace('n/a', '')
        
        nm_words = []
        tokens = self.kiwi.tokenize(line)
        for token in tokens:
            if token.tag in ['MM', 'NNG', 'NNB', 'NNP', 'SL', 'XPN', 'MAG', 'SN', 'SO', 'W_SERIAL']:
                nm_words.append(token.form)
                
        return ' '.join(nm_words)
    
    def cleared_lines_from(self, orglines):
        lines = []
        for line in orglines:
            lines.append(self.cleared_line(line))
        return lines      
    
    def nn_only(self, orglines):
        lines = []
        for key in orglines:
            if pd.isna(key) or key is None:
                key = ''
            else:
                key = str(key).lower().replace('(', ' ').replace(')', ' ').replace('n/a', '')
            
            nm_words = []
            tokens = self.kiwi.tokenize(key)
            for token in tokens:
                if token.tag in ['MM', 'NNG', 'NNB', 'NNP', 'SL', 'XPN', 'MAG', 'SN', 'SO', 'W_SERIAL']:
                    nm_words.append(token.form)
            lines.append(' '.join(nm_words))
        return lines

# KiwiVectorizer 클래스 (bid.ml.train.py에서 복사)
class KiwiVectorizer():
    def __init__(self):
        self.rnd_num = rnd.randint(100, 999)
        self.cur_dir = os.getcwd()
        self.save_dir = self.cur_dir+'\\res\\'
        
        self.vect = TfidfVectorizer(
            ngram_range=(1, 1), 
            token_pattern='(?u)\\b\\w+\\b',
            max_features=5000,
            min_df=2,
            max_df=0.95,
            sublinear_tf=True
        )
    
    def load(self, filename):
        filepath = os.path.join(self.save_dir, filename)
        voca = joblib.load(filepath)
        self.vect.vocabulary_ = voca["vocabulary"] 
        self.vect.idf_ = voca["idf"]
    
    def save(self, filename):
        filepath = os.path.join(self.save_dir, filename)
        joblib.dump({'vocabulary':self.vect.vocabulary_, 'idf':self.vect.idf_}, filepath)
        print("단어사전 파일("+filename+")로 저장합니다. ")
    
    def fit(self, lines):
        return self.vect.fit(lines)
    
    def transform(self, lines):
        return self.vect.transform(lines)
    
    def scores(self, lines):
        return self.toValues(self.transform(lines))

    def toValues(self, csrmat:csr_matrix):
        lst = []
        safty_sz = len(csrmat.indptr)-1
        for i, n in enumerate(csrmat.indptr):
            sumval = 0
            if i<safty_sz:
                indiceVal = csrmat.indices[csrmat.indptr[i]:csrmat.indptr[i+1]]
                dataVal = csrmat.data[csrmat.indptr[i]:csrmat.indptr[i+1]]
                for j, va1 in enumerate(indiceVal):
                    sumval += va1 * dataVal[j]
                lst.append(sumval)
        return lst

class SampleDataPredictor():
    """
    샘플 데이터 예측 클래스
    """
    
    def __init__(self):
        print("="*80)
        print("🔮 샘플 데이터 예측 시스템 초기화")
        print("="*80)
        
        self.cur_dir = os.getcwd()
        self.data_dir = self.cur_dir + '\\data\\'
        self.save_dir = self.cur_dir + '\\res\\7.7\\'
        
        self.load_models_and_preprocessors()
        print("✅ 예측 시스템 초기화 완료")
        print("="*80)
    
    def load_models_and_preprocessors(self):
        """저장된 모델과 전처리 도구들을 로드"""
        try:
            # 1. 형태소 분석기 로드
            print("📚 형태소 분석기 로드 중...")
            self.tokenizer = KiwiTokenizer("mlpregr.tokenizer.v0.1.1.npz")
            self.tokenizer.loadDictonary('표준국어대사전.NNP.csv')
            print("✅ 형태소 분석기 로드 완료")
            
            # 2. TF-IDF 벡터화기 로드
            print("🔤 TF-IDF 벡터화기 로드 중...")
            self.vectorizer = KiwiVectorizer()
            self.vectorizer.load("mlpregr.vectorizer.v0.1.1.npz")
            print("✅ TF-IDF 벡터화기 로드 완료")
            
            # 3. 정규화 도구 로드
            print("📊 정규화 도구 로드 중...")
            self.scaler = joblib.load(self.save_dir + "x_fited_scaler.v2.npz")
            print("✅ 정규화 도구 로드 완료")
            
            # 4. 머신러닝 모델들 로드
            print("🤖 머신러닝 모델들 로드 중...")
            self.model1 = joblib.load(self.save_dir + "mlpregr.model1.v0.1.1.npz")  # 업체투찰률
            self.model2 = joblib.load(self.save_dir + "mlpregr.model2.v0.1.1.npz")  # 예가투찰률
            self.model3 = joblib.load(self.save_dir + "mlpregr.model3.v0.1.1.npz")  # 참여업체수
            print("✅ 머신러닝 모델들 로드 완료")
            
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
            print("먼저 bid.ml.train.py를 실행하여 모델을 훈련시켜주세요.")
            sys.exit(1)
    
    def preprocess_data(self, data_file):
        """데이터 전처리"""
        print("="*80)
        print(f"📁 데이터 로드: {data_file}")
        print("="*80)
        
        # CSV 파일 로드
        data = pd.read_csv(self.data_dir + data_file)
        print(f"데이터 크기: {data.shape}")
        print(f"컬럼: {list(data.columns)}")
        
        # 컬럼명 정리 (공백 제거)
        data.columns = data.columns.str.strip()
        print(f"정리된 컬럼: {list(data.columns)}")
        
        # 필요한 컬럼들 정의
        required_columns = ['기초금액', '낙찰하한률', '참여업체수',
                           '간접비', '순공사원가', 
                           '면허제한코드', '공고기관코드',
                           '공고기관명', '공고기관점수',
                           '공사지역', '공사지역점수',
                           '키워드', '키워드점수']
        
        # 존재하는 컬럼만 선택
        available_columns = [col for col in required_columns if col in data.columns]
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            print(f"⚠️  누락된 컬럼들: {missing_columns}")
            print("기본값으로 채워집니다.")
        
        # 데이터프레임 생성
        dataset_x = pd.DataFrame(data, columns=available_columns)
        
        # 누락된 컬럼들을 기본값으로 채우기
        for col in missing_columns:
            if col in ['면허제한코드', '공고기관코드']:
                dataset_x[col] = 0
            elif col in ['공고기관점수', '공사지역점수', '키워드점수']:
                dataset_x[col] = 0.0
            elif col in ['공고기관명', '공사지역', '키워드']:
                dataset_x[col] = ''
            elif col == '참여업체수':
                dataset_x[col] = 5  # 기본값으로 5 설정
            else:
                dataset_x[col] = 0
        
        # 컬럼 순서 정렬
        dataset_x = dataset_x[required_columns]
        
        # 텍스트 컬럼들을 문자열로 변환
        print("📝 텍스트 데이터 전처리 중...")
        text_columns = ['키워드', '공고기관명', '공사지역']
        for col in text_columns:
            if col in dataset_x.columns:
                dataset_x[col] = dataset_x[col].fillna('').astype(str)
                dataset_x[col] = dataset_x[col].replace(['nan', 'NaN', 'None', 'null'], '')
        
        # 문자열 컬럼들을 숫자로 변환
        print("🔢 숫자 데이터 변환 중...")
        if '면허제한코드' in dataset_x.columns:
            dataset_x['면허제한코드'] = dataset_x['면허제한코드'].astype(str).apply(
                lambda x: hash(x) % 1000000 if pd.notna(x) and x != 'nan' else 0)
        
        if '공고기관코드' in dataset_x.columns:
            dataset_x['공고기관코드'] = dataset_x['공고기관코드'].astype(str).apply(
                lambda x: hash(x) % 1000000 if pd.notna(x) and x != 'nan' else 0)
        
        # 텍스트 데이터를 TF-IDF 점수로 변환
        print("🔤 텍스트를 TF-IDF 점수로 변환 중...")
        lines = self.tokenizer.nn_only(dataset_x["키워드"].tolist())
        lines2 = self.tokenizer.nn_only(dataset_x["공고기관명"].tolist())
        lines3 = self.tokenizer.nn_only(dataset_x["공사지역"].tolist())
        
        # TF-IDF 점수 계산
        pts = self.vectorizer.scores(lines)
        pts2 = self.vectorizer.scores(lines2)
        pts3 = self.vectorizer.scores(lines3)
        
        # 점수를 데이터에 추가
        dataset_x["키워드점수"] = pts
        dataset_x["공고기관점수"] = pts2
        dataset_x["공사지역점수"] = pts3
        
        print(f"✅ 전처리 완료: {dataset_x.shape[1]}개 특성")
        return dataset_x
    
    def predict_data(self, dataset_x):
        """예측 수행"""
        print("="*80)
        print("🔮 예측 수행 중...")
        print("="*80)
        
        # 필요한 컬럼만 선택 (훈련 시 사용한 특성과 동일하게)
        # 훈련 시 사용한 특성: [0,1,2,7,8,13,17,19,21] = 기초금액, 낙찰하한률, 참여업체수, 간접비, 순공사원가, 면허제한코드, 공고기관점수, 공사지역점수, 키워드점수
        feature_columns = ['기초금액', '낙찰하한률', '참여업체수', '간접비', '순공사원가', 
                          '면허제한코드', '공고기관점수', '공사지역점수', '키워드점수']
        
        # 존재하는 컬럼만 선택
        available_feature_columns = [col for col in feature_columns if col in dataset_x.columns]
        selected_columns = dataset_x[available_feature_columns]
        
        print(f"선택된 특성 컬럼: {available_feature_columns}")
        print(f"선택된 컬럼 수: {len(available_feature_columns)}")
        
        # 데이터 검증
        print("🔍 데이터 검증 중...")
        if selected_columns.isnull().any().any():
            print("⚠️  결측값이 발견되었습니다. 0으로 채웁니다.")
            selected_columns = selected_columns.fillna(0)
        
        if selected_columns.isin([np.inf, -np.inf]).any().any():
            print("⚠️  무한값이 발견되었습니다. 0으로 채웁니다.")
            selected_columns = selected_columns.replace([np.inf, -np.inf], 0)
        
        # 정규화 적용
        print("📊 데이터 정규화 중...")
        try:
            x_scaled = self.scaler.transform(selected_columns)
            print(f"✅ 정규화 완료: {x_scaled.shape}")
        except Exception as e:
            print(f"❌ 정규화 실패: {e}")
            print("스케일러가 훈련 시 사용한 특성 수와 맞지 않을 수 있습니다.")
            print(f"현재 특성 수: {selected_columns.shape[1]}")
            raise e
        
        # 3개 모델로 예측 수행
        print("🤖 머신러닝 모델로 예측 중...")
        try:
            pred1 = self.model1.predict(x_scaled)  # 업체투찰률 예측
            print("✅ 업체투찰률 예측 완료")
        except Exception as e:
            print(f"❌ 업체투찰률 예측 실패: {e}")
            pred1 = np.zeros(len(x_scaled))
        
        try:
            pred2 = self.model2.predict(x_scaled)  # 예가투찰률 예측
            print("✅ 예가투찰률 예측 완료")
        except Exception as e:
            print(f"❌ 예가투찰률 예측 실패: {e}")
            pred2 = np.zeros(len(x_scaled))
        
        try:
            pred3 = self.model3.predict(x_scaled)  # 참여업체수 예측
            print("✅ 참여업체수 예측 완료")
        except Exception as e:
            print(f"❌ 참여업체수 예측 실패: {e}")
            pred3 = np.zeros(len(x_scaled))
        
        # 예측 결과를 원본 데이터에 추가
        result_df = dataset_x.copy()
        
        # 입찰번호와 입찰차수를 원본 데이터에서 가져와서 제일 앞에 추가
        original_data = pd.read_csv(self.data_dir + "sample_prediction_data.csv")
        original_data.columns = original_data.columns.str.strip()  # 컬럼명 공백 제거
        
        if '입찰번호' in original_data.columns:
            result_df.insert(0, '입찰번호', original_data['입찰번호'].values)
        if '입찰차수' in original_data.columns:
            result_df.insert(1, '입찰차수', original_data['입찰차수'].values)
        
        # 예측 결과 컬럼들 추가
        result_df['업체투찰률예측'] = pred1
        result_df['예가투찰률예측'] = pred2
        result_df['참여업체수예측'] = pred3
        
        # 추가 계산 컬럼들
        result_df['예정금액예측'] = (result_df['예가투찰률예측'] * result_df['기초금액']) / result_df['낙찰하한률']
        result_df['낙찰금액(업체투찰률)예측'] = result_df['업체투찰률예측'] * result_df['기초금액']
        # A값여부: 간접비가 0원이 아닐 경우 O, 0원일 경우 X
        result_df['A값여부'] = result_df['간접비'].apply(lambda x: 'O' if x != 0 else 'X')
        
        print("✅ 예측 완료")
        print(f"   - 업체투찰률 예측 범위: {pred1.min():.3f} ~ {pred1.max():.3f}")
        print(f"   - 예가투찰률 예측 범위: {pred2.min():.3f} ~ {pred2.max():.3f}")
        print(f"   - 참여업체수 예측 범위: {pred3.min():.1f} ~ {pred3.max():.1f}")
        
        return result_df
    
    def save_predictions(self, result_df, output_file):
        """예측 결과를 엑셀 파일로 저장"""
        print("="*80)
        print("💾 예측 결과 저장 중...")
        print("="*80)
        
        # 결과 저장 디렉토리 생성
        result_dir = os.path.join(self.save_dir, "predict_result")
        os.makedirs(result_dir, exist_ok=True)
        
        output_path = os.path.join(result_dir, output_file)
        
        try:
            result_df.to_excel(
                output_path,
                sheet_name='예측결과',
                na_rep='NaN',
                float_format="%.6f",
                header=True,
                index=True,
                index_label="id",
                freeze_panes=(1, 0)
            )
            print(f"✅ 예측 결과 저장 완료: {output_path}")
            print(f"📊 데이터 크기: {len(result_df)}행 x {len(result_df.columns)}열")
            
        except Exception as e:
            print(f"❌ 엑셀 저장 실패: {e}")
            # CSV로 저장
            csv_path = output_path.replace('.xlsx', '.csv')
            result_df.to_csv(csv_path, 
                           na_rep='NaN', 
                           float_format="%.6f", 
                           header=True, 
                           index=True, 
                           index_label="id",
                           encoding='utf-8-sig')
            print(f"✅ CSV 파일로 저장 완료: {csv_path}")

def main():
    """메인 실행 함수"""
    data_file = "sample_prediction_data.csv"
    
    try:
        print("="*80)
        print("🎯 샘플 데이터 예측 시작")
        print("="*80)
        
        # 예측기 생성
        predictor = SampleDataPredictor()
        
        # 데이터 전처리
        processed_data = predictor.preprocess_data(data_file)
        
        # 예측 수행
        predictions = predictor.predict_data(processed_data)
        
        # 결과 저장
        output_file = f"sample_prediction_result_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        predictor.save_predictions(predictions, output_file)
        
        print("="*80)
        print("🎉 예측 프로세스 완료!")
        print(f"📁 결과 파일: res/predict_result/{output_file}")
        print("="*80)
        
        # 예측 결과 요약 출력
        print("\n📊 예측 결과 요약:")
        print(f"총 예측 건수: {len(predictions)}")
        print(f"업체투찰률 평균: {predictions['업체투찰률예측'].mean():.3f}")
        print(f"예가투찰률 평균: {predictions['예가투찰률예측'].mean():.3f}")
        print(f"참여업체수 평균: {predictions['참여업체수예측'].mean():.1f}")
        print(f"A값 여부: {predictions['A값여부'].value_counts().to_dict()}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
