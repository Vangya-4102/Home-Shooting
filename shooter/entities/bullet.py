import pygame
from config.settings import WIDTH, HEIGHT, BULLET_SPEED, BULLET_SIZE

class Bullet:
    def __init__(self, x, y, dir_x, dir_y):
        self.x = float(x)
        self.y = float(y)
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.rect = pygame.Rect(int(self.x), int(self.y), BULLET_SIZE, BULLET_SIZE)

    def update(self):
        self.x += self.dir_x * BULLET_SPEED
        self.y += self.dir_y * BULLET_SPEED
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def is_out_of_bounds(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT
