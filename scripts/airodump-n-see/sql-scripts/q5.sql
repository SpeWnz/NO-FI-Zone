select DISTINCT CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as ESSID,
	access_points.channel 
from access_points 
where access_points.ESSID not in (SELECT scope_networks.ESSID from scope_networks)
ORDER BY access_points.ESSID, access_points.channel