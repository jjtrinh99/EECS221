import RPi.GPIO as GPIO
import time
from adafruit_bme280 import basic as adafruit_bme280
import smbus
from time import sleep
import board
import pyrebase
from twython import Twython

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

def avg_distance():
    '''record distance measurement 10 times
       return average distance'''

    total_dist = 0
    for _ in range(10):    
     
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(PIN_TRIGGER, GPIO.LOW)
    
        while GPIO.input(PIN_ECHO)==0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO)==1:
            pulse_end_time = time.time()
        
        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150, 2)
        sleep(120)
        total_dist += distance

    avg_dist = total_dist/10
    print ("Distance:",avg_dist,"cm")
    return avg_dist


def temphumidity():
    total_humidity, total_ambient_temp = 0,0

    for _ in range(10):
        time.sleep(1)
        humidity = bme280.humidity
        ambient_temp = (bme280.temperature*1.8) + 32
        total_humidity += humidity
        total_ambient_temp += ambient_temp
        sleep(120)

    avg_humidity = total_humidity/10
    avg_ambient_temp = total_ambient_temp/10
    
    sleep(1)
    return avg_humidity, avg_ambient_temp

def photores():
    total_photores = 0

    for _ in range(10):
        GPIO.setup(resistorPin, GPIO.OUT)
        GPIO.output(resistorPin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.setup(resistorPin, GPIO.IN)
        currentTime = time.time()
    
        while(GPIO.input(resistorPin) == GPIO.LOW):
            diff  = time.time() - currentTime
        sleep(120)
        total_photores = diff + total_photores
        
    avg_photores = (total_photores/10) * 1000
    print("avg_photores: ", avg_photores)
    
    time.sleep(1)
    return avg_photores

def ultrasonic(distance, pulse_duration, humidity, ambient_temp, diff, ctr):

    print ("Waiting for sensor to settle")
    time.sleep(0.5)
    print ("Calculating distance")

    '''GPIO.output(PIN_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(PIN_TRIGGER, GPIO.LOW)'''

    distance = avg_distance()    
    if distance >= 20:
        print("Water is low!")
        message = "Water is low: " + str(distance) +  ' #' + str(ctr)
        twitter.update_status(status= message)
    else:
        print("Water level is good, at: ", distance, "cm")
    data = {
            "distance" : distance
     }
    
    db.child("distance").child("3-distance").push(data)

    humidity, ambient_temp = temphumidity()

    if ambient_temp > 85:
        print("ambient temp is too high, at: ", ambient_temp)
        message = "ambient temp is too high: F" + str(ambient_temp) + ' #' + str(ctr)
        twitter.update_status(status=message)
    elif ambient_temp < 35:
        print("ambient temp is too low, at: ", ambient_temp)
        message = "ambient too low: F" + str(ambient_temp) + ' #' + str(ctr)
        twitter.update_status(status=message)
    
    if humidity > 85:
        print("humidity too high, at:", avg_humidity)
        message = "humidity too high:  %" + str(humidity) + ' #' + str(ctr)
        twitter.update_status(status=message)
    elif humidity < 40:
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
    diff = photores()     
    data = {
            "light": diff
    }
    db.child("light").child("4-light").push(data)
    if (diff * 1000) > 150: 
        message = "more light pls: " + str(diff) + ' #' + str(ctr) 
        twitter.update_status(status = message)

try:
    while True:
        ctr = (ctr + 1)#%10 # modulo operator keeps ctr in range 0-9

        ultrasonic(distance, pulse_duration, humidity, ambient_temp, diff, ctr)
        '''
        temphumidity(humidity, ambient_temp, ctr)
        photoresistor(diff)
        '''

        db.child("Here we go!").child("init").set(string)
        time.sleep(60)
except KeyboardInterrupt:
    print("cleaning up GPIO...")
    GPIO.cleanup()
    print('DONE!')
