select DISTINCT Probed_ESSIDs as "Unique probed SSIDs"
from stations
where Probed_ESSIDs not NULL
order by Probed_ESSIDs asc