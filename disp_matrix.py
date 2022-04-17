# Class provides an easy two dimensional matrix which mapps cartesion coordinates to list entrys There are two
# possibilities how to increment through pixels: horizontal or vertical therefore there are methods for each way
class DispMatrix:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.matrix = bytearray(self.width * self.height)
        self.fill(0)  # Black

    def set_pixel_h(self, x: int, y: int, val: int):
        if not (0 <= x < self.width) or not (0 <= y < self.height):
            return None

        self.matrix[x + y * self.width] = val

    def get_pixel_h(self, x: int, y: int) -> int:
        if not (0 <= x < self.width) or not (0 <= y < self.height):
            return 0

        return self.matrix[x + y * self.width]

    def set_pixel_v(self, x: int, y: int, val: int):
        if not (0 <= x < self.width) or not (0 <= y < self.height):
            return None

        self.matrix[x * self.height + y] = val

    def get_pixel_v(self, x: int, y: int) -> int:
        if not (0 <= x < self.width) or not (0 <= y < self.height):
            return 0

        return self.matrix[x * self.height + y]

    def fill(self, val: int):
        for i in self.matrix:
            self.matrix[i] = val

    def get_matrix(self) -> bytearray:
        return self.matrix

    def fill_rect(self, col_start: int, row_start: int, col_end: int, row_end: int, color: int):
        if not (0 <= col_start < self.width) or not (0 <= col_end < self.width) or not (
                0 <= row_start < self.height) or not (
                0 <= row_end < self.height):
            return None

        diff_width = abs(col_end - col_start)
        diff_height = abs(row_end - row_start)

        if diff_width == 0 == diff_height:
            # Just one pixel was selected
            self.set_pixel_v(col_start, row_start, color)
        elif (diff_width == 0) or (diff_height == 0):
            # Line shall be drawn
            if diff_width == 0:
                # Vertical line
                for i in range(0, diff_width):
                    self.set_pixel_v(i, row_start, color)
            elif diff_height == 0:
                # Horizontal line
                for i in range(0, diff_height):
                    self.set_pixel_h(col_start, i, color)
        else:
            for y in range(row_start, row_end):
                for x in range(col_start, col_end):
                    self.set_pixel_v(x, y, color)
