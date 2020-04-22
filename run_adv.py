# Creates a basic BLE Advertiser
# Check the Advertiser.py class for more info

import sys
import time
from datetime import datetime, timedelta

from Advertiser import Advertiser


# Advertise
def main():
    dt = datetime.now()
    print("Started at: %s" % dt)

    # Create advertiser
    adv = Advertiser()
    
    # Initiate BLE stack
    if adv.setupBleStack('Pi Range Tester 2', interval=1000):

        # Start advertising
        adv.enableAdvertisements(en=True)

        # Advertise for n seconds
        time.sleep(600)

        # Disable advertisements
        adv.enableAdvertisements(en=False)
    
    # Stop
    print("Stopped at: %s" % datetime.now())

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





