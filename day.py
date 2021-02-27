from datetime import datetime
import time

class Day:

    #Define the time for sunrise and sunset here.
    sunrise_time = '7:00'
    sunset_time = '19:00'

    #Define how long each rise/set should last for in minutes
    duration = 30

    #PWM max duty cycle is 4095
    max_duty_cycle = 4095
    
    def __init__(self):
        rise_index = self.sunrise_time.index(":")
        self.sunrise = int(self.sunrise_time[0:rise_index]) * 60 + int(self.sunrise_time[rise_index+1:])
        
        set_index = self.sunset_time.index(":")
        self.sunset = int(self.sunset_time[0:set_index]) * 60 + int(self.sunset_time[set_index+1:])

    def isSunrise(self):
        self.now = datetime.now()
        mins_since = self.getMinutesSince(self.sunrise)
        return mins_since >= 0 and mins_since < self.duration

    def isSunset(self):
        self.now = datetime.now()
        mins_since = self.getMinutesSince(self.sunset)
        return mins_since >= 0 and mins_since < self.duration

    '''
    A day has night time, sunrise time, day time, sunset time. Then it loops back to the beginning.
    This function will return the brightness depending on which stage it is in. 
    '''
    def getBrightness(self):
        self.now = datetime.now()

        #Checks if the current day is in sunrise mode
        if (self.isSunrise()):
            total_seconds = self.getMinutesSince(self.sunrise) * 60 + self.now.second
            return self.scaleBrightness(total_seconds, self.duration*60)

        #Checks if the current day is in sunset mode
        elif (self.isSunset()):
            total_seconds = self.getMinutesSince(self.sunset) * 60 + self.now.second
            return self.max_duty_cycle - self.scaleBrightness(total_seconds, self.duration*60)

        #If minutes since sunrise is negative, it means that it is night time        
        elif (self.getMinutesSince(self.sunrise) <= 0 or self.getMinutesSince(self.sunset+self.duration) >= 0):
            return 0

        #Since it isn't night time, sunset time, or sunrise time, it means it is day time
        return self.max_duty_cycle

    def scaleBrightness(self, brightness, high):
        return (int) ((float(brightness) / float(high)) * self.max_duty_cycle)

    def getMinutesSince(self, minute):
        return self.now.hour * 60 + self.now.minute - minute
