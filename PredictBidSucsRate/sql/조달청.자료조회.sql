select 
bid_ntce_no as 입찰번호
,bid_ntce_ord as 입찰차수
,bid_ntce_nm as 입찰명
,main_cnstty_nm as 주공종명
,prearng_prce_dcsn_mthd_nm as 예정가격결정방법
,sucsfbid_mthd_nm as 낙찰방법
,tot_prdprc_num as 총예가건수
,drwt_prdprc_num as 추첨예가건수
,bdgt_amt as 예산액
,main_cnstty_cnstwk_prearng_amt as 주공종공사예정금액
,presmpt_prce as 추정가격
,govsply_amt as 관급금액
,sucsfbid_lwlt_rate as 낙찰하한률
,bid_begin_dt as 공고일시
,bid_clse_dt as 마감일시
,openg_dt as 개찰일시
from tb_public_bid_const


select * from tb_public_bid_const where rgst_ty_nm='조달청 또는 나라장터 자체 공고건' order by bid_ntce_dt  desc

----------------------------------------------------------------------------------
select 
	#a.bid_restrict_licenseNm + ' ' + a.bid_ntce_nm + ' ' + a.ntce_instt_nm + ' ' + a.cntrct_cncls_mthd_nm + ' ' + b.prtcpt_cnum as txt
	concat(a.bid_restrict_licenseNm , ' ' , a.bid_ntce_nm , ' ' , a.ntce_instt_nm , ' ' , a.cntrct_cncls_mthd_nm) as 키워드
	#,a.bid_ntce_nm
	#,a.ntce_instt_nm
	#,a.cntrct_cncls_mthd_nm 
	,b.prtcpt_cnum as 참여업체수
from 
	tb_public_bid_const a
	inner join tb_const_choice b on (a.bid_ntce_no=b.bid_ntce_no and a.bid_ntce_ord=b.bid_ntce_ord)
where nvl(a.bid_restrict_licenseNm,'') !=''
order by a.openg_dt desc
-----------------------------------------------------------------------------------

select nvl(null,0) as v


select 
a.bid_ntce_no as 입찰번호
,a.bid_ntce_ord as 입찰차수
/*
,a.bid_ntce_nm as 입찰명
,a.main_cnstty_nm as 주공종명
,a.prearng_prce_dcsn_mthd_nm as 예정가격결정방법
,a.sucsfbid_mthd_nm as 낙찰방법

,nvl(c.bssamt,0) as 기초금액
*/
,nvl(c.bssamt,0.00000000)/100000000 as 기초금액률
,nvl(c.bss_amt_purcnstcst,0)/100000000 as 순공사원가율
/*
,nvl(c.rsrvtn_prce_rng_bgn_rate,0)/100 as 예비가격범위시작률
,nvl(c.rsrvtn_prce_rng_end_rate,0)/100 as 예비가격범위종료률
,c.bid_prce_calclA_yn as 입찰가격산식A여부
,nvl(c.bss_amt_purcnstcst,0)/100000000 as 순공사원가
,c.qlty_mngcstA_obj_yn as 품질관리비A적용대상


,a.tot_prdprc_num as 총예가건수
,a.drwt_prdprc_num as 추첨예가건수
*/
,nvl(a.sucsfbid_lwlt_rate,0.00000000)/100 as 낙찰하한률
,nvl(b.prtcpt_cnum,0.00000000)/10000 as 참여업체수
,nvl(b.sucsfbid_amt,0.00000000)/100000000 as 최종낙찰금액
,nvl(b.sucsfbid_rate,0.00000000)/100.00000000 as 최종낙찰률

/*
,a.bid_begin_dt as 공고일시
,a.bid_clse_dt as 마감일시
,a.openg_dt as 개찰일시
*/
from tb_public_bid_const a
inner join tb_const_choice b on (a.bid_ntce_no=b.bid_ntce_no and a.bid_ntce_ord=b.bid_ntce_ord)
inner join TB_PUBLIC_BID_CONST_BASIC_AMOUNT c on (a.bid_ntce_no=c.bid_ntce_no and a.bid_ntce_ord=c.bid_ntce_ord)
where nvl(a.sucsfbid_lwlt_rate,'')!='' and nvl(c.bss_amt_purcnstcst,0)!=0

select * from TB_PUBLIC_BID_CONST where 1=1 limit 0,100

