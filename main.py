import time

import framebuf
from machine import Pin, ADC, SPI
from micropython import const

from disp_matrix import DispMatrix
from display import PmodOLEDrgb
from obj import Ball, Player

# Constants
SCREEN_WIDTH = 96
SCREEN_HEIGHT = 64

spi = SPI(1, baudrate=6000000)

dc = Pin(5, Pin.OUT)
rst = Pin(4, Pin.OUT)

disp = PmodOLEDrgb(spi, dc, rst)

# Analog-Digital converter input (potentiometer)
adc = ADC(0)  # 0 - 1 Volt ! An Vorwiderstand denken!

dispArr = bytearray(SCREEN_WIDTH * SCREEN_HEIGHT * 2)
fbuf = framebuf.FrameBuffer(dispArr, SCREEN_WIDTH, SCREEN_HEIGHT, framebuf.RGB565)
#fbuf.fill(0)

# Display
#disp = PmodOLEDrgb(spi, dc, vcc_en, pmod_en, rst, SCREEN_WIDTH, SCREEN_HEIGHT)

#disp.power_on_seq()
#disp.fill(0xF221)

# Start conditions & positions
ball = Ball(32, 16, 3, 3, 1, -1, SCREEN_WIDTH, SCREEN_HEIGHT)  # vx = 2; vx = -2
player = Player(30, SCREEN_HEIGHT-3, 15, 2, 0, 0)

# Program
tick = time.ticks_ms()

while not ball.get_game_over():
    ntick = time.ticks_ms()
    ball.update(time.ticks_diff(ntick, tick) // 100,
                player)  # the floor division // rounds the result down to the nearest whole number
    tick = ntick
    player.x = adc.read_u16() * (SCREEN_WIDTH-15) / 1023  # warum mal 58? (Erhöhung der Beschleunigung? Willkürlich gewählte Konstante?)
    fbuf.fill(0)  # Fill entire framebuf with specific color
    ball.draw(fbuf)
    player.draw(fbuf)
    disp.block(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, dispArr)
    time.sleep_ms(50)

fbuf.fill(0)
fbuf.text('GAME', 15, 8)
fbuf.text('OVER', 15, 18)
disp.block(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, dispArr)
print('Score: ', ball.get_score())

## https://github.com/danjperron/pico_mpu6050_ssd1331/blob/088c6bf4d71450431ce284d1c346423a5e62747b/ssd1331.py#L107
