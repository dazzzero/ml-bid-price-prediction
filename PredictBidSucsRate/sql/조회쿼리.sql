WITH basic_bid_info AS (
    SELECT
        a.bid_ntce_no AS 입찰번호,
        a.bid_ntce_ord AS 입찰차수,
        ISNULL(c.bssamt, 0) / 100000000.0 AS 기초금액률,
        ISNULL(a.sucsfbid_lwlt_rate, 0) / 100.0 AS 낙찰하한률,
        ISNULL(b.prtcpt_cnum, 0) AS 참여업체수,
        b.sucsfbid_rate AS 최종낙찰률,
        b.sucsfbid_rate - ISNULL(a.sucsfbid_lwlt_rate, 0) AS 낙찰률오차,
        (b.sucsfbid_amt / NULLIF(c.bssamt, 0)) * (ISNULL(a.sucsfbid_lwlt_rate, 0) / 100.0) AS 업체사정률,
        (b.sucsfbid_amt / NULLIF(c.bssamt, 0)) AS 업체투찰률,
        d.plnprc / NULLIF(c.bssamt, 0) AS 예가사정률,
        (d.plnprc / NULLIF(c.bssamt, 0)) * (ISNULL(a.sucsfbid_lwlt_rate, 0) / 100.0) AS 예가투찰률,
        ISNULL(c.bssamt, 0) AS 기초금액,
        ISNULL(d.plnprc, 0) AS 예정금액,
        ISNULL(c.bss_amt_purcnstcst, 0) AS 순공사원가,
        ISNULL(d.bsis_plnprc, 0) AS 기초예정금액,
        b.sucsfbid_amt AS 낙찰금액,
        (ISNULL(c.sfty_mngcst,0) + ISNULL(c.rtrfund_non,0) + ISNULL(c.mrfn_health_insrprm,0)
            + ISNULL(c.npn_insrprm,0) + ISNULL(c.odsn_lngtrmrcpr_insrprm,0)
            + ISNULL(c.sftyChck_mngcst,0) + ISNULL(c.qlty_mngcst,0)) AS 간접비,
        CASE WHEN c.bid_prce_calclA_yn = 'Y' THEN 1 ELSE 0 END AS A계산여부,
        CASE WHEN c.bss_amt_purcnstcst > 0 THEN 1 ELSE 0 END AS 순공사원가적용여부,

        ISNULL(AREA.lic_code, 0) AS 면허제한코드,

        TRY_CAST(ISNULL(a.ntce_instt_cd, '0') AS INT) AS 공고기관코드,
        CASE WHEN ISNULL(a.main_cnstty_nm, '') = '' THEN '-' ELSE a.main_cnstty_nm END AS 주공종명,
        a.bid_ntce_nm AS 입찰명,
        a.area_list AS 공사지역,
        a.ntce_instt_nm AS 공고기관명,
        0.00000000 AS 키워드점수

    FROM bd_cst_main a
             INNER JOIN ad_cst b
                        ON a.bid_ntce_no = b.bid_ntce_no AND a.bid_ntce_ord = b.bid_ntce_ord
             INNER JOIN bd_cst_prc c
                        ON a.bid_ntce_no = c.bid_ntce_no AND a.bid_ntce_ord = c.bid_ntce_ord
             INNER JOIN ad_cst_pprt d
                        ON a.bid_ntce_no = d.bid_ntce_no AND a.bid_ntce_ord = d.bid_ntce_ord
                            AND d.compno_rsrvtn_prce_sno = 1
             INNER JOIN (
                SELECT bid_ntce_no, MAX(bid_ntce_ord) AS bid_ntce_ord
                FROM bd_cst_main
                GROUP BY bid_ntce_no
            ) e ON a.bid_ntce_no = e.bid_ntce_no AND a.bid_ntce_ord = e.bid_ntce_ord
-- INNER JOIN ( 코드화한 지역제한임(나중에 해볼예정)
--         select ca.BID_NTCE_NO, ca.BID_NTCE_ORD, SUM(ISNULL(TRY_CAST(cac.AREA_CL_CD AS BIGINT),0)*1000) AS LIC_CODE
--         from cm_area ca
--                  left join cm_area_cd cac
--                            on ca.prtcpt_psbl_rgn_nm = cac.area_cl_nm
--         where area_cl_cd is not null AND BSNS_DIV_NM = '공사'
--         GROUP BY ca.BID_NTCE_NO, ca.BID_NTCE_ORD
--     ) AREA ON AREA.BID_NTCE_NO = A.BID_NTCE_NO AND AREA.BID_NTCE_ORD = A.BID_NTCE_ORD

    WHERE a.sucsfbid_lwlt_rate IS NOT NULL
),
     train_datasheet AS (
         SELECT
             입찰번호, 입찰차수,
             기초금액률, 낙찰하한률, 참여업체수, 최종낙찰률, 업체사정률, 예가사정률,
             업체투찰률,
             (ROUND(((예정금액 - 간접비) * 낙찰하한률) + 간접비, 0) / NULLIF(기초금액, 0)) AS 예가투찰률,
             (업체투찰률 - (ROUND(((예정금액 - 간접비) * 낙찰하한률) + 간접비, 0) / NULLIF(기초금액, 0))) * 100 AS 투찰률오차,
             기초금액, 예정금액, 순공사원가, 기초예정금액, 낙찰금액, 간접비, A계산여부, 순공사원가적용여부,
             ROUND(((예정금액 - 간접비) * 낙찰하한률) + 간접비, 0) AS 낙찰하한가,
             면허제한코드, 공고기관코드, 주공종명,
             공고기관명, 0.00000000 AS 공고기관점수,
             공사지역, 0.000000000 AS 공사지역점수,
             CONCAT(입찰명, ' ', 주공종명) AS 키워드, 키워드점수
         FROM basic_bid_info
         WHERE 업체투찰률 IS NOT NULL
     ),
     test_datasheet AS (
         SELECT
             입찰번호, 입찰차수,
             기초금액률, 낙찰하한률, 참여업체수, 최종낙찰률, 업체사정률, 예가사정률,
             업체투찰률, 예가투찰률, 투찰률오차,
             기초금액, 예정금액, 순공사원가, 기초예정금액, 낙찰금액, 간접비, A계산여부, 순공사원가적용여부, 낙찰하한가,
             면허제한코드, 공고기관코드, 주공종명,
             공고기관명, 공고기관점수,
             공사지역, 공사지역점수,
             키워드, 키워드점수
         FROM train_datasheet
     )
