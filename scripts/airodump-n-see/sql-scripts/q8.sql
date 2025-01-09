select stations.Station_MAC, stations.Probed_ESSIDs 
from stations 
where stations.Probed_ESSIDs in (SELECT scope_networks.ESSID from scope_networks) 
and stations.BSSID like "%not associated%" order by stations.Probed_ESSIDs