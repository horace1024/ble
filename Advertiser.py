# BLE Advertiser class

import os
import subprocess
import struct
import time
import sys

from datetime import datetime
from ctypes import (CDLL, get_errno)
from ctypes.util import find_library
from socket import (socket, inet_ntoa, SOCK_DGRAM, AF_INET, AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI, SOL_HCI, HCI_FILTER)


# Advertiser class
class Advertiser:
    def __init__(self):
        self.sock = None
        self.bluez = None
        self.advertising = False

    # Configure bluez stack for advertising, interval in ms
    def setupBleStack(self, name, interval=200):
        print("Configuring BLE Advertiser")

        # Sanity check interval
        if((interval < 100) or (interval >= 10000)):
            print("Advertising interval should be between 100ms and 10s")
            sys.exit()
        else:
            adv_int = int(float(interval)/0.625)
    
        # Must run as root
        if not os.geteuid() == 0:
            print("Script only works as root")
            sys.exit()

        # Find Bluetooth bluez library
        btlib = find_library("bluetooth")
        if not btlib:
            print("Cannot find required Bluetooth libraries, must intall bluez")
            sys.exit()

        # Cycle BLE interface
        self.executeOsCmd('sudo hciconfig hci0 down')
        self.executeOsCmd('sudo hciconfig hci0 up')

        # Create BLE stream and socket
        self.bluez = CDLL(btlib, use_errno=True)
        dev_id = self.bluez.hci_get_route(None)
        self.sock = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI)
        self.sock.bind((dev_id,))

        # The socket HCI filter must be set to receive HCI Events
        hci_filter = struct.pack("<IQH", 0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF, 0)
        self.sock.setsockopt(SOL_HCI, HCI_FILTER, hci_filter)

        # Determine TX power
        self.bluez.hci_send_cmd(self.sock.fileno(), 0x08, 0x0007, 0)
        # Assume no events before this?
        data = bytearray(self.sock.recv(1024))
        tx_pow = data[len(data)-1:len(data)]
        powi = int(tx_pow[0])
        if powi > 0x80:
            powi -= 0x80
        print("TX Power: %ddBm" % powi)
        
        # Create advertising parameters struct
        direct_addr = (0,)*6
        adv_params = [adv_int, adv_int, 0x03, 0x00, 0x00]
        adv_params.extend(direct_addr)
        adv_params.extend((0x07, 0x00))
        cmd = struct.pack("<HHBBB6BBB", *adv_params)
        # Send command
        self.bluez.hci_send_cmd(self.sock.fileno(), 0x08, 0x0006, len(cmd), cmd)
        
        # Generate AD types and format payload
        ad1 = bytearray([len(name)+1, 0x09]) + bytearray(name)
        ad2 = bytearray([len(tx_pow)+1, 0x0A]) + tx_pow
        # Combine all AD blocks and zero pad
        data = ad1 + ad2 + bytearray(32-len(ad1)-len(ad2)-1)
        cmd = struct.pack("<B%dB" % len(data), (len(ad1)+len(ad2)), *data)
        # Send command
        self.bluez.hci_send_cmd(self.sock.fileno(), 0x08, 0x0008, len(cmd),  cmd)

        return True


    # Enable/Disable advertisements
    def enableAdvertisements(self, en=False):
        if en and not self.advertising:
            # Start advertising
            cmd = struct.pack("<B", 0x01)
            self.bluez.hci_send_cmd(self.sock.fileno(), 0x08, 0x000A, 1, cmd)
            self.advertising = True
            print("Advertising enabled")
        elif en and self.advertising:
            # Already advertising
            print("Cannot enable advertising - already advertising, do nothing")
        else:
            # Disable advertising
            cmd = struct.pack("<B", 0x00)
            self.bluez.hci_send_cmd(self.sock.fileno(), 0x08, 0x000A, 1, cmd)
            self.advertising = False
            print("Advertising disabled")



    # Execute shell command on OS
    def executeOsCmd(self, cmd):
        print("Shell command: "+cmd)
        output = subprocess.check_call(cmd, shell=True)
        if(output != 0):
            print(output)


    # Convert byte array to string
    def bytes2Str(self, byteArray):
        return(''.join("{0:02X}".format(x) for x in byteArray))


    # Stop advertising on close
    def __del__(self):
        # Disable advertisements
        self.enableAdvertisements()
