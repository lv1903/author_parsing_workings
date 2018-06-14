-- create table match_subject (
-- 	asid1 integer,
-- 	pid1 integer,
-- 	asid2 integer, 
-- 	pid2 integer
-- );

-- start with empty list
truncate match_subject;

with

match_subject_cte as (
	select
		mn.*
-- 		p1.journal_id as jid1,
-- 		p2.journal_id as jid2,
-- 		js1.subject_id as sid1,
-- 		js2.subject_id as sid2
	from 
		match_name mn
	join
		paper p1 on mn.pid1 = p1.id
	join
		paper p2 on mn.pid2 = p2.id
	join
		journal_subject js1 on p1.journal_id = js1.journal_id 
	join
		journal_subject js2 on p2.journal_id = js2.journal_id
	where
		js1.subject_id = js2.subject_id
)

insert into 
	match_subject
select
	* 
from 
	match_subject_cte	
;

-- remove duplicates 
delete from 
	match_subject T1
using   
	match_subject T2
where   
	T1.ctid < T2.ctid  -- delete the older versions
    and T1.asid1  = T2.asid1
	and T1.pid1 = T2.pid1
	and T1.asid2 = T2.asid2
	and T1.pid2 = T2.pid2	
;	
	
select * from match_subject

