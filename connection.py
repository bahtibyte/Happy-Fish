import paho.mqtt.client as mqtt
from datetime import datetime
from threading import Thread
from time import sleep, time
from settings import Settings
from alerts import Alerts

class Stage:
    ignore = 'Ignore'
    retained = 'Retained'
    listening = 'Listening'

class Connection:

    broker = 'mqtt.dioty.co'
    rgb_default = 'RGBA(0,0,0, 255)'

    # Define when to time out, in seconds
    TIMEOUT = 10

    def __init__(self, logger, settings, email, pwd):

        self.logger = logger
        self.settings = settings

        self.client = mqtt.Client('python1')
        self.client.username_pw_set(username=email, password=pwd)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.established_connection = False
        self.is_connecting = False
        self.failed_connection = False
        self.connection_closed = False

        self.root = '/'+email+'/'
        self.root_len = len(self.root)

        self.led_control_topic = self.root + 'led/control/'
        self.led_brightness_topic = self.root + 'led/brightness/'
        self.rgb_control_topic = self.root + 'rgb/control/'
        self.rgb_color_topic = self.root + 'rgb/color/'

        self.stage = Stage.ignore

        self.currently_listening = False
        self.current_thread = None
        self.last_color = None

        self.last_started = datetime.now()

        self.logger.info('Initialized a connection with broker \''+self.broker+'\' with username \''+email+'\'')
    
    def start(self, happyfish):
        self.logger.info('Attempting to connect to MQTT broker')

        self.happyfish = happyfish

        self.connection_thread = Thread(target=self.connect, args=())
        self.connection_thread.start()

    def connect(self):
        
        self.client.connect(self.broker)
        self.client.loop_start()

        self.is_connecting = True

        count = 0

        while not self.established_connection and self.is_connecting:

            if count > self.TIMEOUT and not self.established_connection:
                self.logger.critical('Connection with broker timed out. Aborting connection')            
                self.is_connecting = False
                self.failed_connection = True

            if not self.established_connection:
                count += 1
                self.logger.info('Waiting for connection... Attempt '+str(count))

            sleep(1)

        if self.failed_connection:
            self.logger.critical('FAILED to connect with MQTT broker')
            self.end()

        if self.established_connection:
            self.established()

    def established(self):
        self.logger.info('Connection is established with the MQTT broker')
        
        self.logger.debug('Switching stage to RETAINED')
        self.stage = Stage.retained

        self.logger.info('Creating dummy settings for retained data')
        self.dummy_settings = Settings(self.logger, True)

        self.dummy_settings.printConfig()

        self.logger.info('Subscribing to root topic \''+self.root+'#\'')
        self.client.subscribe(self.root+'#')

        sleep(2)
        self.logger.info('Retrieved all retained messages')
        self.dummy_settings.printConfig()

        self.stage = Stage.ignore
        self.logger.info('Fixing conflicting retained settings')
        self.fix_conflicts()

        sleep(1)
        self.logger.info('Final dummy settings')
        self.dummy_settings.printConfig()

        self.stage = Stage.listening
        self.settings.leds = self.dummy_settings.leds.copy()
        self.settings.rgbs = self.dummy_settings.rgbs.copy()

        self.logger.info('Cloned dummy settings to local settings')
        self.settings.printConfig()

    def end(self):
        self.logger.info('Ending and stoppping any form of connection left with the broker')
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        self.is_connecting = False
        if rc == 0:
            self.established_connection = True
            self.logger.info('Connected with MQTT broker, result code: '+str(rc))
            self.happyfish.reconnect_delay = 60
            alerts = Alerts(self.logger)
            alerts.alertInfo('Raspberry Pi connected to MQTT successfully')
        else:
            self.established_connection = False
            self.failed_connection = True
            self.logger.critical('Bad connection, result code: '+str(rc))
            self.happyfish.reconnect_delay = self.happyfish.reconnect_delay * 2
            alerts = Alerts(self.logger)
            alerts.alertCritical(f'Raspberry Pi could NOT connect to MQTT. Bad Connection. RC {rc}')

    def on_disconnect(self, client, userdata, flags, rc=0):
        self.logger.critical('Connection disconnected, return code: '+str(rc))
        self.happyfish.reconnect_delay = self.happyfish.reconnect_delay * 2
        self.connection_closed = True
        self.time_ended = time()
        alerts = Alerts(self.logger)
        alerts.alertCritical(f'RPi disconnected from the MQTT server. RC {rc}')

    def on_message(self, client, userdata, message):
        if self.stage == Stage.ignore:
            self.on_ignore(message)
        if self.stage == Stage.retained:
            self.on_retained(message)
        if self.stage == Stage.listening:
            self.on_listening(message)

    def on_ignore(self, message):
        self.logger.info(f'Ignoring TOPIC [{message.topic}] MESSAGE [{message.payload}]')
    
    def on_retained(self, message):
        self.logger.info(f'Retained TOPIC [{message.topic}] MESSAGE [{message.payload}]')
        try:
            if message.topic:
                topics = message.topic[self.root_len:].split('/')
                msg = self.format(str(message.payload))

                if len(topics) == 3:
                    if topics[0] == 'led':
                        if topics[1] == 'control':
                            self.dummy_settings.led_control(topics[2], msg)
                        if topics[1] == 'brightness':
                            self.dummy_settings.led_brightness(topics[2], msg)
                    if topics[0] == 'rgb':
                        if topics[1] == 'control':
                            self.dummy_settings.rgb_control(topics[2], msg)
                        if topics[1] == 'color':
                            self.dummy_settings.rgb_color(topics[2], msg)

        except Exception as e:
            self.logger.critical('Unable to parse the incoming topic')
            self.logger.critical('Exception: '+str(e))
    
    def on_listening(self, message):
        self.logger.info(f'Listening TOPIC [{message.topic}] MESSAGE [{message.payload}]')
        
        try:
            if message.topic:
                topics = message.topic[self.root_len:].split('/')
                msg = self.format(str(message.payload))

                if len(topics) == 3:
                    if topics[0] == 'led':
                        if topics[1] == 'reset':
                            self.led_reset(topics[2])
                        if topics[1] == 'control':
                            self.led_control(topics[2], msg == 'True')
                        if topics[1] == 'brightness':
                            self.led_brightness(topics[2], int(msg))
                    if topics[0] == 'rgb':
                        if topics[1] == 'reset':
                            self.rgb_reset(topics[2])
                        if topics[1] == 'control':
                            self.rgb_control(topics[2], msg == 'True')
                        if topics[1] == 'color':
                            self.rgb_color(topics[2], str(msg))

        except Exception as e:
            self.logger.critical('Unable to parse the incoming topic')
            self.logger.critical('Exception: '+str(e))

    def format(self, message):
        return message[2:len(message)-1]   

    def fix_conflicts(self):
        for rack in self.dummy_settings.rgbs.keys():
            if self.dummy_settings.rgbs[rack][0]:
                shelf = rack + '3'
                if self.dummy_settings.leds[shelf][0] == True:
                    self.publish_led_control(shelf, False)
                    self.dummy_settings.led_control(shelf, False)
                if self.dummy_settings.leds[shelf][1] != 0:
                    self.publish_led_brightness(shelf, 0)
                    self.dummy_settings.led_brightness(shelf, 0)
            else:
                color = self.dummy_settings.rgbs[rack][1]
                if color[0] != 0 or color[1] != 0 or color[2] != 0:
                    self.publish_rgb_color(rack, self.rgb_default)
                    self.dummy_settings.rgb_color(rack, self.rgb_default)
        
        for shelf in self.dummy_settings.leds.keys():
            if not self.dummy_settings.leds[shelf][0]:
                if self.dummy_settings.leds[shelf][1] != 0:
                    self.publish_led_brightness(shelf, 0)
                    self.dummy_settings.led_brightness(shelf, 0)
        
        self.logger.info('Finished fixing conflicting settings')

    def led_reset(self, shelf):
        self.logger.info(f'Incoming request LED reset for shelf \'{shelf}\'')
        self.publish_led_control(shelf, False)
        self.publish_led_brightness(shelf, 0)

    def led_control(self, shelf, control):
        self.logger.info(f'Incoming request LED control shelf \'{shelf}\' control \'{control}\'')

        if control:
            if '3' in shelf:
                rack = shelf[0]
                if self.settings.rgbs[rack][0]:
                    self.logger.info(f'Illegal request to control shelf \'{shelf}\'. Settings: {self.settings.rgbs[rack]}')
                    self.antiInterference()
                    self.publish_led_control(shelf, False)
                else:
                    self.settings.led_control(shelf, control)
            else:
                self.settings.led_control(shelf, control)
        else:
            if self.settings.leds[shelf][1] != 0:
                self.settings.led_brightness(shelf, 0)
                self.publish_led_brightness(shelf, 0)
            
            self.settings.led_control(shelf, control)

    def led_brightness(self, shelf, brightness):
        self.logger.info(f'Incoming request LED brightness shelf\'{shelf} btight \'{brightness}')

        if not self.settings.leds[shelf][0] and brightness != 0:
            self.logger.info(f'Illegal request to change brightness for shelf \'{shelf}\'. Settings: {self.settings.leds[shelf]}')
            self.antiInterference()
            self.publish_led_brightness(shelf, 0)
        else:
            self.settings.led_brightness(shelf, brightness)

    def rgb_reset(self, rack):
        self.logger.info(f'Incoming request RGB reset for rack \'{rack}\'')
        self.publish_rgb_control(rack, False)
        self.publish_rgb_color(rack, self.rgb_default)

    def rgb_control(self, rack, control):
        self.logger.info(f'Incoming request RGB control for rack \'{rack}\' control \'{control}\'')

        if control:
            shelf = rack + '3'
            if self.settings.leds[shelf][0]:
                self.led_reset(shelf)
        else:
            color = self.settings.rgbs[rack][1]
            if color[0] != 0 or color[1] != 0 or color[2] != 0:
                self.publish_rgb_color(rack, self.rgb_default)

        self.settings.rgb_control(rack, control)
    
    def rgb_color(self, rack, color):
        self.logger.info(f'Incoming request RGB color for rack \'{rack}\' color \'{color}\'')
        
        if color == self.settings.rgbs[rack][2]:
            self.logger.info(f'Rack {rack} is already {color}')
            return

        self.last_color = str(rack) + '/' + str(color)

        if not self.currently_listening:
            self.logger.info('Creating a new rgb thread')
            self.current_thread = Thread(target=self.rgb_color_thread, args=(rack,))
            self.currently_listening = True
            self.current_thread.start()
    
    def rgb_color_thread(self, rack):
        self.logger.info(f'RGB color listener thread started. Listening for rgb rack {rack}')
        start = time()

        tracking = self.last_color

        while int(time() - start) == 0:
            if self.last_color[0] != rack:
                break
                
            if tracking != self.last_color:
                tracking = self.last_color
        
        self.logger.info(f'RGB color listener thread ended. Rack {rack}\'s final color {tracking[2:]}')
        self.currently_listening = False
        
        raw_color = tracking[2:]

        if self.settings.rgbs[rack][0] == False and raw_color != self.rgb_default:
            self.antiInterference()
            self.settings.rgb_color(rack, self.rgb_default)
            self.publish_rgb_color(rack, self.rgb_default)
        else:
            self.settings.rgb_color(rack, raw_color)

    def publish_led_control(self, shelf, control):
        self.client.publish(self.led_control_topic + shelf, str(control), 0, retain=True)
        self.antiTimeout()

    def publish_led_brightness(self, shelf, value):
        self.client.publish(self.led_brightness_topic + shelf, str(value), 0, retain=True)
        self.antiTimeout()

    def publish_rgb_control(self, rack, control):
        self.client.publish(self.rgb_control_topic + rack, str(control), 0, retain=True)
        self.antiTimeout()

    def publish_rgb_color(self, rack, color):
        self.client.publish(self.rgb_color_topic + rack, color, 0, retain=True)
        self.antiTimeout()

    def antiTimeout(self):
        sleep(0.1)
    
    def antiInterference(self):
        sleep(0.5)