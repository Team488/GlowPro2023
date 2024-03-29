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
######  Input   Number  Mode        Function
######  11111   31      no code     NO_CODE
######  00000   0       not_booted  
######  00001   1       disabled    DISABLED
######  00010   2       enabled     enabled
######  00011   3       cube mode   display_Cube
######  00100   4       cone acq.   blinkingCone
######  00101   5       cube acq.   blinkingCube
######  00110   6       cone mode   display_Cone
######  
######  
######  
#############################################

#############################################
######  setup board output & neopixel light strip objects
#############################################
'''
pixel_pin = board.D5
num_pixels = 20

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1, auto_write=False)

steps=30
wait=0.04

conecube_length = 10
current_mode_length = 20-conecube_length

movingRainbow = 0

mode = 31

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
        update_conecube_mode()
        if read_current_mode() != current_mode:
            return
        for i in range(current_mode_length):
            pixels[i]=(0, 255*countdown/steps, 0)
        pixels.show()
        wait_and_check(wait)

    for countup in range(1, steps, 1):
        update_conecube_mode()
        if read_current_mode() != current_mode:
            return
        for i in range(current_mode_length):
            pixels[i]=(0, 255*countup/steps, 0)
        pixels.show()
        wait_and_check(wait)

def no_code():
    for noCode in range(num_pixels):
        pixels[noCode]=(80, 80, 80)
    pixels.show()
    wait_and_check(0.3)
    for noCode in range(num_pixels):
        pixels[noCode]=(0, 0, 0)
    pixels.show()
    wait_and_check(0.3)

def disabled():
    for countdown in range(steps, 1, -1):
        for i in range(num_pixels):
            pixels[i]=(255*countdown/steps, 0, 0)
        pixels.show()
        wait_and_check(wait)

    for countup in range(1, steps, 1):
        for i in range(num_pixels):
            pixels[i]=(255*countup/steps, 0, 0)
        pixels.show()
        wait_and_check(wait)

def disabled_with_auto():
    for i in range(num_pixels):
        pixels[i]=(20, 50, 20)
    for countdown in range(steps, 1, -1):
        pixels.brightness = countdown/steps
        pixels.show()
        wait_and_check(wait)

    for countup in range(1, steps, 1):
        pixels.brightness = countup/steps
        pixels.show()
        wait_and_check(wait)

def blinkingCube():
    for cube in range(current_mode_length):
        pixels[cube]=(145, 0, 255)
    pixels.show()
    wait_and_check(0.3)
    for cube in range(current_mode_length):
        pixels[cube]=(0, 0, 0)
    pixels.show()
    wait_and_check(0.2)

def blinkingCone():
    for cone in range(current_mode_length):
        pixels[cone]=(255, 165, 0)
    pixels.show()
    wait_and_check(0.3)
    for cone in range(current_mode_length):
        pixels[cone]=(0, 0, 0)
    pixels.show()
    wait_and_check(0.2)

def display_cone_cube(color):
    for i in range(20-conecube_length, 20, 1):
        pixels[i]=color


def moving_rainbow(switch):    
    global movingRainbow
    length = 0
    if switch:
        length = 20
    else:
        length = current_mode_length
    current_mode = read_current_mode()
    update_conecube_mode()
    for r in range(length):
        if read_current_mode() != current_mode:
            return
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

'''
#########################################################
#######   get current input from robot for cone/cube
'''

def update_conecube_mode():
    if pin_conecube.value == 1:
        display_cone_cube((145, 0, 255))
    else:
        display_cone_cube((255, 165, 0))
    pixels.show()

class ModeChangedException(Exception):
    pass

def wait_and_check(durationS):
    if mode == read_current_mode():
        time.sleep(durationS)
    else:
        raise ModeChangedException("Mode changed")

#############################################
######  main loop
#############################################

def main():
    global mode
    # Read mode and alliance from pins
    mode = read_current_mode()

    try:    
        #Select display option
        if mode == 31:
            no_code()
        elif mode == 1:
            disabled()
        elif mode == 2:
            enabled(mode)
        elif mode == 3:
            moving_rainbow(False)
        elif mode == 4:
            disabled_with_auto()
        elif mode == 5: #arm in position
            moving_rainbow(True)
        else:
            no_code()
    except ModeChangedException:
        # Mode changed, restart loop
        pass

while True:
    main()


####### EXTRAS ########

'''def lowBattery():
    for lowBattery in range(20):
        pixels[lowBattery]=(0, 255, 0)
    pixels.show()
    wait_and_check(5/count)
    for lowBattery in range(20):
        pixels[lowBattery]=(240, 70, 0)
    pixels.show()
    wait_and_check(1)

    if count < 4:
        for lowBattery in range(20):
            pixels[lowBattery]=(0, 255, 0)
        pixels.show()
        wait_and_check(5/count)
        for lowBattery in range(20):
            pixels[lowBattery]=(240, 70, 0)
        pixels.show()
        wait_and_check(1)

    elif count >= 4 and count >= 8:
        for lowBattery in range(20):
            pixels[lowBattery]=(240, 70, 0)
        pixels.show()
        wait_and_check(5/(count-3))
        for lowBattery in range(20):
            pixels[lowBattery]=(255, 0, 0)
        pixels.show()
        wait_and_check(1)

    else:
        pixels[lowBattery]=(255, 0, 0)'''


