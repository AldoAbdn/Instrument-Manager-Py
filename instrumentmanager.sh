#!/bin/bash
python3 "/home/pi/Documents/Instrument-Manager-Py/InstrumentManager.py" & sleep 10; /usr/bin/chromium-browser --noerrdialogs --disable-infobars --kiosk http://0.0.0.0:5000


