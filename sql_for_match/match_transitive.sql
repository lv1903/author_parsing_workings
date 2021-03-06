with match_likely as (
	select 
		* 
	from 
		match_prob mp
	where 
	prob > 0.9

)

select 
	mp.*,
	ml1.asid2 as asid_likely1,
	ml1.pid2 as pid_likely1
-- 	ml1.prob as prob_likey1,
-- 	ml2.asid2 as asid_likely2,
-- 	ml2.pid2 as pid_likely2
from 
 	match_prob mp
join
	match_likely ml1 on mp.asid1 = ml1.asid1 and mp.pid1 = ml1.pid1
join
	match_likely ml2 on mp.asid2 = ml2.asid1 and mp.pid2 = ml2.pid1
where 
	ml1.asid2 = ml2.asid2 and ml1.pid2 = ml2.pid2
	and
	mp.pid1 != ml2.pid2 and mp.pid2 != ml1.pid2
order by mp.asid1, pid1, asid2, pid2

-- select * from match_likely
--where pid1 = 369333 or pid2 = 369333