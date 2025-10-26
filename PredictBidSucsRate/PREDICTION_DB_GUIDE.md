# 예측 결과 데이터베이스 저장 가이드

## 📋 개요

`predict_sample_data.py` 스크립트로 예측한 결과를 SQLite 데이터베이스에 저장하고 관리할 수 있는 시스템입니다.

## 🗄️ 데이터베이스 구조

### 테이블: ML_C

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| 입찰번호 | VARCHAR(50) | 입찰번호 (PK) |
| 입찰차수 | VARCHAR(10) | 입찰차수 (PK) |
| 기초금액률 | DECIMAL(18,9) | 기초금액률 |
| 낙찰하한률 | DECIMAL(10,7) | 낙찰하한률 |
| 기초금액 | DECIMAL(20,2) | 기초금액 |
| 순공사원가 | DECIMAL(20,2) | 순공사원가 |
| 간접비 | DECIMAL(20,2) | 간접비 |
| A계산여부 | VARCHAR(10) | A계산 여부 (O/X) |
| 순공사원가적용여부 | VARCHAR(10) | 순공사원가 적용 여부 |
| 면허제한코드 | VARCHAR(200) | 면허제한코드 |
| 공고기관코드 | VARCHAR(50) | 공고기관코드 |
| 주공종명 | VARCHAR(200) | 주공종명 |
| 공고기관명 | VARCHAR(200) | 공고기관명 |
| 공고기관점수 | DECIMAL(10,8) | 공고기관 TF-IDF 점수 |
| 공사지역 | VARCHAR(400) | 공사지역 |
| 공사지역점수 | DECIMAL(12,9) | 공사지역 TF-IDF 점수 |
| 키워드 | VARCHAR(1000) | 키워드 |
| 키워드점수 | DECIMAL(10,8) | 키워드 TF-IDF 점수 |
| 공고일자 | DATETIME | 공고일자 |
| 개찰일시 | DATETIME | 개찰일시 |
| 예측_URL | VARCHAR(4000) | 예측 URL |
| 업체투찰률_예측 | DECIMAL(18,9) | 업체투찰률 예측값 |
| 예가투찰률_예측 | DECIMAL(18,9) | 예가투찰률 예측값 |
| 참여업체수_예측 | INTEGER | 참여업체수 예측값 |
| 등록일시 | DATETIME | 등록일시 |
| 예측일시 | DATETIME | 예측 수행 일시 |

## 🚀 사용 방법

### 1. 예측 실행 및 데이터베이스 저장

```bash
cd PredictBidSucsRate
python predict_sample_data.py
```

**실행 결과:**
- 엑셀 파일 저장: `res/predict_result/sample_prediction_result_YYYYMMDD_HHMMSS.xlsx`
- 데이터베이스 저장: `dac/ml_c.db`

### 2. 예측 결과 조회 및 관리

```bash
python query_prediction_results.py
```

**메뉴 옵션:**
1. **요약 통계 보기**: 전체 저장된 데이터의 통계 정보
2. **최근 예측 결과 보기**: 최근 N건의 예측 결과 조회
3. **엑셀 파일로 내보내기**: 데이터베이스의 데이터를 엑셀 파일로 내보내기
4. **입찰번호로 검색**: 특정 입찰번호로 검색
5. **오래된 데이터 삭제**: 지정된 일수 이전 데이터 삭제

## 📁 파일 구조

```
PredictBidSucsRate/
├── dac/
│   ├── DatabaseManager.py              # 데이터베이스 관리 클래스
│   ├── PredictionResultManager.py      # 예측 결과 저장/조회 클래스
│   ├── ml_c.db                         # SQLite 데이터베이스 파일 (ML_C 테이블)
│   └── setup/
│       └── prediction_result.sql       # ML_C 테이블 생성 스크립트
├── predict_sample_data.py              # 예측 실행 스크립트 (DB 저장 기능 포함)
├── query_prediction_results.py         # 예측 결과 조회/관리 스크립트
└── res/
    └── predict_result/                 # 엑셀 결과 파일 저장 폴더
```

## 🔧 주요 기능

