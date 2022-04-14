import machine
import framebuf
import time


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

    def draw(self, fbuffer):
        fbuffer.fill_rect(int(self.x), int(self.y), self.w, self.h, 1)     # draw rectangle at given location, size and color


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


spi = SPI(1, baudrate=6667000, polarity=0, phase=0)  # Hier waren 80 MHz voreingstellt, aufgrund der 1/(50 ms) == 20 Hz versuche ich es erstmal mit 40 kHz

# Data/Command (d/c)
dc = Pin(15, Pin.OUT)

# Vcc_Enable
vcc_en = Pin(14, Pin.OUT)

# Pmod_Enable
pmod_en = Pin(13, Pin.OUT)

# Reset (RES)
rst = Pin(16, Pin.OUT)

def power_on_seq():
    ## Power-On Sequence where bytes provided are in the format of (command, data)
    # 1. Bring data/command (d/c pin) logic low
    dc.value(0)
    # 2. Bring reset pin logic high
    rst.value(1)
    # 3. Bring Vcc Enable logic low
    vcc_en.value(0)
    # 4. Bring Pmod Enable to logic high and delay 20 ms to allow 3.3 V rail to become stable
    pmod_en.value(1)
    time.sleep_ms(20)
    # 5. Bring RES logic low, wait for at least 3 us and then bring it back to logic high to reset the display controller
    rst.value(0)
    time.sleep_us(4)
    rst.value(1)
    # 6. Wait for reset operation to complete; this takes a maximum of 3 us to complete
    time.sleep_us(3)
    rst.value(0)    # Nicht sicher ob das richtig ist!
    # 7. Enable driver IC to accept commands by sending unlock command (0xFD, 0x12)
    spi.write(b"0xFD")
    spi.write(b"0x12")
    # 8. Display off command
    spi.write(b"0xAE")
    # 9. Set remap and display formats
    spi.write(b"0xA0")
    spi.write(b"0x72")
    # 10. Set display start line to top line
    spi.write(b"0xA1")
    spi.write(b"0x00")
    # 11. Set display offset to no vertical offset
    spi.write(b"0xA2")
    spi.write(b"0x00")
    # 12. Make it a normal display with no color inversion or forcing pixels on/off
    spi.write(b"0xA4")
    # 13. Set multiplex ratio to enable all of common pins calculated by 1+register value
    spi.write(b"0xA8")
    spi.write(b"0x3F")
    # 14. Set master configuration to use a required external Vcc supply
    spi.write(b"0xAD")
    spi.write(b"0x8E")
    # 15. Disable power saving mode
    spi.write(b"0xB0")
    spi.write(b"0x0B")
    # 16. Set phase length of charge and discharge rates of OLED pixel in units of display clock
    spi.write(b"0xB1")
    spi.write(b"0x31")
    # 17. Set display clock divide ratio and oscillator freq, setting clock divider ratio to 1 and internal oscillator freq to ~890 kHz
    spi.write(b"0xB3")
    spi.write(b"0xF0")
    # 18. Set second pre-charge speed of color A to drive color (red) to target driving voltage
    spi.write(b"0x8A")
    spi.write(b"0x64")
    # 19. Set second pre-charge speed of color B to drive color (green) to target driving voltage
    spi.write(b"0x8B")
    spi.write(b"0x78")
    # 20. Set second pre-charge speed of color C to drive color (blue) to target driving voltage
    spi.write(b"0x8C")
    spi.write(b"0x64")
    # 21. Set pre-charge voltage to approximately 45 % of Vcc to drive each color to target driving voltage
    spi.write(b"0xBB")
    spi.write(b"0x3A")
    # 22. Set the VCOMH deselect level, which is minimum voltage level to be registered as logic high to 83 % of Vcc
    spi.write(b"0xBE")
    spi.write(b"0x3E")
    # 23. Set master current attenuation factor to set a reference current for the segment drivers
    spi.write(b"0x87")
    spi.write(b"0x06")
    # 24. Set contrast for color A (red), effectively setting brightness level
    spi.write(b"0x81")
    spi.write(b"0x91")
    # 25. Set contrast for color B (green), effectively setting brightness level
    spi.write(b"0x82")
    spi.write(b"0x50")
    # 26. Set contrast for color C (blue), effectively setting brigthness level
    spi.write(b"0x83")
    spi.write(b"0x7D")
    # 27. Disable scrolling
    spi.write(b"0x2E")
    # 28. Clear screen bye sending clear command and dimensions of window to clear (top column, top row, bottom column, bottom row)
    spi.write(b"0x25")
    spi.write(b"0x00")
    spi.write(b"0x00")
    spi.write(b"0x5F")
    spi.write(b"0x3F")
    # 29. Bring VccEn logic high and wait 25 ms
    vcc_en.value(1)
    time.sleep_ms(25)
    # 30. Turn display on
    spi.write(b"0xAF")
    # 31. Wait at least 100 ms before further operation
    time.sleep_ms(100)
    # Done!


def power_off_seq():
    # 1. Turn the display off
    spi.write(b"0xAE")
    # 2. Bring Vcc Enable logic low
    vcc_en.value(0)
    # 3. Delay 400 ms
    time.sleep_ms(400)
    # 4. Disconnect positiv voltage supply to PmodOLEDrgb


# Start conditions & positions
ball = Ball(32, 16, 3, 3, 2, -2)
player = Player(30, 31, 10, 3, 0, 0)

adc = machine.ADC(0)    # 0 - 1 Volt ! An Vorwiderstand denken!


# the floor division // rounds the result down to the nearest whole number
fbuf = framebuf.FrameBuffer(bytearray(SCREEN_WIDTH * SCREEN_HEIGHT // 8), SCREEN_WIDTH, SCREEN_HEIGHT, framebuf.MONO_HLSB)
tick = time.ticks_ms()

while not game_over:
    ntick = tick.ticks_ms()
    ball.update(time.ticks_diff(ntick, tick) // 100, player)
    tick = ntick
    player.x = adc.read_u16() * 58 / 255  # warum mal 58? (Erhöhung der Beschleunigung? Willkürlich gewählte Konstante?)
    fbuf.fill(0)    # Fill entire framebuf with specific color
    ball.draw(fbuf)
    player.draw(fbuf)
    spi.write(bytearray([fbuf]))

    time.sleep_ms(50)   # Adjust this for more performance boosts (Schätze damit kann man es schneller machen == Schwierigkeitsgrad)

fbuf.fill(0)
fbuf.text('GAME', 15, 8)    # Write text to framebuf using coordinates as the upper-left corner of the text (color can be defined (standard value 1))
fbuf.text('OVER', 15, 18)
spi.writeto(8, fbuf)

print('Score: ', score)


## https://github.com/danjperron/pico_mpu6050_ssd1331/blob/088c6bf4d71450431ce284d1c346423a5e62747b/ssd1331.py#L107