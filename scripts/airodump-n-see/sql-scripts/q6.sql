select DISTINCT CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as ESSID,
	access_points.Privacy, access_points.Authentication from access_points where lower(access_points.ESSID) not in (SELECT scope_networks.ESSID from scope_networks)  order by access_points.ESSID