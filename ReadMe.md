# Instrument Manager
Simple Python based flask app that displays installed instruments. Uses PyVISA and PyVISA-py.

Designed to run on a raspberry pi, provides a public API for querying instruments.

## How to Run
There is a shell script called instrumentmanager.sh that will run the flask server and open a fullscreen instance of Chromium, tested on Raspian OS.

There is a shell script called instrumentmanagersim.sh that will run the flask server in simulation mode and open a fullscreen instance of Chromium, tested on Raspian OS.

Alternatively run the following command in a terminal: Python3 InstrumentManager.py

Add -s to the above command to run the app in simulation mode which will provide some dummy instruments.

The default password is 1234A and then press the # key.

## Screens
Below are images of the login and instrument views 

![Login](images/login.jpg)
![Instruments](images/instruments.jpg)


