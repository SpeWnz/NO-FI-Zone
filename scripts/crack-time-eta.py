from datetime import timedelta

passwordCount = int(input("Password count: "))
ssidCount = int(input("SSID count: "))

total = passwordCount * ssidCount

performance = int(input("Performance pmk/sec: "))

t = timedelta(seconds=int(total/performance))
print(t)