select * from (
	select 
		row_number() over (partition by bid_ntce_no order by bid_ntce_ord desc) as sno, 
		nvl(bid_restrict_licenseCd,'0000') as bid_restrict_licenseCd, 
		ntce_instt_nm, 
		main_cnstty_nm 
	from TB_PUBLIC_BID_CONST
) t where t.sno=1
	and limit 0, 100

select 
/*a.bid_ntce_no as 입찰번호
,a.bid_ntce_ord as 입찰차수
,*/
c.bssamt/100000000 as 기초금액률
,a.sucsfbid_lwlt_rate/100 as 낙찰하한률
,b.prtcpt_cnum/1000 as 참여업체수
,b.sucsfbid_amt / (c.bssamt * (a.sucsfbid_lwlt_rate/100)) as 사정률
/*,b.sucsfbid_amt as 낙찰금액
,round(c.bssamt * (b.sucsfbid_amt / (c.bssamt * (a.sucsfbid_lwlt_rate/100))) * (a.sucsfbid_lwlt_rate/100),0) as 투찰금액
,b.sucsfbid_rate as 최종낙찰률
*/
from tb_public_bid_const a
inner join tb_const_choice b on (a.bid_ntce_no=b.bid_ntce_no and a.bid_ntce_ord=b.bid_ntce_ord)
inner join TB_PUBLIC_BID_CONST_BASIC_AMOUNT c on (a.bid_ntce_no=c.bid_ntce_no and a.bid_ntce_ord=c.bid_ntce_ord)
where nvl(a.sucsfbid_lwlt_rate,'')!=''

#-----------------------------------------------------------------------------------------------------------
	select 
		a.bid_ntce_no as 입찰번호
		,a.bid_ntce_ord as 입찰차수
		,nvl(c.bssamt,0.00000000) as 기초금액률
		,nvl(a.sucsfbid_lwlt_rate,0.00000000) as 낙찰하한률
		,nvl(b.prtcpt_cnum,0.00000000) as 참여업체수
		,b.sucsfbid_rate as 최종낙찰률
		,b.sucsfbid_rate-a.sucsfbid_lwlt_rate as 낙찰률오차
		,b.sucsfbid_amt / (c.bssamt * (a.sucsfbid_lwlt_rate/100)) as 업체사정률
		,d.plnprc/c.bssamt as 예가사정률 
		,(b.sucsfbid_amt / (c.bssamt * (a.sucsfbid_lwlt_rate/100)))-(d.plnprc/c.bssamt) as 사정률오차
		,c.bssamt as 기초금액
		,d.plnprc as 예정금액
		,c.bssamt*(d.plnprc/c.bssamt) as 예정금액A
		,round(b.sucsfbid_amt/d.plnprc,5)*100 as 업체투찰률
		,b.sucsfbid_rate
		,b.sucsfbid_amt
		,round(b.sucsfbid_amt/round(b.sucsfbid_amt/d.plnprc,5),0) as 예정금액A
		,nvl(c.bss_amt_purcnstcst,0) as 순공사원가		
		,nvl(d.bsis_plnprc,0.00000000) as 기초예정금액
		,round(nvl(d.plnprc,0.00000000)*(a.sucsfbid_lwlt_rate/100),0) as 낙찰하한가
		,b.sucsfbid_amt as 낙찰금액
		,case when c.bid_prce_calclA_yn='Y' then 1 else 0 end as A계산여부  
		,case when c.bss_amt_purcnstcst > 0 then 1 else 0 end as 순공사원가적용여부
		#c.qlty_mngcstA_obj_yn
		,nvl(a.bid_restrict_licenseCd,'0000') as bid_restrict_licenseCd, 
		,a.ntce_instt_nm, 
		,a.main_cnstty_nm 		
	from 
		tb_public_bid_const a
		inner join tb_const_choice b on (a.bid_ntce_no=b.bid_ntce_no and a.bid_ntce_ord=b.bid_ntce_ord)
		inner join TB_PUBLIC_BID_CONST_BASIC_AMOUNT c on (a.bid_ntce_no=c.bid_ntce_no and a.bid_ntce_ord=c.bid_ntce_ord)
		inner join TB_CONST_AMOUNT_DETAIL d on (a.bid_ntce_no=d.bid_ntce_no and a.bid_ntce_ord=d.bid_ntce_ord and d.compno_rsrvtn_prce_sno=1)
		inner join ( select bid_ntce_no, max(bid_ntce_ord) as bid_ntce_ord  from tb_public_bid_const group by bid_ntce_no ) e on (a.bid_ntce_no=e.bid_ntce_no and a.bid_ntce_ord=e.bid_ntce_ord )
	where 
		nvl(a.sucsfbid_lwlt_rate,'')!='' #and nvl(c.bss_amt_purcnstcst,0)!=0
		and c.bid_prce_calclA_yn='Y'
		#and  a.rgst_ty_nm='조달청 또는 나라장터 자체 공고건'
	order by a.bid_ntce_no desc

