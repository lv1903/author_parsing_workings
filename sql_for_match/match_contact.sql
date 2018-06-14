-- create table match_contact (
-- 	asid1 integer,
-- 	pid1 integer,
-- 	asid2 integer, 
-- 	pid2 integer
-- );

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
	
select * from match_contact





