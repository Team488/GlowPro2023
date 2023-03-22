# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT
from digitalio import DigitalInOut, Direction, Pull
import time
import board
import neopixel
from rainbowio import colorwheel

'''
#############################################
######  
######  INPUT MAP
######  
######  Alliance: [pin7]
######  Alliance: 1 = blue, 0 = red
###### 
###### 
######  Input mapping for light display: 
######  [pin13][pin12][pin11][pin10][pin9]
###### 
######  Input   Number  Mode            Function
######  11111   31      no code         NO_CODE
######  00000   0         
######  00001   1       disabled        DISABLED
######  00010   2       enabled         enabled
######  00011   3       GamePiece       GamePiece_Collected
######  00100   4       arm_Position    ARM_IN_SCORING_POSITION
######  00101   5       cube acq.       blinkingCube
######  00110   6       cone mode       display_Cone
######  
######  
######  
#############################################
'''
#NO_CODE = 31 # with no code, all the bits are high by default (we can't control this)
#DISABLED = 1
#ENABLED = 2
#GAME_PIECE_COLLECTED = 3
#ARM_IN_SCORING_POSITION = 4
'''
#############################################
######  setup board output & neopixel light strip objects
#############################################
'''
pixel_pin = board.D5
num_pixels = 20

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1, auto_write=False)

allianceColor=(0, 0, 0)
steps=30
wait=0.04

conecube_length = 15

'''
#############################################
######  setup pins for input
#############################################
'''

#pin7
pin_conecube = DigitalInOut(board.D7)
pin_conecube.direction = Direction.INPUT
pin_conecube.pull = Pull.DOWN

#pin9
pin9 = DigitalInOut(board.D9)
pin9.direction = Direction.INPUT
pin9.pull = Pull.DOWN

#pin10
pin10 = DigitalInOut(board.D10)
pin10.direction = Direction.INPUT
pin10.pull = Pull.DOWN

#pin11
pin11 = DigitalInOut(board.D11)
pin11.direction = Direction.INPUT
pin11.pull = Pull.DOWN

#pin12
pin12 = DigitalInOut(board.D12)
pin12.direction = Direction.INPUT
pin12.pull = Pull.DOWN

#pin13
pin13 = DigitalInOut(board.D13)
pin13.direction = Direction.INPUT
pin13.pull = Pull.DOWN

'''
#############################################
######  color display functions
#############################################
'''
def enabled(current_mode):
    for countdown in range(steps, 1, -1):
        read_conecube_mode()
        if read_current_mode() != current_mode:
            return
        for i in range((20-conecube_length)):
            pixels[i]=(0, 255*countdown/steps, 0)
        pixels.show()
        time.sleep(wait)
    for countup in range(1, steps, 1):
        read_conecube_mode()
        if read_current_mode() != current_mode:
            return
        for i in range((20-conecube_length)):
            pixels[i]=(0, 255*countup/steps, 0)
        pixels.show()
        time.sleep(wait)

def RobotNotBooted():
    for noCode in range(20):
        pixels[noCode]=(255, 0, 0)
    pixels.show()
    time.sleep(0.3)
    for noCode in range(20):
        pixels[noCode]=(0, 0, 0)
    pixels.show()
    time.sleep(0.3)

def RobotDisabled(current_mode):
    for countdown in range(steps, 1, -1):
        if read_current_mode() != current_mode:
            return
        for i in range(20): #disabled takes priority over conecube mode
            pixels[i]=(255*countdown/steps, 0, 0)
        pixels.show()
        time.sleep(wait)
    for countup in range(1, steps, 1):
        read_conecube_mode()
        if read_current_mode() != current_mode:
            return
        for i in range(20):
            pixels[i]=(255*countup/steps, 0, 0)
        pixels.show()
        time.sleep(wait)

def arm_Position():
    for i in range((20-conecube_length)):
        pixels[i]=(0, 255, 0)
    pixels.show()

def display_Cube():
    for i in range((20-conecube_length)):
        pixels[i]=(145, 0, 255)
    pixels.show()

def display_Cone():
    for i in range((20-conecube_length)):
        pixels[i]=(255, 165, 0)
    pixels.show()

def blinkingCube():
    for cube in range((20-conecube_length)):
        pixels[cube]=(145, 0, 255)
    pixels.show()
    time.sleep(0.3)
    for cube in range((20-conecube_length)):
        pixels[cube]=(0, 0, 0)
    pixels.show()
    time.sleep(0.2)

def blinkingCone():
    for cone in range((20-conecube_length)):
        pixels[cone]=(255, 165, 0)
    pixels.show()
    time.sleep(0.3)
    for cone in range((20-conecube_length)):
        pixels[cone]=(0, 0, 0)
    pixels.show()
    time.sleep(0.2)

def display_conecube(color): #does not have a show for fast execution
    for i in range(20-conecube_length, 20, 1):
        pixels[i]=color

def GamePiece_Collected():    
    movingRainbow = 0
    current_mode = read_current_mode()
    while read_current_mode() == current_mode:
        for r in range((20-conecube_length)):
            read_conecube_mode()
            pixels[r]=colorwheel((255/20*(r+movingRainbow))%255)  
            pixels.show()
        movingRainbow = movingRainbow+1

'''
#############################################
######  get current input from robot
#############################################
'''
def read_current_mode():
    temp = int(pin9.value)
    temp1 = int(pin10.value)<<1
    temp2 = int(pin11.value)<<2
    temp3 = int(pin12.value)<<3
    temp4 = int(pin13.value)<<4
    return (temp+temp1+temp2+temp3+temp4)

def read_conecube_mode():
    if pin_conecube.value == 1:
        display_conecube((145, 0, 255))
    else:
        display_conecube((255, 165, 0))

def main():
    # Read mode and alliance from pins
    mode = read_current_mode()
    read_conecube_mode()
    
    #Select display option
    if mode == 31:#NO_CODE:
        RobotNotBooted()
    elif mode == 1:#DISABLED:
        RobotDisabled(mode)
    elif mode == 2:#ENABLED:
        enabled(mode)
    elif mode == 3:#GAME_PIECE_COLLECTED:
        GamePiece_Collected()
    elif mode == 4:#ARM_IN_SCORING_POSITION:
        arm_Position()
    elif mode == 5:
        blinkingCube()
    elif mode == 6:
        display_Cone()
    else:
        RobotDisabled(mode)

while True:
    main()


####### EXTRAS ########
'''def lowBattery():
    for lowBattery in range(20):
        pixels[lowBattery]=(0, 255, 0)
    pixels.show()
    time.sleep(5/count)
    for lowBattery in range(20):
        pixels[lowBattery]=(240, 70, 0)
    pixels.show()
    time.sleep(1)

    if count < 4:
        for lowBattery in range(20):
            pixels[lowBattery]=(0, 255, 0)
        pixels.show()
        time.sleep(5/count)
        for lowBattery in range(20):
            pixels[lowBattery]=(240, 70, 0)
        pixels.show()
        time.sleep(1)

    elif count >= 4 and count >= 8:
        for lowBattery in range(20):
            pixels[lowBattery]=(240, 70, 0)
        pixels.show()
        time.sleep(5/(count-3))
        for lowBattery in range(20):
            pixels[lowBattery]=(255, 0, 0)
        pixels.show()
        time.sleep(1)

    else:
        pixels[lowBattery]=(255, 0, 0)'''


