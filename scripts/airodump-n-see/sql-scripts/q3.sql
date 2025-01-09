select CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as ESSID, access_points.Privacy, access_points.Authentication
from access_points 
GROUP BY access_points.ESSID