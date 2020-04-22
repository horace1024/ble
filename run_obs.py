# Creates a basic BLE Observer
# Check the Observer.py class for more info

import sys
import time
import signal
from datetime import datetime, timedelta

from Observer import Observer


# Create pretty hex string from bytearray
def bytes2Str(byteArray):
    return(''.join("{0:02X}".format(x) for x in byteArray))


# Observe
def main():
    dt = datetime.now()
    print("Started at: %s" % dt)

    # Create Observer
    obs = Observer()
    obs.setupBleStack()

    # Matching address
    adr = 'DC:A6:32:63:50:9A'
    adr = None

    # Counter
    rx = 0

    while(True):
        # Get received advertisements
        ad_structs, rssi, addr = obs.rxParse(match_addr=adr)
        
        # Check for address match and valid reception       
        if rssi is not None and ad_structs is not None and addr is not None:

            # From our Pi only if includes: Name, TX Power
            name = next((ad['data'] for ad in ad_structs if ad['type'] == 0x09), None)
            tx_power = next((ad['data'] for ad in ad_structs if ad['type'] == 0x0A), None)
            # Detect parity bit
            if tx_power is not None:
                if tx_power[0] > 0x80:
                    tx_power = tx_power[0] - 0x80
                else:
                    tx_power = tx_power[0]

            # Log
            if name is not None and tx_power is not None:
                print('%d %s "%s", TX: %ddBm, RSSI: %ddBm' % (rx, addr, name, tx_power, rssi))
            else:
                print('%d %s, RSSI: %ddBm' % (rx, addr, rssi))
            rx += 1



# Program start
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("CTRL-C Detected")
        print("Stopped at: %s" % datetime.now())
        sys.exit()





