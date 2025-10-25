WITH basic_bid_info AS (
    SELECT
        a.bid_ntce_no AS 입찰번호,
        a.bid_ntce_ord AS 입찰차수,
        ISNULL(c.bssamt, 0) / 100000000.0 AS 기초금액률,
        ISNULL(a.sucsfbid_lwlt_rate, 0) / 100.0 AS 낙찰하한률,
        ISNULL(b.prtcpt_cnum, 0) AS 참여업체수,
        b.sucsfbid_rate AS 최종낙찰률,
        b.sucsfbid_rate - a.sucsfbid_lwlt_rate AS 낙찰률오차,
        (b.sucsfbid_amt / c.bssamt) * (a.sucsfbid_lwlt_rate / 100.0) AS 업체사정률,
        (b.sucsfbid_amt / c.bssamt) AS 업체투찰률,
        d.plnprc / c.bssamt AS 예가사정률,
        (d.plnprc / c.bssamt) * (a.sucsfbid_lwlt_rate / 100.0) AS 예가투찰률,
        ISNULL(c.bssamt, 0) AS 기초금액,
        ISNULL(d.plnprc, 0) AS 예정금액,
        ISNULL(c.bss_amt_purcnstcst, 0) AS 순공사원가,
        ISNULL(d.bsis_plnprc, 0) AS 기초예정금액,
        b.sucsfbid_amt AS 낙찰금액,
        (ISNULL(c.sfty_mngcst, 0) + ISNULL(c.rtrfund_non, 0) + ISNULL(c.mrfn_health_insrprm, 0) + ISNULL(c.npn_insrprm, 0) + ISNULL(c.odsn_lngtrmrcpr_insrprm, 0) + ISNULL(c.sftyChck_mngcst, 0) + ISNULL(c.qlty_mngcst, 0)) AS 간접비,
        CASE WHEN c.bid_prce_calclA_yn = 'Y' THEN 1 ELSE 0 END AS A계산여부,
        CASE WHEN c.bss_amt_purcnstcst > 0 THEN 1 ELSE 0 END AS 순공사원가적용여부,
        ISNULL(a.ntce_instt_cd, '')  AS 공고기관코드,
        CASE WHEN a.main_cnstty_nm = '' THEN '-' ELSE ISNULL(a.main_cnstty_nm, '-') END AS 주공종명,
        a.bid_ntce_nm AS 입찰명,
        a.ntce_instt_nm AS 공고기관명,
        0.00000000 AS 키워드점수,
        a.BID_NTCE_DT AS 공고일자,
        a.OPENG_DT AS 개찰일시
    FROM
        bd_cst_main a
            INNER JOIN ad_cst b ON a.bid_ntce_no = b.bid_ntce_no AND a.bid_ntce_ord = b.bid_ntce_ord
            INNER JOIN bd_cst_prc c ON a.bid_ntce_no = c.bid_ntce_no AND a.bid_ntce_ord = c.bid_ntce_ord
            INNER JOIN ad_cst_pprt d ON a.bid_ntce_no = d.bid_ntce_no AND a.bid_ntce_ord = d.bid_ntce_ord AND d.compno_rsrvtn_prce_sno = 1
            INNER JOIN (
            SELECT bid_ntce_no, MAX(bid_ntce_ord) AS bid_ntce_ord
            FROM bd_cst_main
            GROUP BY bid_ntce_no
        ) e ON a.bid_ntce_no = e.bid_ntce_no AND a.bid_ntce_ord = e.bid_ntce_ord
    WHERE
        ISNULL(a.sucsfbid_lwlt_rate, '87.745') != 0
),
     train_datasheet AS (
         SELECT
             입찰번호, 입찰차수,
             기초금액률, 낙찰하한률, 참여업체수, 최종낙찰률, 업체사정률, 예가사정률,
             업체투찰률,
             (ROUND(((예정금액 - 간접비) * 낙찰하한률) + 간접비, 0) / 기초금액) AS 예가투찰률,
             (업체투찰률 - ((ROUND(((예정금액 - 간접비) * 낙찰하한률) + 간접비, 0) / 기초금액))) * 100 AS 투찰률오차,
             기초금액, 예정금액, 순공사원가, 기초예정금액, 낙찰금액, 간접비, A계산여부, 순공사원가적용여부,
             ROUND(((예정금액 - 간접비) * 낙찰하한률) + 간접비, 0) AS 낙찰하한가,
             공고기관코드, 주공종명,
             공고기관명, 0.00000000 AS 공고기관점수,
             0.000000000 AS 공사지역점수,
             입찰명 + ' ' + 주공종명 AS 키워드, 키워드점수, 공고일자, 개찰일시
         FROM basic_bid_info
         WHERE 업체투찰률 IS NOT NULL
     ),
     LicenseAgg AS (
         SELECT
             main.BID_NTCE_NO,
             main.BID_NTCE_ORD,
             STUFF((
                       SELECT ',' + CAST(sub.lcns_lmt_cd AS VARCHAR)
                       FROM cm_lcs sub
                       WHERE sub.BID_NTCE_NO = main.BID_NTCE_NO
                         AND sub.BID_NTCE_ORD = main.BID_NTCE_ORD
                       FOR XML PATH(''), TYPE
                   ).value('.', 'NVARCHAR(MAX)'), 1, 1, '') AS 면허제한코드
         FROM cm_lcs main
         GROUP BY main.BID_NTCE_NO, main.BID_NTCE_ORD
     ),
     AreaAgg AS (
         SELECT
             a.BID_NTCE_NO,
             a.BID_NTCE_ORD,
             STUFF((
                       SELECT ',' + c.area_cl_nm
                       FROM cm_area sub_a
                                JOIN cm_area_cd c ON sub_a.PRTCPT_PSBL_RGN_NM = c.area_cl_nm
                       WHERE sub_a.BID_NTCE_NO = a.BID_NTCE_NO
                         AND sub_a.BID_NTCE_ORD = a.BID_NTCE_ORD
                       FOR XML PATH(''), TYPE
                   ).value('.', 'NVARCHAR(MAX)'), 1, 1, '') AS 공사지역
         FROM cm_area a
         GROUP BY a.BID_NTCE_NO, a.BID_NTCE_ORD
     )
