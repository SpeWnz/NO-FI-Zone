from datetime import timedelta

passwordCount = int(input("Password count: "))
performance = int(input("Performance pmk/sec: "))

t = timedelta(seconds=int(passwordCount/performance))
print(t)
