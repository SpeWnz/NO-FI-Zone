select CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as ESSID,
	access_points.BSSID, access_points.Privacy, access_points.Authentication, oui.vendors.OUI , oui.vendors.Vendor, oui.vendors.Info
from access_points join oui.vendors on access_points.ap_OUI = oui.vendors.OUI
order by access_points.ESSID;