select DISTINCT access_points.ESSID, stations.sta_OUI, oui.vendors.OUI , oui.vendors.Vendor, oui.vendors.Info
from stations join oui.vendors on stations.sta_OUI = oui.vendors.OUI, access_points
where access_points.ESSID in (SELECT scope_networks.ESSID from scope_networks)
and stations.BSSID like "%not associated%"
order by access_points.ESSID;