SELECT
    t.입찰번호, t.입찰차수,
    t.기초금액률, t.낙찰하한률, t.참여업체수, t.최종낙찰률, t.업체사정률, t.예가사정률,
    t.업체투찰률,
    (ROUND(((t.예정금액 - t.간접비) * t.낙찰하한률) + t.간접비, 0) / t.기초금액) AS 예가투찰률,
    (t.업체투찰률 - ((ROUND(((t.예정금액 - t.간접비) * t.낙찰하한률) + t.간접비, 0) / t.기초금액))) * 100 AS 투찰률오차,
    t.기초금액, t.예정금액, t.순공사원가,
    t.기초예정금액, t.낙찰금액, t.간접비,
    t.A계산여부, t.순공사원가적용여부,
    ROUND(((t.예정금액 - t.간접비) * t.낙찰하한률) + t.간접비, 0) AS 낙찰하한가,
    l.면허제한코드, t.공고기관코드, t.주공종명,
    t.공고기관명, 0.00000000 AS 공고기관점수,
    a.공사지역, 0.000000000 AS 공사지역점수,
    t.키워드, t.키워드점수, t.키워드점수, t.공고일자, t.개찰일시,
    'http://192.168.0.54:5000/api/predict?' +
    'bssamt=' + CAST(t.기초금액 AS VARCHAR) +
    '&lowerrt=' + CAST(t.낙찰하한률 AS VARCHAR) +
    '&companycnt=' + CAST(t.참여업체수 AS VARCHAR) +
    '&a=' + CAST(t.간접비 AS VARCHAR) +
    '&orgamt=' + CAST(t.순공사원가 AS VARCHAR) +
    '&limitlic=' + ISNULL(l.면허제한코드, '') +
    '&instt=' + t.공고기관명 +
    '&area=' + ISNULL(a.공사지역, '') +
    '&keyword=' + t.키워드 AS 예측_URL
FROM
    train_datasheet t
        LEFT JOIN LicenseAgg l
                  ON t.입찰번호 = l.BID_NTCE_NO AND t.입찰차수 = l.BID_NTCE_ORD
        LEFT JOIN AreaAgg a
                  ON t.입찰번호 = a.BID_NTCE_NO AND t.입찰차수 = a.BID_NTCE_ORD;