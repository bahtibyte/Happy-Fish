
class Settings:
    
    def __init__(self, logger, dummy):
        
        self.logger = logger
        self.dummy = dummy
        
        self.dummy_str = ''

        if self.dummy:
            self.dummy_str = 'dummy '
            

        if not dummy:
            self.logger.info('Setting initial configurations for LEDs and RGBs')

        self.leds = {
            'A1' : [False, 0],
            'A2' : [False, 0],
            'A3' : [False, 0],
            'B1' : [False, 0],
            'B2' : [False, 0],
            'B3' : [False, 0],
            'C1' : [False, 0],
            'C2' : [False, 0],
            'C3' : [False, 0]
        }

        self.rgbs = {
            'A' : [False, [0, 0, 0], 'RGBA(0,0,0, 255)'],
            'B' : [False, [0, 0, 0], 'RGBA(0,0,0, 255)'],
            'C' : [False, [0, 0, 0], 'RGBA(0,0,0, 255)']
        }

        if not dummy:
            self.printConfig()

    def turnAllOff(self):
        for shelf in self.leds.keys():
            self.leds[shelf][0] = True
            self.leds[shelf][1] = 0
        for rack in self.rgbs.keys():
            self.rgbs[rack][0] = False


    def led_control(self, shelf, control):
        before = self.leds[shelf][0]
        self.leds[shelf][0] = str(control) == 'True'
        self.logger.debug(self.dummy_str+'Shelf ['+shelf+'] control changed from \''+str(before)+'\' to \''+str(control)+'\'')
        
    def led_brightness(self, shelf, brightness):
        before = self.leds[shelf][1]
        self.leds[shelf][1] = int(brightness)
        self.logger.debug(self.dummy_str+'Shelf ['+shelf+'] brightness changed from \''+str(before)+'\' to \''+str(brightness)+'\'')

    def rgb_control(self, rack, control):
        before = self.rgbs[rack][0]
        self.rgbs[rack][0] = str(control) == 'True'
        self.logger.debug(self.dummy_str+'Rack ['+rack+'] control changed from \''+str(before)+'\' to \''+str(control)+'\'')

    def rgb_color(self, rack, color):
        before = self.rgbs[rack][1].copy()
        formatted = color[5:len(color)-1].split(",")
        self.rgbs[rack][1][0] = int(formatted[0])
        self.rgbs[rack][1][1] = int(formatted[1])
        self.rgbs[rack][1][2] = int(formatted[2])
        self.rgbs[rack][2] = color
        self.logger.debug(self.dummy_str+'Rack ['+rack+'] color changed from \''+str(before)+'\' to \''+str(self.rgbs[rack][1])+'\'')

    def printConfig(self):
        self.logger.debug(self.dummy_str+'LEDs config '+str(self.leds))
        self.logger.debug(self.dummy_str+'RGBs config '+str(self.rgbs))
