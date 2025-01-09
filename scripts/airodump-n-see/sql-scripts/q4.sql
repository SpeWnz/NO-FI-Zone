select DISTINCT access_points.ESSID, access_points.channel 
from access_points 
where access_points.ESSID in (SELECT scope_networks.ESSID from scope_networks)
ORDER BY access_points.ESSID, access_points.channel