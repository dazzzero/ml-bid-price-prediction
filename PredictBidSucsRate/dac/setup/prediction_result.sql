-- ML_C 테이블 (예측 결과 저장)
CREATE TABLE IF NOT EXISTS ML_C (
    입찰번호 VARCHAR(50) NOT NULL
    , 입찰차수 VARCHAR(10) NOT NULL
    , 기초금액률 DECIMAL(18, 9)
    , 낙찰하한률 DECIMAL(10, 7)
    , 기초금액 DECIMAL(20, 2)
    , 순공사원가 DECIMAL(20, 2)
    , 간접비 DECIMAL(20, 2)
    , A계산여부 VARCHAR(10) DEFAULT '0'
    , 순공사원가적용여부 VARCHAR(10) DEFAULT '0'
    , 면허제한코드 VARCHAR(200)
    , 공고기관코드 VARCHAR(50)
    , 주공종명 VARCHAR(200)
    , 공고기관명 VARCHAR(200)
    , 공고기관점수 DECIMAL(21, 17) DEFAULT 0.00000000 NOT NULL
    , 공사지역 VARCHAR(400)
    , 공사지역점수 DECIMAL(21, 17) DEFAULT 0.000000000 NOT NULL
    , 키워드 VARCHAR(1000)
    , 키워드점수 DECIMAL(22, 17) DEFAULT 0.00000000 NOT NULL
    , 공고일자 DATETIME
    , 개찰일시 DATETIME
    , 예측_URL VARCHAR(4000) NOT NULL
    , 업체투찰률_예측 DECIMAL(18, 9)
    , 예가투찰률_예측 DECIMAL(18, 9)
    , 참여업체수_예측 INTEGER
    , 등록일시 DATETIME NOT NULL DEFAULT(DATETIME('now', 'localtime'))
    , 예측일시 DATETIME
    , PRIMARY KEY (입찰번호, 입찰차수)
);
