select DISTINCT access_points.ESSID, stations.sta_OUI, oui.vendors.Vendor, oui.vendors.Info
from stations join oui.vendors on stations.sta_OUI = oui.vendors.OUI, access_points
where access_points.ESSID not in (SELECT scope_networks.ESSID from scope_networks)
and access_points.Authentication like "%MGT%"
order by access_points.ESSID;