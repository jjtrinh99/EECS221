import RPi.GPIO as GPIO
import time
from adafruit_bme280 import basic as adafruit_bme280
import smbus
from time import sleep
import board
import pyrebase
from twython import Twython
import photores

i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

PIN_TRIGGER = 4
PIN_ECHO = 17

GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)
GPIO.output(PIN_TRIGGER, GPIO.LOW)

resistorPin = 40
 
distance = 0
pulse_duration = 0
humidity = 0
ambient_temp = 0
diff = 0
ctr = 0

config = {
  "apiKey": "twOI7G4dMO56MZkRfAne0Sj59ETe9j0awFEnCkYl",
  "authDomain": "smartvase-5f009",
  "databaseURL": "https://smartvase-5f009-default-rtdb.firebaseio.com/",
  "storageBucket": "smartvase-5f009.appspot.com"
}

data = {
    "temp": ambient_temp,
    "humidity": humidity,
    "distance": distance,
    "light": diff*1000
     }

firebase = pyrebase.initialize_app(config)
db = firebase.database()
string = "starting now"

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

message = "Hello World!"

def ultrasonic(distance, pulse_duration, humidity, ambient_temp, diff, ctr):

    print ("Waiting for sensor to settle")
    time.sleep(0.5)
    print ("Calculating distance")

    GPIO.output(PIN_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    while GPIO.input(PIN_ECHO)==0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO)==1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    distance = round(pulse_duration * 17150, 2)
    print ("Distance:",distance,"cm")
    
    if distance >= 30:
        print("Water is low!")
        message = "Water is low: " + str(distance) +  '#' + str(ctr)
        twitter.update_status(status= message)
    else:
        print("Water level is good, at: ", distance, "cm")
    data = {
            "distance" : distance
     }
    
    db.child("distance").child("3-distance").push(data)

#def temphumidity(humidity, ambient_temp, ctr):
    time.sleep(1)
    humidity = bme280.humidity
    ambient_temp = (bme280.temperature*1.8) + 32
    
    if ambient_temp > 45:
        print("ambient temp is too high, at: ", ambient_temp)
        message = "ambient temp is too high: F" + str(ambient_temp) + ' #' + str(ctr)
        twitter.update_status(status=message)
    elif ambient_temp < 30:
        print("ambient temp is too low, at: ", ambient_temp)
        message = "ambient too low: F" + str(ambient_temp) + ' #' + str(ctr)
        twitter.update_status(status=message)
    
    if humidity > 95:
        print("humidity too high, at:", humidity)
        message = "humidity too high:  %" + str(humidity) + ' #' + str(ctr)
        twitter.update_status(status=message)
    elif humidity < 85:
        print("humidity is too low, at:", humidity)
        message = "low humidity at: % " + str(humidity) + ' #' + str(ctr)
        twitter.update_status(status=message)
    
    data = {
        "temp": humidity,
        "humidity": ambient_temp,
     }
    
    db.child("humidity&temp").child("2-humidity,temp").push(data)
  
#was calling the photoresistor 
 #thru another file originally, 
  #but was able to move it here 
  
#def photoresistor(diff):
    GPIO.setup(resistorPin, GPIO.OUT)
    GPIO.output(resistorPin, GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(resistorPin, GPIO.IN)
    currentTime = time.time()
    while(GPIO.input(resistorPin) == GPIO.LOW):
        diff  = time.time() - currentTime
    print(diff * 1000)
    time.sleep(1)
    
    data = {
        "light": diff*1000
    }
    db.child("light").child("4-light").push(data)

while True:
    ctr = ctr + 1 
    if(ctr >=10):
        ctr = 0

    ultrasonic(distance, pulse_duration, humidity, ambient_temp, diff, ctr)
    '''
    temphumidity(humidity, ambient_temp, ctr)
    photoresistor(diff)
    '''
    #exec(open('photores.py').read())


    db.child("Here we go!").child("init").set(string)
    time.sleep(5)

GPIO.cleanup()

