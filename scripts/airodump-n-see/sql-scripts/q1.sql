select * 
from access_points 
where access_points.ESSID in (SELECT scope_networks.ESSID from scope_networks)
order by access_points.ESSID;