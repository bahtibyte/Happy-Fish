from logging.handlers import TimedRotatingFileHandler
import logging
from time import sleep
import pathlib
from threading import Timer
from electronics import Electronics
from settings import Settings
from connection import Connection, Stage
from alerts import Alerts
import os

class HappyFish():

    def logSetup (self):
        logger = logging.getLogger('testlog')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt='%(asctime)s [%(filename)-15s %(lineno)-4s %(funcName)15s()] %(levelname)-8s %(message)s', datefmt='%m-%d-%y %H:%M:%S')
        fh = TimedRotatingFileHandler(str(pathlib.Path().absolute())+'/logs/HappyFish.log', when='midnight', interval=1)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger

    def __init__(self):
        self.logger = self.logSetup()

        alerts = Alerts(self.logger)
        alerts.alertInfo('Raspberry Pi: Running HappyFish.py')

        self.mqtt_email = os.environ["MQTT_EMAIL"]
        self.mqtt_password = os.environ["MQTT_PASSWORD"]

        self.logger.info('='*50)
        self.logger.info('Running main script')

        self.settings = Settings(self.logger, False)

        self.electronics = Electronics(self.logger, self.settings)

        self.logger.info('Updating the pwm modules for the first time')
        self.result = self.electronics.updateModule()

        self.reconnect_count = 0

        if self.result == True:
            self.logger.info('PWM modules updated. Electronics working as intended')
        else:
            self.logger.critical('Failed to light up the lab room. Check pwm modules')
            self.logger.critical('Terminating script. Please check hardware')
            alerts = Alerts(self.logger)
            alerts.alertCritical('Raspberry Pi: PWM Module cannot be opened')
            exit()

        self.connection = Connection(self.logger, self.settings, self.mqtt_email, self.mqtt_password)
        self.connection.start()
        self.reconnecting = False

    def start(self):
        try:
            self.logger.info('Running main loop')
            while True:
                sleep(0.5)

                self.electronics.updateModule()

                if not self.reconnecting and self.connection.connection_closed and self.reconnect_count < 5:
                    self.logger.critical('Connection appears to be closed... Ending connection and Will reconnect after 60 seconds')
                    self.connection.end()
                    self.reconnecting = True
                    self.timer = Timer(60, self.reconnect, args=None, kwargs=None)
                    self.timer.start()

        except KeyboardInterrupt:
            self.logger.critical('Script manually terminated')

        self.connection.end()

        self.settings.printConfig()

        self.logger.info('Script ended. Shutting down the lights')
        self.settings.turnAllOff()
        self.result = self.electronics.updateModule()

        if self.result == True:
            self.logger.info('Successfully turned off all the lights')
        else:
            self.logger.critical('Failed to turn off the lights. Unable to communicate with pwm module')

        alerts = Alerts(self.logger)
        alerts.alertCritical('HappyFish script got terminated... Unknown reason')

        self.ended = True
    
    def reconnect(self):
        self.logger.critical('Attempting to reconnect again')
        self.connection = Connection(self.logger, self.settings, self.mqtt_email, self.mqtt_password)
        self.connection.start()
        self.reconnecting = False
        self.reconnect_count = self.reconnect_count + 1