### 1. 자동 데이터베이스 저장
- 예측 실행 시 자동으로 데이터베이스에 저장
- 엑셀 파일과 데이터베이스에 동시 저장
- **UPSERT 방식**: 기존 데이터가 있으면 업데이트, 없으면 새로 저장
- 저장 실패 시에도 엑셀 파일은 정상 저장

### 2. 데이터 조회 및 검색
- 전체 통계 정보 조회
- 최근 예측 결과 조회
- 입찰번호로 특정 데이터 검색
- 데이터를 엑셀 파일로 내보내기

### 3. 데이터 관리
- 오래된 데이터 자동 삭제
- 모델 버전별 데이터 구분
- 예측 일시 자동 기록

## ⚙️ 설정 옵션

### predict_sample_data.py 설정

```python
# 데이터베이스 저장 여부 설정
predictor.save_predictions(
    predictions, 
    output_file, 
    save_to_db=True,        # True: DB 저장, False: 엑셀만 저장
    model_version="v0.1.1", # 모델 버전
    insert_mode="REPLACE"   # 저장 모드: REPLACE(업데이트), IGNORE(무시), INSERT(오류)
)
```

### 저장 모드 옵션

- **REPLACE** (기본값): 기존 데이터가 있으면 업데이트, 없으면 새로 저장
- **IGNORE**: 기존 데이터가 있으면 무시하고 건너뜀
- **INSERT**: 기존 데이터가 있으면 오류 발생 (중복 방지)

### 데이터베이스 설정

- **데이터베이스 파일**: `dac/ml_c.db`
- **테이블명**: `ML_C`
- **테이블 자동 생성**: 최초 실행 시 자동으로 테이블 생성
- **인코딩**: UTF-8
- **기본키**: (입찰번호, 입찰차수) 복합키

## 🛠️ 문제 해결

### 1. 데이터베이스 연결 실패
```
❌ 데이터베이스 매니저 초기화 실패
```
**해결방법:**
- `dac` 폴더가 존재하는지 확인
- `prediction_result.sql` 파일이 존재하는지 확인
- 파일 권한 확인

### 2. 테이블 생성 실패
```
❌ 테이블 생성 실패
```
**해결방법:**
- SQLite3가 설치되어 있는지 확인
- `dac` 폴더에 쓰기 권한이 있는지 확인

### 3. 데이터 저장 실패
```
❌ 데이터베이스 저장 실패
```
**해결방법:**
- 데이터 타입이 올바른지 확인
- 필수 컬럼에 값이 있는지 확인
- 데이터베이스 파일이 손상되지 않았는지 확인

## 📊 성능 최적화

### 1. 대용량 데이터 처리
- 100건씩 배치로 저장하여 메모리 사용량 최적화
- 진행률 표시로 처리 상황 모니터링

### 2. 데이터 정리
- 정기적으로 오래된 데이터 삭제
- 인덱스 생성으로 조회 성능 향상

## 🔍 모니터링

### 저장된 데이터 확인
```python
from dac.PredictionResultManager import PredictionResultManager

db_manager = PredictionResultManager()
count = db_manager.get_prediction_count()
print(f"저장된 데이터: {count}건")
```

### 최근 예측 결과 조회
```python
results = db_manager.get_prediction_results(limit=10)
for result in results:
    print(result)
```

### 특정 입찰번호로 검색
```python
# query_prediction_results.py에서 입찰번호 검색 기능 사용
# 또는 직접 SQL 쿼리 실행
db_cmd = db_manager.connection.command()
query = "SELECT * FROM ML_CST WHERE 입찰번호 = ?"
results = db_cmd.select(query, ('입찰번호값',))
```

## 📝 주의사항

1. **데이터 백업**: 정기적으로 `ml_c.db` 파일을 백업하세요.
2. **모델 버전 관리**: 모델이 업데이트될 때마다 버전을 변경하세요.
3. **디스크 공간**: 대용량 데이터 저장 시 디스크 공간을 확인하세요.
4. **동시 접근**: 여러 프로세스가 동시에 데이터베이스에 접근하지 않도록 주의하세요.

## 🆘 지원

문제가 발생하면 다음 정보와 함께 문의하세요:
- 오류 메시지 전체 내용
- 실행 환경 (Python 버전, OS)
- 데이터 크기 및 형태
- 실행한 명령어