#-------------------------------------------------------------------------------------------
with basic_bid_info as (
	select 
		a.bid_ntce_no as 입찰번호
		,a.bid_ntce_ord as 입찰차수
		,nvl(c.bssamt,0)/100000000 as 기초금액률
		,nvl(a.sucsfbid_lwlt_rate,0)/100 as 낙찰하한률
		,nvl(b.prtcpt_cnum,0)*1000 as 참여업체수
		,b.sucsfbid_rate as 최종낙찰률
		,b.sucsfbid_rate-a.sucsfbid_lwlt_rate as 낙찰률오차
		,(b.sucsfbid_amt / c.bssamt) * (a.sucsfbid_lwlt_rate/100) as 업체사정률
		,(b.sucsfbid_amt / c.bssamt) as 업체투찰률
		,d.plnprc/c.bssamt as 예가사정률 
		,(d.plnprc / c.bssamt) * (a.sucsfbid_lwlt_rate/100) AS 예가투찰률
		#,(b.sucsfbid_amt / (c.bssamt * (a.sucsfbid_lwlt_rate/100)))-(d.plnprc/c.bssamt) as 사정률오차
		#,c.bssamt * (b.sucsfbid_amt / c.bssamt) * (a.sucsfbid_lwlt_rate/100) as 업체투찰액1
		#,c.bssamt * (d.plnprc / c.bssamt) * (a.sucsfbid_lwlt_rate/100) as 예가투찰액1
		,nvl(c.bssamt,0) as 기초금액
		,nvl(d.plnprc,0) as 예정금액
		,nvl(c.bss_amt_purcnstcst,0) as 순공사원가		
		,nvl(d.bsis_plnprc,0) as 기초예정금액
		,b.sucsfbid_amt as 낙찰금액
		,(nvl(c.sfty_mngcst,0)+nvl(c.rtrfund_non,0)+nvl(c.mrfn_health_insrprm,0)+nvl(c.npn_insrprm,0)+nvl(c.odsn_lngtrmrcpr_insrprm,0)+nvl(c.sftyChck_mngcst,0)+nvl(c.qlty_mngcst,0)) as 간접비
		,case when c.bid_prce_calclA_yn='Y' then 1 else 0 end as A계산여부  
		,case when c.bss_amt_purcnstcst > 0 then 1 else 0 end as 순공사원가적용여부
		#c.qlty_mngcstA_obj_yn
		#,nvl(a.bid_restrict_licenseCd,'0000') as 면허제한코드
		,(convert((gfn_split(nvl(a.bid_restrict_licenseCd,'0000'), ',', 1)),signed)*1000 + convert((gfn_split(nvl(a.bid_restrict_licenseCd,'0000'), ',', 2)),signed)*1000 + convert((gfn_split(nvl(a.bid_restrict_licenseCd,'0000'), ',', 3)),signed)*1000)/1000000 as 면허제한코드
		#,convert((gfn_split(nvl(a.bid_restrict_licenseCd,'0000'), ',', 1)),signed)*100 AS 면허제한A
		#,convert((gfn_split(nvl(a.bid_restrict_licenseCd,'0000'), ',', 2)),signed)*100 AS 면허제한B
		#,convert((gfn_split(nvl(a.bid_restrict_licenseCd,'0000'), ',', 3)),signed)*100 AS 면허제한C		
		,convert(nvl(a.ntce_instt_cd, '0'),signed) / 1000000 as 공고기관코드
		,a.main_cnstty_nm as 주공종명			
	from 
		tb_public_bid_const a
		inner join tb_const_choice b on (a.bid_ntce_no=b.bid_ntce_no and a.bid_ntce_ord=b.bid_ntce_ord)
		inner join TB_PUBLIC_BID_CONST_BASIC_AMOUNT c on (a.bid_ntce_no=c.bid_ntce_no and a.bid_ntce_ord=c.bid_ntce_ord)
		inner join TB_CONST_AMOUNT_DETAIL d on (a.bid_ntce_no=d.bid_ntce_no and a.bid_ntce_ord=d.bid_ntce_ord and d.compno_rsrvtn_prce_sno=1)
		inner join ( select bid_ntce_no, max(bid_ntce_ord) as bid_ntce_ord  from tb_public_bid_const group by bid_ntce_no ) e on (a.bid_ntce_no=e.bid_ntce_no and a.bid_ntce_ord=e.bid_ntce_ord )
	where 
		nvl(a.sucsfbid_lwlt_rate,'')!='' #and nvl(c.bss_amt_purcnstcst,0)!=0
		#and  a.rgst_ty_nm='조달청 또는 나라장터 자체 공고건'
	order by a.bid_ntce_no desc
)
select  
	입찰번호,	입찰차수,	
	기초금액률,	낙찰하한률,	참여업체수,	최종낙찰률,	업체사정률,	예가사정률,	
	round(업체투찰률*10000,0) AS 업체투찰률,	
	round((round(((예정금액-간접비)*낙찰하한률)+간접비,0)/기초금액)*10000,0) as 예가투찰률,	
	round((업체투찰률 - ((round(((예정금액-간접비)*낙찰하한률)+간접비,0)/기초금액)))*10000,0) as 투찰률오차, 
	#round(업체투찰률*기초금액,0),	round(예가투찰액1,0),	
	기초금액,	예정금액,	순공사원가,	기초예정금액,	낙찰금액,	간접비, A계산여부, 순공사원가적용여부,
	round(((예정금액-간접비)*낙찰하한률)+간접비, 0) as 낙찰하한가,
	면허제한코드, 공고기관코드, 주공종명
