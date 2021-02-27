from twilio.rest import Client
import os

class Alerts:
        
    account_sid = os.environ("TWILIO_ACCOUNT_SID")
    auth_token = os.environ("TWILIO_AUTH_TOKEN")

    number = os.environ("TWILIO_NUMBER")
    to = os.environ("TWILIO_MY_NUMBER")

    def __init__(self, logger):
        #self.client = Client(self.account_sid, self.auth_token)
        self.logger = logger
        self.logger.info('FALSE Twilio Alert System initialized')

    def alertInfo(self, msg):
        self.logger.info(f'FALSE Sending alertInfo. MSG=[{msg}]')
        #message = self.client.messages.create(body=f'[INFO] {msg}', from_=self.number, to=self.to)
        #self.logger.info(f'Alert SID {message.sid}')

    def alertCritical(self, msg):
        self.logger.critical(f'FALSE Sending alertCritical. MSG=[{msg}]')
        #message = self.client.messages.create(body=f'[CRITICAL] {msg}', from_=self.number, to=self.to)
        #self.logger.critical(f'Alert SID {message.sid}')
