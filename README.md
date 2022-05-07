
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

## Install Libraries
```sh
sudo pip3 install adafruit-pca9685
sudo pip3 install paho-mqtt
sudo pip3 install twilio
```