from basic_bid_info where 업체투찰률 is not null

	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
select 
/*a.bid_ntce_no as 입찰번호
,a.bid_ntce_ord as 입찰차수
,*/
c.bssamt as 기초금액률
,a.sucsfbid_lwlt_rate as 낙찰하한률
,b.prtcpt_cnum as 참여업체수
,b.sucsfbid_amt / (c.bssamt * (a.sucsfbid_lwlt_rate/100)) as 업체사정률
,b.sucsfbid_amt as 낙찰금액
,round(c.bssamt * (b.sucsfbid_amt / (c.bssamt * (a.sucsfbid_lwlt_rate/100))) * (a.sucsfbid_lwlt_rate/100),0) as 투찰금액
,b.sucsfbid_rate as 최종낙찰률
,c.bid_prce_calclA_yn

from tb_public_bid_const a
inner join tb_const_choice b on (a.bid_ntce_no=b.bid_ntce_no and a.bid_ntce_ord=b.bid_ntce_ord)
inner join TB_PUBLIC_BID_CONST_BASIC_AMOUNT c on (a.bid_ntce_no=c.bid_ntce_no and a.bid_ntce_ord=c.bid_ntce_ord)
where nvl(a.sucsfbid_lwlt_rate,'')!=''

#-----------------------------------------------------------------------------------------------------------
최대낙찰률오차	최소낙찰률오차	평균낙찰률오차		최대사정률오차	최소사정률오차	평균사정률오차
1.55		0.001		0.6422147403	0.017685586	0.000011475	0.0073189976
#-----------------------------------------------------------------------------------------------------------
/*
max(낙찰률오차) as 최대낙찰률오차
,min(낙찰률오차) as 최소낙찰률오차
,avg(낙찰률오차) as 평균낙찰률오차
,max(사정률오차) as 최대사정률오차
,min(사정률오차) as 최소사정률오차
,avg(사정률오차) as 평균사정률오차
*/

