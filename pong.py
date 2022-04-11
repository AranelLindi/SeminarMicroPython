import machine
import framebuf
import time
# import pyb

from machine import Pin, SPI    # selbst hinzugefügt

# Constants
SCREEN_WIDTH = 96
SCREEN_HEIGHT = 64

# Global variables
game_over = False
score = 0


class Entity:
    def __init__(self, x, y, w, h, vx, vy):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vx = vx
        self.vy = vy

    def draw(self, fbuf):
        fbuf.fill_rect(int(self.x), int(self.y), self.w, self.h, 1)     # draw rectangle at given location, size and color


class Player(Entity):
    pass


class Ball(Entity):
    def update(self, dt, player):
        self.x += self.vx * dt
        if self.x <= 0:
            self.x = 0
            self.vx = -self.vx

        if self.x >= SCREEN_WIDTH - self.w:
            self.x = SCREEN_WIDTH - self.w
            self.vx = - self.vx

        if self.y <= 0:
            self.y = 0
            self.vy = -self.vy

        if self.y >= (SCREEN_HEIGHT - self.h - player.h):
            if (self.x >= player.x) and (self.x <= player.x + player.w):
                self.y = SCREEN_HEIGHT - self.h - player.h
                self.vy = -self.vy

                global score
                score += 1

                if score % 2 == 0:
                    self.vx += self.vx / abs(self.vx) * 1

                if score % 3 == 0:
                    self.vy += self.vy / abs(self.vy) * 1
            else:
                global game_over
                game_over = True


# Start conditions & positions
ball = Ball(32, 16, 1, 1, 2, -2)
player = Player(30, 31, 10, 1, 0, 0)

adc = machine.ADC(0)    # 0 - 1 Volt ! An Vorwiderstand denken!
spi = SPI(1, baudrate=40000, polarity=0, phase=0)  # Hier waren 80 MHz voreingstellt, aufgrund der 1/(50 ms) == 20 Hz versuche ich es erstmal mit 40 kHz

# the floor division // rounds the result down to the nearest whole number
fbuf = framebuf.FrameBuffer(bytearray(SCREEN_WIDTH * SCREEN_HEIGHT // 8), SCREEN_WIDTH, SCREEN_HEIGHT, framebuf.MONO_HLSB)
tick = time.ticks_ms()

while not game_over:
    ntick = tick.ticks_ms()
    ball.update(time.ticks_diff(ntick, tick) // 100, player)
    tick = ntick
    player.x = adc.read() * 58 / 255  # warum mal 58? (Erhöhung der Beschleunigung? Willkürlich gewählte Konstante?)
    fbuf.fill(0)    # Fill entire framebuf with specific color
    ball.draw(fbuf)
    player.draw(fbuf)
    spi.writeto(8, fbuf)
    time.sleep_ms(50)   # Adjust this for more performance boosts (Schätze damit kann man es schneller machen == Schwierigkeitsgrad)

fbuf.fill(0)
fbuf.text('GAME', 15, 8)    # Write text to framebuf using coordinates as the upper-left corner of the text (color can be defined (standard value 1))
fbuf.text('OVER', 15, 18)
spi.writeto(8, fbuf)

print('Score: ', score)