SELECT TOP 100
    CONCAT(
            'http://192.168.0.54:5000/api/predict?',
            'bssamt=', 기초금액,
            '&lowerrt=', 낙찰하한률,
            '&companycnt=', 참여업체수,
            '&a=', 간접비,
            '&orgamt=', 순공사원가,
            '&limitlic=', 면허제한코드,
            '&instt=', 공고기관명,
            '&area=', 공사지역,
            '&keyword=', 키워드
    ) AS 쿼리,
    입찰번호, 입찰차수,
    기초금액률, 낙찰하한률, 참여업체수, 최종낙찰률, 업체사정률, 예가사정률,
    업체투찰률, 예가투찰률, 투찰률오차,
    기초금액, 예정금액, 순공사원가, 기초예정금액, 낙찰금액, 간접비, A계산여부, 순공사원가적용여부, 낙찰하한가,
    면허제한코드, 공고기관코드, 주공종명,
    공고기관명, 공고기관점수,
    공사지역, 공사지역점수,
    키워드, 키워드점수
FROM test_datasheet
ORDER BY 입찰번호 DESC;


-- select * from bd_cst_main

-- select * from cm_user;
-- select * from cm_area;
-- select * from cm_area_cd cac;
-- select * from cm_area_cd cac
-- left join cm_area ca on cac.area_cl_nm = ca.prtcpt_psbl_rgn_nm;

-- select ca.BID_NTCE_NO, ca.BID_NTCE_ORD, SUM(ISNULL(TRY_CAST(cac.AREA_CL_CD AS BIGINT),0)*1000) AS 면허제한코드
-- from cm_area ca
-- left join cm_area_cd cac
--     on ca.prtcpt_psbl_rgn_nm = cac.area_cl_nm
-- where area_cl_cd is not null
-- GROUP BY ca.BID_NTCE_NO, ca.BID_NTCE_ORD;



-- SELECT
--     ca.BID_NTCE_NO,
--     ca.BID_NTCE_ORD,
--     SUM(TRY_CAST(cac.AREA_CL_CD AS INT) * 1000) AS 면허제한코드
-- FROM cm_area ca
--          LEFT JOIN cm_area_cd cac
--                    ON ca.prtcpt_psbl_rgn_nm = cac.area_cl_nm
-- WHERE cac.AREA_CL_CD IS NOT NULL
-- GROUP BY
--     ca.BID_NTCE_NO,
--     ca.BID_NTCE_ORD;


-- select * from cm_area;
-- select * from CM_LCS;


-- 면허제한코드, 업종제한코드 cd로 바꿔서 숫자로 바꿔 다 더해 계산

