
# Installation Guide

## Prepare your Raspberry Pi
[Getting Started with your Raspberry Pi](https://projects.raspberrypi.org/en/projects/raspberry-pi-getting-started/)

Plug the SD Card in your Raspberry Pi and connect your Pi to a screen, mouse and a keyboard. Check the connection twice before plugging the power.

## Starting the setup

Make sure you have access to internet and update/upgrade your fresh Raspbian install.

Update your Pi first. Open up a terminal, and do the following:
```sh
sudo apt update -y
sudo apt full-upgrade -y
sudo apt install git
```

## Configure I2c
https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c

## Install Libraries
```sh
sudo pip3 install adafruit-pca9685
sudo pip3 install paho-mqtt
sudo pip3 install twilio
```

## Clone the repo
Can be cloned anywhere but preferribly in the /home/pi
```sh
git clone https://github.com/bahtibyte/happy-fish
```

## Environment variables
The following environment variables are needeed to run the program
```sh
export MQTT_EMAIL=""
export MQTT_PASSWORD=""
export TWILIO_ACCOUNT_SID=""
export TWILIO_AUTH_TOKEN=""
export TWILIO_NUMBER=""
export TWILIO_MY_NUMBER=""
```

## Running the program
cd into happy-fish folder and run the main file.
```sh
python3 main.py
```


