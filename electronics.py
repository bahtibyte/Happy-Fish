from Adafruit_PCA9685 import PCA9685
from schedule import Schedule, Stages
import sys

class Electronics:
    """
    A class used to deal with the electronics in the system 

    ...

    Attributes
    ----------
    settings : Settings
        an object to keep track of each shelves configuration
    schedule : Schedule
        Tracks which stage of the day it is. Each shelf follows
        the default schedule, unless owner has manual override
    led_pins : dict
        shelf name mapped to pin on pwm module
    rgb_pins : dict
        rack name mapped to pins on pwm module
    pwm_led, pwm_rgb : PCA9685
        16 channel pwm module

    Methods
    -------
    updateModule()
        Refreshes all the shelves with the current light configuration
    getBrightness(brightness, scaled)
        Adjusts the brightnesss to match the requirements of PCA9685
    """

    MAX_DUTY_CYCLE = 4095

    def __init__(self, logger, settings):
        """
        Initializes the LED pin out. Room to change shelf mappings.
        Constructs the 16 bit pwm modules. 
        Creates the Schedule to track the stage of the day.

        Parameters
        ----------
        logger : Logger
            Logs and saves the data seperated by day
        settings : Settings
            Reference to the shelves configuration. Contains LED and RGB configs
        """
        self.logger = logger
        self.settings = settings

        self.logger.info('Initializing Electronics object')
    
        self.led_pins = {
            'A1' : 11,
            'A2' : 10,
            'A3' : 9,
            'B1' : 0,
            'B2' : 1,
            'B3' : 2,
            'C1' : 3,
            'C2' : 4,
            'C3' : 5
        }

        self.rgb_pins = {
            'A' : [8, 9, 10],
            'B' : [0, 1, 2],
            'C' : [4, 5, 6]
        }

        self.logger.debug('LED pin out ' + str(self.led_pins))
        self.logger.debug('RGB pin out ' + str(self.rgb_pins))

        try:
            self.pwm_led = PCA9685(address=0x40)
            self.pwm_rgb = PCA9685(address=0x41)

            # Higher the frequency, the smoother the light looks
            self.pwm_led.set_pwm_freq(120)
            self.pwm_rgb.set_pwm_freq(120)

            self.logger.info('Initialized the LED and RGB pwm modules')
        except:
            self.logger.critical('Unable to access I/O pwm module')
            self.logger.critical('Electronic initializing failed')
        else:
            self.logger.info('Electronic Initializing finished')

        self.schedule = Schedule(logger)

    def updateModule(self):
        """ Will update each shelf's lights accordingly.
        If owner has manual control of any shelf, the light is set to what was defined by the owner.  
        If owner does not have manual control, the lights will follow the scheduled sunrise and sunset
        """

        try:
            # The adjusted brightness depending on the current stage of the day
            percentage = self.schedule.getBrightnessPercentage()
            brightness = self.getBrightness(self.schedule.getBrightnessPercentage(), 1)

            # Iterates through each available shelf
            for shelf in self.led_pins.keys():

                # Manual LED override is enabled for the current shelf. Sets the brightnesss to what the user requested
                if self.settings.leds[shelf][0] == True:
                    brightness = percentage * self.settings.leds[shelf][1] / 100.0 * self.MAX_DUTY_CYCLE
                    self.pwm_led.set_pwm(self.led_pins[shelf], 0, int(brightness))

                #In case Rack 3 has rgb priority
                elif '3' in shelf:
                    rack = shelf[0]
                    if self.settings.rgbs[rack][0] == True:
                        self.pwm_led.set_pwm(self.led_pins[shelf], 0, 0)
                    else:
                        brightness = percentage * self.MAX_DUTY_CYCLE
                        self.pwm_led.set_pwm(self.led_pins[shelf], 0, int(brightness))

                # Stays on default schedule. Follows the sunset and sunrise
                else:
                    brightness = percentage * self.MAX_DUTY_CYCLE
                    self.pwm_led.set_pwm(self.led_pins[shelf], 0, int(brightness))

            # Iterates through each available rack
            for rack in self.rgb_pins.keys():

                # Manual RGB override is enabled for the current rack, 3rd shelf
                if self.settings.rgbs[rack][0] == True and self.schedule.stage != Stages.pre_sun_rise and self.schedule.stage != Stages.post_sun_set:
                    colors = self.settings.rgbs[rack][1]
                    self.pwm_rgb.set_pwm(self.rgb_pins[rack][0], 0, self.getBrightness(colors[0], 255))
                    self.pwm_rgb.set_pwm(self.rgb_pins[rack][1], 0, self.getBrightness(colors[1], 255))
                    self.pwm_rgb.set_pwm(self.rgb_pins[rack][2], 0, self.getBrightness(colors[2], 255))

                # No manual control of rack. Goes back default schedule. i.e off
                else:
                    self.pwm_rgb.set_pwm(self.rgb_pins[rack][0], 0, 0)
                    self.pwm_rgb.set_pwm(self.rgb_pins[rack][1], 0, 0)
                    self.pwm_rgb.set_pwm(self.rgb_pins[rack][2], 0, 0)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.logger.critical(f'Unable to update the pwm modules. [{exc_type} line # {exc_tb.tb_lineno}]')
            return False
        else:
            return True

    def getBrightness(self, brightness, scale):
        """Given raw brightness and the scale, this function will
        return a adjusted brightness out of MAX_DUTY_CYCLE

        Parameters
        ----------
        brightness : int, float
            The ratio of brightness out of scale
        scale : int
            The maximum value of brightness
        Returns
        -------
        int
            Adjusted brightness between 0 (inclusive) to MAX_DUTY_CYCLE (inclusive)
        """
        return int(((float(brightness)) / float(scale)) * self.MAX_DUTY_CYCLE)
