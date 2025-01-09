# crea la tabella per gli ap
CREATE TABLE access_points (BSSID TEXT,  First_time_seen TEXT,  Last_time_seen TEXT,  channel INTEGER,  Speed INTEGER,  Privacy TEXT,  Cipher TEXT,  Authentication TEXT,  Power INTEGER,  num_beacons INTEGER,  num_IV INTEGER,  LAN_IP TEXT,  ID_length INTEGER,  ESSID TEXT,  Key TEXT,  ap_OUI TEXT)

# crea la tabella per le stations
CREATE TABLE stations (Station_MAC TEXT,  First_time_seen TEXT,  Last_time_seen TEXT,  Power INTEGER,  num_of_packets INTEGER,  BSSID TEXT,  Probed_ESSIDs TEXT)

# crea la tabella per le reti in scope
CREATE TABLE "scope_networks" (
	"ESSID"	TEXT,
	"Privavcy"	TEXT,
	"Authentication"	TEXT
);

# inseirmento automatico degli AP in scope
insert into scope_networks
select DISTINCT access_points.ESSID, access_points.Privacy, access_points.Authentication 
from access_points 
where lower(access_points.ESSID) like "%NAME_HERE%" and access_points.ESSID not in (select scope_networks.ESSID from scope_networks)
order by access_points.ESSID;


# 1 - tutti dati degli ap in scope
select * 
from access_points 
where access_points.ESSID in (SELECT scope_networks.ESSID from scope_networks)
order by access_points.ESSID;

# 2 - dati "essenziali" degli ap in scope
select DISTINCT access_points.ESSID, access_points.Privacy, access_points.Authentication 
from access_points 
where access_points.ESSID in (SELECT scope_networks.ESSID from scope_networks)
order by access_points.ESSID;

# 3 - ssids unique con dati "essenziali"
select CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as ESSID, access_points.Privacy, access_points.Authentication
from access_points 
GROUP BY access_points.ESSID

# 4 - canali usati da SSID in scope
select DISTINCT access_points.ESSID, access_points.channel 
from access_points 
where access_points.ESSID in (SELECT scope_networks.ESSID from scope_networks)
ORDER BY access_points.ESSID, access_points.channel

# 5 - canali usati da SSID fuori scope
select DISTINCT CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as ESSID,
	access_points.channel 
from access_points 
where access_points.ESSID not in (SELECT scope_networks.ESSID from scope_networks)
ORDER BY access_points.ESSID, access_points.channel

# 6 - ssids estranei 
select DISTINCT CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as ESSID,
	access_points.Privacy, access_points.Authentication from access_points where lower(access_points.ESSID) not in (SELECT scope_networks.ESSID from scope_networks)  order by access_points.ESSID

# 7 - ssid estranei di tipo "wpa2 enterprise"
select DISTINCT CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as ESSID,
	access_points.Privacy, access_points.Authentication 
	from access_points 
	where lower(access_points.ESSID) not in (SELECT scope_networks.ESSID from scope_networks)
	and access_points.Authentication like "%MGT%"
	order by access_points.ESSID


# 8 - probe request afferenti a ap in scope (client "not associated" che cercavano reti del cliente)
select stations.Station_MAC, stations.Probed_ESSIDs 
from stations 
where stations.Probed_ESSIDs in (SELECT scope_networks.ESSID from scope_networks) 
and stations.BSSID like "%not associated%" order by stations.Probed_ESSIDs

# controllo incrociato per ouis (bisogna fare attach db)
select CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as ESSID,
	access_points.BSSID, access_points.Privacy, access_points.Authentication, oui.vendors.OUI , oui.vendors.Vendor, oui.vendors.Info
from access_points join oui.vendors on access_points.ap_OUI = oui.vendors.OUI
order by access_points.ESSID

## oppure
select CASE access_points.ESSID
	WHEN NULL then '(hidden)'
	WHEN '' then '(hidden)'
	WHEN ' ' then '(hidden)'
	ELSE access_points.ESSID
	END as ESSID,
	access_points.BSSID, access_points.Privacy, access_points.Authentication, oui.vendors.OUI , oui.vendors.Vendor, oui.vendors.Info
from access_points,oui.vendors
where access_points.ap_OUI = oui.vendors.OUI
order by access_points.ESSID


# incrocia tutti gli oui con tutti i rispetti ssid e default charsets
select *
from vendors, ssid_charsets
where lower(vendors.Vendor) = lower(ssid_charsets.vendor_shortname)
order by vendors.Vendor


# quali ssid e default charset non abbiamo ancora censito?
select * 
from ssid_charsets
where ssid_charsets.vendor_shortname not in 
(
select ssid_charsets.vendor_shortname
from vendors, ssid_charsets
where lower(vendors.Vendor) = lower(ssid_charsets.vendor_shortname)
)


# vendor(s) chiamati xxxx
select *
from vendors
where lower(vendors.Vendor) like "xxxx"