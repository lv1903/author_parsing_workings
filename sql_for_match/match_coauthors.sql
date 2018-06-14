-- create table match_coauthor (
-- 	asid1 integer,
-- 	pid1 integer,
-- 	asid2 integer, 
-- 	pid2 integer
-- )

-- start with empty list
truncate match_coauthor;

-- add the author paper pairs that have matching coauthors
with match_coauthor_cte as (
	select
		mn.asid1,
		mn.pid1,
-- 		ap1.author_id as coid1,
-- 		av.asid2 as vid,
		mn.asid2,
		mn.pid2 
-- 		ap2.author_id as coid2
	from 
		match_name mn
	join 
		author_paper ap1 on mn.pid1 = ap1.paper_id
	join 
		author_paper ap2 on mn.pid2 = ap2.paper_id
	join 
		author_variant av on ap1.author_id = av.asid1
	
	where 
 		(
 			mn.asid1 != ap1.author_id
 			and 
 			mn.asid2 != ap2.author_id
 		) and (
 			ap1.author_id = ap2.author_id
 			or
 			av.asid2 = ap2.author_id
 		)
)

insert into 
	match_coauthor 
select 
	* 
from 
	match_coauthor_cte	
;

-- remove duplicates (where we have more than one shared coauthor)
delete from 
	match_coauthor T1
using   
	match_coauthor T2
where   
	T1.ctid < T2.ctid  -- delete the older versions
    and T1.asid1  = T2.asid1
	and T1.pid1 = T2.pid1
	and T1.asid2 = T2.asid2
	and T1.pid2 = T2.pid2	
;  	
	
select * from match_coauthor
