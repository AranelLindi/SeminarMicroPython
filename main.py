import time

import framebuf
from machine import Pin, ADC, SPI

from display import PmodOLEDrgb
from obj import Ball, Player

# Display size (constants)
SCREEN_WIDTH = 96
SCREEN_HEIGHT = 64

# SPI initialization
spi = SPI(1, baudrate=6000000)  # 6 MHz

# Control pins for display
dc = Pin(5, Pin.OUT)
rst = Pin(4, Pin.OUT)

# Display object initialization (includes Power-On-Sequence)
disp = PmodOLEDrgb(spi, dc, rst)

# Analog-Digital converter input
adc = ADC(0)  # Caution ! ADC should not have more than 1 volt !

# Array which is storing next frame
dispArr = bytearray(SCREEN_WIDTH * SCREEN_HEIGHT * 2)
fbuf = framebuf.FrameBuffer(dispArr, SCREEN_WIDTH, SCREEN_HEIGHT, framebuf.RGB565)

# Start conditions & positions
ball = Ball(32, 16, 3, 3, 1, -1, SCREEN_WIDTH, SCREEN_HEIGHT)  # vx = 2; vx = -2
player = Player(30, SCREEN_HEIGHT - 3, 15, 2, 0, 0)

# Required to calculate dt for first time
tick = time.ticks_ms()

# Execute loop as long as game isnt lost
while not ball.get_game_over():
    ntick = time.ticks_ms()
    ball.update(time.ticks_diff(ntick, tick) // 100,
                player)  # the floor division // rounds the result down to the nearest whole number
    tick = ntick
    player.x = adc.read_u16() * (SCREEN_WIDTH - 15) / 1023
    fbuf.fill(0)  # Fill entire framebuf with specific color (0 == black)
    ball.draw(fbuf)  # Inserts current ball position into frame
    player.draw(fbuf)  # Inserts current player platform position into frame
    disp.block(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, dispArr)  # Sends current frame to display
    time.sleep_ms(50)  # Waits for next iteration

# Game is lost...
fbuf.fill(0)
fbuf.text('GAME', 15, 8)
fbuf.text('OVER', 15, 18)
disp.block(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, dispArr)
print('Score: ', ball.get_score())  # Score is sent through UART / USB
