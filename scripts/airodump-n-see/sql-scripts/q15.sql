select DISTINCT CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as "Detected SSID",
	access_points.BSSID, access_points.Privacy, access_points.Authentication, oui.vendors.OUI, oui.vendors.Vendor, oui.vendors.Info, 
	oui.ssid_charsets.ssid as "Default SSID", oui.ssid_charsets.total_length as "Default PW Length", oui.ssid_charsets.default_charset as "Default PW Charset"
from access_points,oui.vendors, oui.ssid_charsets
where access_points.ap_OUI = oui.vendors.OUI 
and lower(oui.vendors.Vendor) = lower(oui.ssid_charsets.vendor_shortname)
and (access_points.Authentication like "%PSK%" or access_points.Authentication like "%SAE%")
order by access_points.ESSID