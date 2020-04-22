# BLE Observer class

import os
import subprocess
import struct
import sys

from datetime import datetime
from ctypes import (CDLL, get_errno)
from ctypes.util import find_library
from socket import (socket, inet_ntoa, SOCK_DGRAM, AF_INET, AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI, SOL_HCI, HCI_FILTER)



# Observer class
class Observer:
    def __init__(self):
        self.sock = None
        self.bluez = None

    # Configure bluez stack for scanning
    def setupBleStack(self):
        print("Configuring BLE Observer")

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

        # Create Unix socket with BLE Host Controller Interface (Raw)
        self.bluez = CDLL(btlib, use_errno=True)
        dev_id = self.bluez.hci_get_route(None)
        self.sock = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI)
        self.sock.bind((dev_id,))

        # Configure scanning and socket filter for certain HCI Events
        self.bluez.hci_le_set_scan_parameters(self.sock.fileno(), 0, 0x10, 0x10, 0, 0, 1000)
        hci_filter = struct.pack("<IQH", 0x00000010, 0x4000000000000000, 0)
        self.sock.setsockopt(SOL_HCI, HCI_FILTER, hci_filter)
        self.bluez.hci_le_set_scan_enable(self.sock.fileno(), 1, 0, 1000)


    # Recieve data from socket and parse
    def rxParse(self, match_addr=None):
        # Get data from socket, blocking
        data = bytearray(self.sock.recv(1024))
        str = self.bytes2Str(data)

        # Match RX packet against HCI Event, LE Advertising Report
        if((data[0] != 0x04) or (data[1] != 0x3E) or (data[3] != 0x02)):
            print("Other HCI packet type, discard")
            return (None,)*3

        # Extract address
        addr = ':'.join("{0:02X}".format(x) for x in data[12:6:-1])
        
        # Match address if given
        if match_addr is not None:
            if match_addr != addr:
                return (None,)*3

        # Get RSSI
        rssiStr = str[(len(str)-2):len(str)]
        rssi = int('0x'+rssiStr, 0)-255

        # Obtain advertisement length and sanity check
        payload = data[13:len(data)-1]
        if((len(payload)-1) != int(payload[0])):
            print("Length error decoding payload")
            return (None,)*3
        pay_len = int(payload[0])
        
        # Extract the AD Structures from advertisement payload
        adi = 1
        ads = []
        while adi < pay_len:
            ad_len = payload[adi]
            ad_type = payload[adi+1]
            ad_data = payload[adi+2:adi+ad_len+1]
            ads.append({'len':ad_len, 'type':ad_type, 'data':ad_data})
            adi = adi + ad_len + 1
            #print("AD %d length: %d, type: 0x%02X" % (len(ads), ad_len, ad_type))

        # Return AD structures and RSSI
        return ads, rssi, addr


    # Execute shell command on OS
    def executeOsCmd(self, cmd):
        print("Shell command: "+cmd)
        output = subprocess.check_call(cmd, shell=True)
        if(output != 0):
            print(output)


    # Convert byte array to string
    def bytes2Str(self, byteArray):
        return(''.join("{0:02X}".format(x) for x in byteArray))


   
