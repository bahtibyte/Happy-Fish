from time import time,sleep

start = time()

while int(time() - start) < 5:
    print(time())
    sleep(1)

'''
from time import sleep

sunrise = '07:00'
sunset =  '17:28'
duration = 1

sunrise_start = (int(sunrise[:sunrise.index(':')]) * 3600) + (int(sunrise[sunrise.index(':')+1:]) * 60)

sunset_start = (int(sunset[:sunset.index(':')]) * 3600) + (int(sunset[sunset.index(':')+1:]) * 60)

duration_seconds = duration * 60


print('sunrise_start:',sunrise_start)
print('sunset_start:',sunset_start)
print('duration_seconds:',duration_seconds)

x = 0

while True:
    now = datetime.now()
    seconds = (now.hour * 3600) + (now.minute * 60) + (now.second)


    x += 1

    if seconds < sunrise_start:
        print(x,'I am OFF')
    elif seconds < sunrise_start + duration_seconds:
        print(x,'Sunrise')
    elif seconds < sunset_start:
        print(x,'I am ON')
    elif seconds < sunset_start + duration_seconds:
        print(x,'Sunset')
    else:
        print(x,'I am OFF')
    

    if x > 100:
        break

    sleep(1)
'''