

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
	offset 2400
	
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

----------------
-----------------
-------------

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


---------------
---------------
------------------

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
	

-----------------
-----------------
------------------


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


-----------------------
---------------------
--------------------------

-- start with empty list
truncate match_contact;

with

contact_paper as (
	select 
		c.name,
		c.email,
		cp.paper_id as pid
	from 
		contact c
	join
		contact_paper cp on c.id = cp.contact_id
	where
		length(trim(name)) > 0
),

match_contact_cte as (
	select 
		mn.*
-- 		a1.name as name1,
-- 		a2.name as name2,
-- 		cp1.email as email1,
-- 		cp1.pid,
-- 		cp2.email as email2,
-- 		cp2.pid
	from 
		match_name mn
	join
		author a1 on a1.id = mn.asid1
	join
		author a2 on a2.id = mn.asid2
	join
		contact_paper cp1 on cp1.name = a1.name and cp1.pid = mn.pid1
	join
		contact_paper cp2 on cp2.name = a2.name and cp2.pid = mn.pid2
	where 
		cp1.email = cp2.email
)

insert into 
	match_contact
select
	* 
from 
	match_contact_cte	
;

-- remove duplicates 
delete from 
	match_contact T1
using   
	match_contact T2
where   
	T1.ctid < T2.ctid  -- delete the older versions
    and T1.asid1  = T2.asid1
	and T1.pid1 = T2.pid1
	and T1.asid2 = T2.asid2
	and T1.pid2 = T2.pid2	
;	

-----------------------
-------------------------
-----------------------------

truncate new_match_prob;


------------------------------------------------------
-- update name match default p = 0.25

with prob_match as (
	select 
	*,
	.25 as prob
	from match_name
)

insert into new_match_prob select * from prob_match;


------------------------------------------------------
-- update coauthor match tp = 0.5 and fp = 0.1

with evidence as (
	select 
		mp.asid1,
		mp.pid1,
		mp.asid2, 
		mp.pid2,
		mp.prob
	from 
		new_match_prob mp	
	join
		match_coauthor e on mp.asid1 = e.asid1 and mp.pid1 = e.pid1 and mp.asid2 = e.asid2 and mp.pid2 = e.pid2
)

update 
	new_match_prob mp
set 
	prob = (0.5 * mp.prob)/((0.5 * mp.prob)+(0.1 * (1 - mp.prob)))	
from
	evidence e
where 
	mp.asid1 = e.asid1 and mp.pid1 = e.pid1 and mp.asid2 = e.asid2 and mp.pid2 = e.pid2	
;

------------------------------------------------------
-- update research area match tp = 0.5 and fp = 0.2

with evidence as (
	select 
		mp.asid1,
		mp.pid1,
		mp.asid2, 
		mp.pid2,
		mp.prob
	from 
		new_match_prob mp	
	join
		match_research_area e on mp.asid1 = e.asid1 and mp.pid1 = e.pid1 and mp.asid2 = e.asid2 and mp.pid2 = e.pid2
)

update 
	new_match_prob mp
set 
	prob = (0.5 * mp.prob)/((0.5 * mp.prob)+(0.2 * (1 - mp.prob)))	
from
	evidence e
where 
	mp.asid1 = e.asid1 and mp.pid1 = e.pid1 and mp.asid2 = e.asid2 and mp.pid2 = e.pid2	
;

------------------------------------------------------
-- update subject match tp = 0.5 and fp = 0.01

with evidence as (
	select 
		mp.asid1,
		mp.pid1,
		mp.asid2, 
		mp.pid2,
		mp.prob
	from 
		new_match_prob mp	
	join
		match_subject e on mp.asid1 = e.asid1 and mp.pid1 = e.pid1 and mp.asid2 = e.asid2 and mp.pid2 = e.pid2
)

update 
	new_match_prob mp
set 
	prob = (0.5 * mp.prob)/((0.5 * mp.prob)+(0.01 * (1 - mp.prob)))	
from
	evidence e
where 
	mp.asid1 = e.asid1 and mp.pid1 = e.pid1 and mp.asid2 = e.asid2 and mp.pid2 = e.pid2	
;


----------------------------------------
-- insert into match prob

--truncate match_prob;
insert into 
	match_prob
select
	* 
from 
	new_match_prob
;

----------------------------------------------
--remove duplicates
delete from 
	match_prob T1
using   
	match_prob T2
where   
	T1.ctid < T2.ctid  -- delete the older versions
    and T1.asid1  = T2.asid1
	and T1.pid1 = T2.pid1
	and T1.asid2 = T2.asid2
	and T1.pid2 = T2.pid2	

;
------------------------------------------------------
-- select 
-- 	round(mp.prob, 2) as prob,
-- 	mp.asid1,
-- 	mp.asid2,
-- 	mp.pid1,
-- 	mp.pid2,
-- 	a1.name as name1,
-- 	a2.name as name2,
-- 	p1.title as title1,
-- 	p2.title as title2
-- from match_prob mp
-- join author a1 on mp.asid1 = a1.id
-- join author a2 on mp.asid2 = a2.id
-- join paper p1 on mp.pid1 = p1.id
-- join paper p2 on mp.pid2 = p2.id
-- where prob > .81

select count(*) from match_prob
