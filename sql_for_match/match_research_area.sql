-- create table match_research_area (
-- 	asid1 integer,
-- 	pid1 integer,
-- 	asid2 integer, 
-- 	pid2 integer
-- );

-- start with empty list
truncate match_research_area;

with

journal_research_area as (
	select
		js.journal_id as jid, 
		ras.research_area_id as raid
	from
		journal_subject js
	join
		research_area_subject ras on js.subject_id = ras.subject_id
),

match_research_area_cte as (
	select
		mn.*
-- 		p1.journal_id as jid1,
-- 		p2.journal_id as jid2,
-- 		jra1.raid as raid1,
-- 		jra2.raid as raid2
	from 
		match_name mn
	join
		paper p1 on mn.pid1 = p1.id
	join
		paper p2 on mn.pid2 = p2.id
	join
		journal_research_area jra1 on p1.journal_id = jra1.jid 
	join
		journal_research_area jra2 on p2.journal_id = jra2.jid 
	where
		jra1.raid = jra2.raid
)

insert into 
	match_research_area
select
	* 
from 
	match_research_area_cte	
;

-- remove duplicates (where we have more than one shared coauthor)
delete from 
	match_research_area T1
using   
	match_research_area T2
where   
	T1.ctid < T2.ctid  -- delete the older versions
    and T1.asid1  = T2.asid1
	and T1.pid1 = T2.pid1
	and T1.asid2 = T2.asid2
	and T1.pid2 = T2.pid2	
;  	
	
select * from match_research_area

