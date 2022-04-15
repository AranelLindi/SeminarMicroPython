import time

import framebuf
import machine
from machine import Pin, SPI

from display import PmodOLEDrgb
from obj import Ball, Player

# Constants
SCREEN_WIDTH = 96
SCREEN_HEIGHT = 64

# Global variables -- werden die wirklich gebraucht? Zum Schluss nochmal prüfen
# game_over = False
# score = 0

# Data/Command (d/c)
dc = Pin(5, Pin.OUT)
dc.value(0)

# Vcc_Enable
vcc_en = Pin(4, Pin.OUT)
vcc_en.value(0)

# Pmod_Enable
pmod_en = Pin(10, Pin.OUT)
pmod_en.value(0)

# Reset (RES)
rst = Pin(9, Pin.OUT)
rst.value(0)

# Analog-Digital converter input (potentiometer)
adc = machine.ADC(0)  # 0 - 1 Volt ! An Vorwiderstand denken!

# Hardware SPI
spi = SPI(1, baudrate=80000000, polarity=0,
          phase=0)  # Hier waren 80 MHz voreingstellt, aufgrund der 1/(50 ms) == 20 Hz versuche ich es erstmal mit 40 kHz

# the floor division // rounds the result down to the nearest whole number
fbuf = framebuf.FrameBuffer(bytearray(SCREEN_WIDTH * SCREEN_HEIGHT // 8), SCREEN_WIDTH, SCREEN_HEIGHT,
                            framebuf.RGB565)

# Display
disp = PmodOLEDrgb(spi, dc, vcc_en, pmod_en, rst, SCREEN_WIDTH, SCREEN_HEIGHT)
disp.power_on_seq()

# Start conditions & positions
ball = Ball(32, 16, 3, 3, 2, -2, SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(30, 31, 10, 3, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

# Program
tick = time.ticks_ms()

while not ball.get_game_over():
    ntick = time.ticks_ms()
    ball.update(time.ticks_diff(ntick, tick) // 100, player)
    tick = ntick
    player.x = adc.read_u16() * 58 / 255  # warum mal 58? (Erhöhung der Beschleunigung? Willkürlich gewählte Konstante?)
    fbuf.fill(0x00)  # Fill entire framebuf with specific color
    ball.draw(fbuf)
    player.draw(fbuf)
    disp.draw_bitmap(0x00, 0x00, hex(SCREEN_WIDTH - 1), hex(SCREEN_HEIGHT - 1), fbuf)
    # spi.write(bytearray([fbuf]))

    time.sleep_ms(
        50)  # Adjust this for more performance boosts (Schätze damit kann man es schneller machen == Schwierigkeitsgrad)

fbuf.fill(0)
fbuf.text('GAME', 15,
          8)  # Write text to framebuf using coordinates as the upper-left corner of the text (color can be defined (standard value 1))
fbuf.text('OVER', 15, 18)
# spi.writeto(8, fbuf)
disp.draw_bitmap(0x00, 0x00, hex(SCREEN_WIDTH - 1), hex(SCREEN_HEIGHT - 1), fbuf)

print('Score: ', ball.get_score())

## https://github.com/danjperron/pico_mpu6050_ssd1331/blob/088c6bf4d71450431ce284d1c346423a5e62747b/ssd1331.py#L107
