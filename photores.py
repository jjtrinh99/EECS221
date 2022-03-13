import RPi.GPIO as GPIO
import time
from adafruit_bme280 import basic as adafruit_bme280
import smbus
from time import sleep
import board
import pyrebase
from twython import Twython

config = {
  "apiKey": "X",
  "authDomain": "Y",
  "databaseURL": "Z",
  "storageBucket": "0"
}


firebase = pyrebase.initialize_app(config)
db = firebase.database()

from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

twitter = Twython(
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)


#GPIO.setmode(GPIO.BOARD)

resistorPin = 40
ctr = 0
#while True:
GPIO.setup(resistorPin, GPIO.OUT)
GPIO.output(resistorPin, GPIO.LOW)
time.sleep(0.1)
    
GPIO.setup(resistorPin, GPIO.IN)
currentTime = time.time()
diff = 0
    
while(GPIO.input(resistorPin) == GPIO.LOW):
    diff  = time.time() - currentTime
        
print(diff * 1000)
time.sleep(1)

data = {
    "light": diff*1000
}
db.child("light").child("4-light").push(data)
ctr = ctr + 1 
if diff*1000  >= 90:
    print("lightitupGGG!")
    message = "lightitupGGG " + str(diff*1000)
    twitter.update_status(status= message + ' ' + str(ctr))


