-- create table match_name (
-- 	asid1 integer,
-- 	pid1 integer,
-- 	asid2 integer, 
-- 	pid2 integer
-- )


truncate match_name;

with 

new_paper as (
	select 
		author_id as asid,
		paper_id as pid
	from 
		author_paper
	order by paper_id desc, author_id desc
	limit 100
	offset 1300
	
),

match_name_cte as (
	
	select 
		np.asid as asid1,
		np.pid as pid1,
-- 		av.asid1 as vid1,
-- 		av.asid2 as vid2,
		ap.author_id as asid2,
		ap.paper_id as pid2
	from
		new_paper np
	join
		author_variant av on np.asid = av.asid1
	join
		author_paper ap on av.asid2 = ap.author_id
	where 
		np.pid != ap.paper_id

)

insert into 
	match_name 
select 
	* 
from 
	match_name_cte;

-- remove duplicates (where we have more than one variant)
delete from 
	match_name T1
using   
	match_name T2
where   
	T1.ctid < T2.ctid  -- delete the older versions
    and T1.asid1  = T2.asid1
	and T1.pid1 = T2.pid1
	and T1.asid2 = T2.asid2
	and T1.pid2 = T2.pid2	
;  	

--create index a1_idx on match_name (asid1);
-- create index a2_idx on match_name (asid2);
-- create index a1a2_idx on match_name (asid1, asid2);

;
	
select * from match_name ;
-- select count(*) from match_name;
--select count(*) from match_name_cte

