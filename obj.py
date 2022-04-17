from framebuf import FrameBuffer

from disp_matrix import DispMatrix


class _Entity:
    def __init__(self, x: int, y: int, w: int, h: int, vx: int, vy: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vx = vx
        self.vy = vy

    def draw(self, fbuf):
        fbuf.fill_rect(int(self.x), int(self.y), self.w, self.h, 0xFFFF)  # White


class Player(_Entity):
    pass


class Ball(_Entity):
    def __init__(self, x: int, y: int, w: int, h: int, vx: int, vy: int, screen_width: int, screen_height: int):
        super().__init__(x, y, w, h, vx, vy)  # Call constructor of inherited class
        self.score = 0
        self.game_over = False
        self.screen_width = screen_width
        self.screen_height = screen_height

    def get_score(self):
        return self.score

    def get_game_over(self):
        return self.game_over

    def update(self, dt: int, player: Player):  # Not sure if 'int' is correct type of dt !?
        self.x += self.vx * dt
        if self.x <= 0:
            self.x = 0
            self.vx = -self.vx

        if self.x >= self.screen_width - self.w:
            self.x = self.screen_width - self.w
            self.vx = - self.vx
        self.y += self.vy * dt
        if self.y <= 0:
            self.y = 0
            self.vy = -self.vy

        if self.y >= (self.screen_height - self.h - player.h):
            if (self.x >= player.x) and (self.x <= player.x + player.w):
                self.y = self.screen_height - self.h - player.h
                self.vy = -self.vy

                self.score += 1

                if self.score % 2 == 0:
                    self.vx += self.vx / abs(self.vx) * 1

                if self.score % 3 == 0:
                    self.vy += self.vy / abs(self.vy) * 1
            else:
                self.game_over = True
