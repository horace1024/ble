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
def main(f):
    dt = datetime.now()
    print("Started at: %s" % dt)

    # Create Observer
    obs = Observer()
    obs.setupBleStack()

    # Define mission
    dist = 5
    numt = 20

    # Matching address
    adr = 'B8:27:EB:67:72:BF'

    # Must use state machine due to blocking socket
    state = 'wait'
    df = datetime.now()
    rxn = 0
    
    while True:
        
        # Get data
        ads, rssi, addr = obs.rxParse(match_addr=adr)
        
        if state == 'wait':
            rxn = 0
            # Wait for input
            dist = input("Enter distance in METRES (float): ")
            print("Capturing %d packets at %.2f metres, please wait..." % (numt, dist))
            f.write("%.2f," % (dist))
            df = datetime.now() + timedelta(seconds=3)
            # Next state
            state = 'clear'
        
        elif state == 'clear':
            if datetime.now() < df:
                state = 'clear'
            else:
                state = 'capture'

        elif state == 'capture':
            if rssi is not None:
                name = next((ad['data'] for ad in ads if ad['type'] == 0x09), None)
                txp = next((ad['data'] for ad in ads if ad['type'] == 0x0A), None)
                if txp is not None:
                    if txp[0] > 0x80:
                        txp = txp[0] - 0x80
                    else:
                        txp = txp[0]
                print('%d %s "%s" %ddBm %ddBm' % (rxn, addr, name, txp, rssi))
                f.write("%.0f" % (rssi))
                rxn += 1
                if rxn < numt:
                    f.write(",")
            # Next state
            if rxn > numt-1:
                state = 'post-capture'
            else:
                state = 'capture'
            

        elif state == 'post-capture':
            f.write("\n")
            print("Distance done")
            state = 'wait'
        

    # Measurement complete
    f.close()
    print("Measurement complete: %s" % datetime.now())


# Program start
if __name__ == "__main__":
    try:
        try:
            f = open('range.csv', 'w')
        except IOError:
            print("Error opening output file")
            sys.exit()
        # Run experiment
        main(f)
    except KeyboardInterrupt:
        print("CTRL-C Detected")
    finally:
        f.close()
        print("Stopped at: %s" % datetime.now())
        sys.exit()





