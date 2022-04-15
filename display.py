import time


def convert_16bits_to_rgb(color):
    # Use bit masks to extract RGB color from 16 bit integer
    return (color and 0x7C00), (color and 0x03E0), (color and 0x001F)


def convert_rgb_to_16bits(r, g, b):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


class PmodOLEDrgb:  # SSD1331-Display
    def __init__(self, spi, dc, vcc_en, pmod_en, rst, screen_width, screen_height):
        self.spi = spi
        self.dc = dc
        self.vcc_en = vcc_en
        self.pmod_en = pmod_en
        self.rst = rst
        self.screen_width = screen_width
        self.screen_height = screen_height

    def power_on_seq(self):
        ## Power-On Sequence where bytes provided are in the format of (command, data)
        # 1. Bring data/command (d/c pin) logic low
        self.dc.value(0)
        # 2. Bring reset pin logic high
        self.rst.value(1)
        # 3. Bring Vcc Enable logic low
        self.vcc_en.value(0)
        # 4. Bring Pmod Enable to logic high and delay 20 ms to allow 3.3 V rail to become stable
        self.pmod_en.value(1)
        time.sleep_ms(20)
        # 5. Bring RES logic low, wait for at least 3 us and then bring it back to logic high to reset the display controller
        self.rst.value(0)
        time.sleep_us(4)
        self.rst.value(1)
        # 6. Wait for reset operation to complete; this takes a maximum of 3 us to complete
        time.sleep_us(3)
        #self.rst.value(0)  # Nicht sicher ob das richtig ist!
        # 7. Enable driver IC to accept commands by sending unlock command (0xFD, 0x12)
        self.spi.write(b"0xFD")
        self.spi.write(b"0x12")
        # 8. Display off command
        self.spi.write(b"0xAE")
        # 9. Set remap and display formats
        self.spi.write(b"0xA0")
        self.spi.write(b"0x72")
        # 10. Set display start line to top line
        self.spi.write(b"0xA1")
        self.spi.write(b"0x00")
        # 11. Set display offset to no vertical offset
        self.spi.write(b"0xA2")
        self.spi.write(b"0x00")
        # 12. Make it a normal display with no color inversion or forcing pixels on/off
        self.spi.write(b"0xA4")
        # 13. Set multiplex ratio to enable all of common pins calculated by 1+register value
        self.spi.write(b"0xA8")
        self.spi.write(b"0x3F")
        # 14. Set master configuration to use a required external Vcc supply
        self.spi.write(b"0xAD")
        self.spi.write(b"0x8E")
        # 15. Disable power saving mode
        self.spi.write(b"0xB0")
        self.spi.write(b"0x0B")
        # 16. Set phase length of charge and discharge rates of OLED pixel in units of display clock
        self.spi.write(b"0xB1")
        self.spi.write(b"0x31")
        # 17. Set display clock divide ratio and oscillator freq, setting clock divider ratio to 1 and internal oscillator freq to ~890 kHz
        self.spi.write(b"0xB3")
        self.spi.write(b"0xF0")
        # 18. Set second pre-charge speed of color A to drive color (red) to target driving voltage
        self.spi.write(b"0x8A")
        self.spi.write(b"0x64")
        # 19. Set second pre-charge speed of color B to drive color (green) to target driving voltage
        self.spi.write(b"0x8B")
        self.spi.write(b"0x78")
        # 20. Set second pre-charge speed of color C to drive color (blue) to target driving voltage
        self.spi.write(b"0x8C")
        self.spi.write(b"0x64")
        # 21. Set pre-charge voltage to approximately 45 % of Vcc to drive each color to target driving voltage
        self.spi.write(b"0xBB")
        self.spi.write(b"0x3A")
        # 22. Set the VCOMH deselect level, which is minimum voltage level to be registered as logic high to 83 % of Vcc
        self.spi.write(b"0xBE")
        self.spi.write(b"0x3E")
        # 23. Set master current attenuation factor to set a reference current for the segment drivers
        self.spi.write(b"0x87")
        self.spi.write(b"0x06")
        # 24. Set contrast for color A (red), effectively setting brightness level
        self.spi.write(b"0x81")
        self.spi.write(b"0x91")
        # 25. Set contrast for color B (green), effectively setting brightness level
        self.spi.write(b"0x82")
        self.spi.write(b"0x50")
        # 26. Set contrast for color C (blue), effectively setting brigthness level
        self.spi.write(b"0x83")
        self.spi.write(b"0x7D")
        # 27. Disable scrolling
        self.spi.write(b"0x2E")
        # 28. Clear screen bye sending clear command and dimensions of window to clear (top column, top row, bottom column, bottom row)
        self.spi.write(b"0x25")
        self.spi.write(b"0x00")
        self.spi.write(b"0x00")
        self.spi.write(b"0x5F")
        self.spi.write(b"0x3F")
        # 29. Bring VccEn logic high and wait 25 ms
        self.vcc_en.value(1)
        time.sleep_ms(25)
        # 30. Turn display on
        self.spi.write(b"0xAF")
        # 31. Wait at least 100 ms before further operation
        time.sleep_ms(100)
        # Done !

    def clear_display(self):
        self.spi.write(b"0x25")  # Clear mode
        self.spi.write(b"0x00")  # Set starting column coordinates
        self.spi.write(b"0x00")  # Set starting row coordinates
        self.spi.write(b"0x5F")  # Set finishing column coordinates
        self.spi.write(b"0x3F")  # Set finishing row coordinates

    def draw_bitmap(self, col_start, row_start, col_end, row_end, pixels):
        # Check if coordinates out of range
        if not (0 <= col_start <= self.screen_width) or not (0 <= col_end <= self.screen_width) or not (
                0 <= row_start <= self.screen_height) or not (
                0 <= row_end <= self.screen_height):  # Hier können meines erachtens die gleich zeichen beim größer-gleich weg (wg. SCREEN_WIDTH-1 !)
            return None

        self.spi.write(b"0x15")  # Set column address
        self.spi.write(col_start)
        self.spi.write(col_end)

        self.spi.write(b"0x75")  # Set row address
        self.spi.writer(row_start)
        self.spi.write(row_end)

        for x in range(0, self.screen_width):
            for y in range(0, self.screen_height):
                self.spi.write(pixels.pixel(x, y))

        # self.spi.write(
        # pixels)  # POTENZIELLE FEHLERQUELLE ! Entweder werden nicht alle nacheinander geschrieben oder es dauert zu lange etc. Hier besonders drauf achten ob das geht, wenn nicht, dann ist der Fehler höchstwahrscheinlich in dieser Zeile

    def draw_line(self, col_start, row_start, col_end, row_end, line_color):
        # Check if coordinates out of range
        if not (0 <= col_start <= self.screen_width) or not (0 <= col_end <= self.screen_width) or not (
                0 <= row_start <= self.screen_height) or not (0 <= row_end <= self.screen_height):
            return None

        self.spi.write(b"0x21")  # Draw line
        self.spi.write(col_start)
        self.spi.write(row_start)
        self.spi.write(col_end)
        self.spi.write(row_end)

        rgb_line = convert_16bits_to_rgb(line_color)

        self.spi.write(rgb_line[0])  # red
        self.spi.write(rgb_line[1])  # green
        self.spi.write(rgb_line[2])  # blue

    def draw_rectangle(self, col_start, row_start, col_end, row_end, line_color, bfill, fill_color):
        # Check if coordinates out of range
        if not (0 <= col_start <= self.screen_width) or not (0 <= col_end <= self.screen_width) or not (
                0 <= row_start <= self.screen_height) or not (0 <= row_end <= self.screen_height):
            return None

        self.spi.write(b"0x26")  # Enable fill
        if bfill:
            self.spi.write(b"0x01")
        else:
            self.spi.write(b"0x00")

        self.spi.write(b"0x22")  # Draw rectangle
        self.spi.write(col_start)
        self.spi.write(row_start)
        self.spi.write(col_end)
        self.spi.write(row_end)

        rgb_line = convert_16bits_to_rgb(line_color)
        rgb_fill = convert_16bits_to_rgb(fill_color)

        self.spi.write(rgb_line[0])  # red
        self.spi.write(rgb_line[1])  # green
        self.spi.write(rgb_line[2])  # blue

        self.spi.write(rgb_fill[0])  # red
        self.spi.write(rgb_fill[1])  # green
        self.spi.write(rgb_fill[2])  # blue

    def power_off_seq(self):
        # 1. Turn the display off
        self.spi.write(b"0xAE")
        # 2. Bring Vcc Enable logic low
        self.vcc_en.value(0)
        # 3. Delay 400 ms
        time.sleep_ms(400)
        # 4. Disconnect positive voltage supply to PmodOLEDrgb
        # Done !