select 
max(낙찰률오차) as 최대낙찰률오차
,min(낙찰률오차) as 최소낙찰률오차
,avg(낙찰률오차) as 평균낙찰률오차
,max(사정률오차) as 최대사정률오차
,min(사정률오차) as 최소사정률오차
,avg(사정률오차) as 평균사정률오차
from (

	select 
		a.bid_ntce_no as 입찰번호
		,a.bid_ntce_ord as 입찰차수
		,nvl(c.bssamt,0)/100000000 as 기초금액률
		,nvl(a.sucsfbid_lwlt_rate,0)/100 as 낙찰하한률
		,nvl(b.prtcpt_cnum,0)/10000 as 참여업체수
		,b.sucsfbid_rate as 최종낙찰률
		,b.sucsfbid_rate-a.sucsfbid_lwlt_rate as 낙찰률오차
		,(b.sucsfbid_amt / c.bssamt) * (a.sucsfbid_lwlt_rate/100) as 업체사정률
		,d.plnprc/c.bssamt as 예가사정률 
		,(d.plnprc / c.bssamt) * (a.sucsfbid_lwlt_rate/100) AS 예가투찰률
		#,(b.sucsfbid_amt / (c.bssamt * (a.sucsfbid_lwlt_rate/100)))-(d.plnprc/c.bssamt) as 사정률오차
		,c.bssamt * (b.sucsfbid_amt / c.bssamt) * (a.sucsfbid_lwlt_rate/100) as 업체투찰액1
		,c.bssamt * (d.plnprc / c.bssamt) * (a.sucsfbid_lwlt_rate/100) as 예가투찰액1
		,nvl(c.bssamt,0) as 기초금액
		,nvl(d.plnprc,0) as 예정금액
		,nvl(c.bss_amt_purcnstcst,0) as 순공사원가		
		,nvl(d.bsis_plnprc,0) as 기초예정금액
		,round(nvl(d.plnprc,0)*(a.sucsfbid_lwlt_rate/100),0) as 낙찰하한가
		,b.sucsfbid_amt as 낙찰금액
		,(nvl(c.sfty_mngcst,0)+nvl(c.rtrfund_non,0)+nvl(c.mrfn_health_insrprm,0)+nvl(c.npn_insrprm,0)+nvl(c.odsn_lngtrmrcpr_insrprm,0)+nvl(c.sftyChck_mngcst,0)+nvl(c.qlty_mngcst,0)) as 간접비
		,case when c.bid_prce_calclA_yn='Y' then 1 else 0 end as A계산여부  
		,case when c.bss_amt_purcnstcst > 0 then 1 else 0 end as 순공사원가적용여부
		#c.qlty_mngcstA_obj_yn
	from 
		tb_public_bid_const a
		inner join tb_const_choice b on (a.bid_ntce_no=b.bid_ntce_no and a.bid_ntce_ord=b.bid_ntce_ord)
		inner join TB_PUBLIC_BID_CONST_BASIC_AMOUNT c on (a.bid_ntce_no=c.bid_ntce_no and a.bid_ntce_ord=c.bid_ntce_ord)
		inner join TB_CONST_AMOUNT_DETAIL d on (a.bid_ntce_no=d.bid_ntce_no and a.bid_ntce_ord=d.bid_ntce_ord and d.compno_rsrvtn_prce_sno=1)
		inner join ( select bid_ntce_no, max(bid_ntce_ord) as bid_ntce_ord  from tb_public_bid_const group by bid_ntce_no ) e on (a.bid_ntce_no=e.bid_ntce_no and a.bid_ntce_ord=e.bid_ntce_ord )
	where 
		nvl(a.sucsfbid_lwlt_rate,'')!='' #and nvl(c.bss_amt_purcnstcst,0)!=0
		#and  a.rgst_ty_nm='조달청 또는 나라장터 자체 공고건'
	order by a.bid_ntce_no desc
		
) t where 1=1
	and (t.낙찰률오차 >= 0 or t.사정률오차 >= 0) 
	and (낙찰률오차 < (0.7751243247006349*2) and 낙찰률오차 > 0)
	and (사정률오차 < (0.008846118712522638*2) and 사정률오차 > (0.0000000052658302*1.2))
	#t.기초금액 = 347320000

	
	
	
	
	
	
	
	
	
	
select * from tb_const_choice
select * from TB_PUBLIC_BID_CONST_BASIC_AMOUNT
select * from TB_CONST_AMOUNT_DETAIL


select * from TB_PUBLIC_BID_CONST_BASIC_AMOUNT
where bid_ntce_no in (select distinct bid_ntce_no from tb_public_bid_const)

select * from TB_CONST_CHOICE where bid_ntce_no in (select distinct bid_ntce_no from tb_public_bid_const)
select * from TB_CONST_AMOUNT_DETAIL where bid_ntce_no in (select distinct bid_ntce_no from tb_public_bid_const)


select distinct replace(replace(replace(prcbdr_nm, '주식회사', ''),'(주)',''),' ','') as cpynm from TB_PUBLIC_BID_CONST_OPEN;
select * from TB_PUBLIC_BID_CONST_OPEN where prcbdr_bizno ='1018163743'