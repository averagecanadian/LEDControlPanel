# Importing modules
import spidev # To communicate with SPI devices
from gpiozero import Button
from numpy import interp    # To scale values
from time import sleep
import RPi.GPIO as GPIO
import pigpio

import time
import I2C_LCD_driver

# play audio
from pygame import mixer

import subprocess

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

btnGreen = Button(25)
btnBlue = Button(19)
btnRed = Button(12)

btnFireTruck = Button(13)
btnPoliceCar = Button(27)

btnWhite = Button(5)
btnOrange = Button(22)
btnYellow = Button(6)


pi = pigpio.pi()
GPIO.setup(17, GPIO.IN)
prev_input = 0

#GPIO pings of MOSFETTS
GPIORed = 16
GPIOGreen = 20
GPIOBlue = 21

#Determine if slider or button will set colour
btnSelector = 0 # 0 = slider, 1 = buttons

mixer.init()

# Start SPI connection
spi = spidev.SpiDev() # Created an object
spi.open(0,0)   
# Initializing LED pin as OUTPUT pin
# Read MCP3008 data

def analogInput(channel):
  spi.max_speed_hz = 1350000
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
        
def Sirens(btnSelected):
    i = 0
    if (btnSelected == "PoliceCar"):
        sound = mixer.Sound('police.wav')
        sound.play(-1)
        while i == 0:
            pi.set_PWM_dutycycle(GPIORed, 0)
            pi.set_PWM_dutycycle(GPIOGreen, 0)
            pi.set_PWM_dutycycle(GPIOBlue, 255)
            sleep(0.3)
            pi.set_PWM_dutycycle(GPIORed, 255)
            pi.set_PWM_dutycycle(GPIOGreen, 0)
            pi.set_PWM_dutycycle(GPIOBlue, 0)
            sleep(0.3)
            if (btnFireTruck.is_pressed or btnRed.is_pressed or btnBlue.is_pressed or btnGreen.is_pressed or btnWhite.is_pressed or btnOrange.is_pressed or btnYellow.is_pressed):
                sound.stop()                
                i = 1 #exit while loop            
    if (btnSelected == "FireTruck"):
        sound = mixer.Sound('FireTruck.wav')
        sound.play(-1)
        while i == 0:
            pi.set_PWM_dutycycle(GPIORed, 255)
            pi.set_PWM_dutycycle(GPIOGreen, 255)
            pi.set_PWM_dutycycle(GPIOBlue, 255)
            sleep(0.3)
            pi.set_PWM_dutycycle(GPIORed, 255)
            pi.set_PWM_dutycycle(GPIOGreen, 0)
            pi.set_PWM_dutycycle(GPIOBlue, 0)
            sleep(0.3)
            if (btnPoliceCar.is_pressed or btnRed.is_pressed or btnBlue.is_pressed or btnGreen.is_pressed or btnWhite.is_pressed or btnOrange.is_pressed or btnYellow.is_pressed):
                sound.stop()
                i = 1 #exit while loop


#variables to hold previous RGB colours from slider. Only clear lcd if a value has changed. 
prevRed = 0
prevBlue = 0
prevGreen = 0

while True:    
    input = GPIO.input(17) #toggle switch

        #### Check to see if mylcd exists. I have to put it in this loop because if the application starts while the power button for the LEDs / LCDs is off it will throw an error. If the object doesn't exist, it will create the object. 
    try:
        mylcd
    except NameError:
        try:
            mylcd = I2C_LCD_driver.lcd()
        except:
            pass
        
    if (input == 0): #if toggle switch reads low input = 0, do slider stuff
        outputRed = analogInput(0) # Reading from CH0
        outputRed = int((interp(outputRed, [0, 1023], [0, 100])) * 2.55)
        outputBlue = analogInput(1) # Reading from CH0
        outputBlue = int((interp(outputBlue, [0, 1023], [0, 100])) * 2.55)
        outputGreen = analogInput(2) # Reading from CH0
        outputGreen = int((interp(outputGreen, [0, 1023], [0, 100])) * 2.55)
        
        if (outputRed != prevRed or outputBlue != prevBlue or outputGreen != prevGreen):
            try:
                mylcd.lcd_clear()
                pi.set_PWM_dutycycle(GPIORed, outputRed)
                mylcd.lcd_display_string("Red: " + str(outputRed),1)
                pi.set_PWM_dutycycle(GPIOBlue, outputBlue)
                mylcd.lcd_display_string("Blue: " + str(outputBlue),2)
                pi.set_PWM_dutycycle(GPIOGreen, outputGreen)
                mylcd.lcd_display_string("Green: " + str(outputGreen),3)
                prevRed = outputRed
                prevBlue = outputBlue
                prevGreen = outputGreen
            except Exception:
                pass                
        sleep(0.2)
    else: # do button stuff
        if btnGreen.is_pressed:
            pi.set_PWM_dutycycle(GPIORed, 0)
            pi.set_PWM_dutycycle(GPIOGreen, 255)            
            pi.set_PWM_dutycycle(GPIOBlue, 0)
            sleep(0.3)
        if btnBlue.is_pressed:            
            pi.set_PWM_dutycycle(GPIORed, 0)
            pi.set_PWM_dutycycle(GPIOGreen, 0)
            pi.set_PWM_dutycycle(GPIOBlue, 255)
            sleep(0.3)
        if btnRed.is_pressed:
            pi.set_PWM_dutycycle(GPIORed, 255)
            pi.set_PWM_dutycycle(GPIOGreen, 0)
            pi.set_PWM_dutycycle(GPIOBlue, 0)
            sleep(0.3)
        if btnWhite.is_pressed:
            pi.set_PWM_dutycycle(GPIORed, 255)
            pi.set_PWM_dutycycle(GPIOGreen, 255)
            pi.set_PWM_dutycycle(GPIOBlue, 255)
            sleep(0.3)
        if btnOrange.is_pressed:
            pi.set_PWM_dutycycle(GPIORed, 255)
            pi.set_PWM_dutycycle(GPIOGreen, 165)
            pi.set_PWM_dutycycle(GPIOBlue, 0)
            sleep(0.3)
        if btnYellow.is_pressed:
            pi.set_PWM_dutycycle(GPIORed, 255)
            pi.set_PWM_dutycycle(GPIOGreen, 255)
            pi.set_PWM_dutycycle(GPIOBlue, 0)
            sleep(0.3)
        if btnFireTruck.is_pressed:
            Sirens("FireTruck")
            sleep(0.3)
        if btnPoliceCar.is_pressed:            
            Sirens("PoliceCar")
            sleep(0.3)

            
            
            
