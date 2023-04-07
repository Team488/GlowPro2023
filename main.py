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
######  INPUT MAP
######  Alliance: [pin7]
######  Alliance: 1 = blue, 0 = red
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
#############################################

#############################################
######  setup vars
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
current_time = time.time()

mode = 31
'''
#############################################
######  setup input
#############################################
'''
pin_conecube = DigitalInOut(board.D7)
pin_conecube.direction = Direction.INPUT
pin_conecube.pull = Pull.DOWN

pin9 = DigitalInOut(board.D9)
pin9.direction = Direction.INPUT
pin9.pull = Pull.DOWN

pin10 = DigitalInOut(board.D10)
pin10.direction = Direction.INPUT
pin10.pull = Pull.DOWN

pin11 = DigitalInOut(board.D11)
pin11.direction = Direction.INPUT
pin11.pull = Pull.DOWN

pin12 = DigitalInOut(board.D12)
pin12.direction = Direction.INPUT
pin12.pull = Pull.DOWN

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

def disabled_with_auto(color):
    for i in range(num_pixels):
        pixels[i]=color
    for countdown in range(steps, 1, -1):
        pixels.brightness = countdown/steps
        pixels.show()
        wait_and_check(wait)
    for countup in range(1, steps, 1):
        pixels.brightness = countup/steps
        pixels.show()
        wait_and_check(wait)

def display_cone_cube(color):
    global current_time 
    if time.time() - current_time < 0.25:
        return
    if current_time % 2 == 0:
        for i in range(20-conecube_length, 20, 1):
            if i >= (20-conecube_length)+conecube_length/2: pixels[i]=color
            else: pixels[i]=(255,255,255)
    else:
        for i in range(20-conecube_length, 20, 1):
            if i >= (20-conecube_length)+conecube_length/2: pixels[i]=(255,255,255)
            else: pixels[i]=color
    current_time = time.time()
    
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

def read_current_mode():
    return int(pin9.value)+int(pin10.value<<1)+int(pin11.value<<2)+int(pin12.value<<3)+int(pin13.value<<4) #(temp+temp1+temp2+temp3+temp4)

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

def unknown(len):
    for i in range(len):
        pixels[i]=(0, 255, 0)
    for countdown in range(steps, 1, -1):
        pixels.brightness = countdown/steps
        pixels.show()
        wait_and_check(wait)
    for countup in range(1, steps, 1):
        pixels.brightness = countup/steps
        pixels.show()
        wait_and_check(wait)

def display_Cone():
    for i in range(15, 20, 1):
        pixels[i]=(255, 165, 0)
    pixels.show()

def main():
    global mode
    mode = read_current_mode()
    try:    
        if mode == 31:
            no_code()
        elif mode == 1:
            disabled()
        elif mode == 2:
            enabled(mode)
        elif mode == 3:
            moving_rainbow(False)
        elif mode == 4:
            disabled_with_auto((20, 50, 20))
        elif mode == 5:
            moving_rainbow(True)
        elif mode == 6:
            disabled_with_auto((0, 150, 0))
        else:
            unknown(mode)
    except ModeChangedException:
        pass

while True:
    main()