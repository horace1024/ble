# Bluetooth Low Energy
BLE Advertiser and Observer classes for Python based on bluez library

## Design
These scripts are built for Raspberry Pi but may work on other Linux platforms. Rather than using BluePy, these scripts are based directly on Bluez, the official Linux Bluetooth C libraries. Python calls to the underlying C libraries is achieved through ctypes. 

## Installation
The following packages should be installed on your system:
```bash
sudo apt update
sudo apt install -y bluetooth pi-bluetooth bluez libglib2.0-dev python-dbus python-gobject libbluetooth-dev
```

## Testing
Ideally use two devices such as two Raspberry Pis. Failing that, use one Pi as the Advertiser and use a phone as the Observer.
Clone this repo to each pi. Install the requirements above. Then on the advertiser run:
```bash
sudo python run_adv.py
```
and on the observer run:
```bash
sudo python run_obs.py
```
You should see advertisement packets being received on the observer.

## Editing
In run_obs.py you can change the MAC address that will be filtered in the Observer.py class. If you're testing in a busy environment this is useful.

In run_adv.py you can change the interval at which advertisements will be sent. You can also set the name of the device which is attached to the advertisement in a AD Structure with Bluetooth number 0x09.

