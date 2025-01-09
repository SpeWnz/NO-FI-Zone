select Probed_ESSIDs, count(Probed_ESSIDs) as "Total Count"
from stations
group by Probed_ESSIDs
ORDER by "Total Count" desc
limit 10;