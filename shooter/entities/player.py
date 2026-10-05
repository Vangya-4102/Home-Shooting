import pygame
from config.settings import PLAYER_SIZE, RED_TEAM_COLOR, BLUE_TEAM_COLOR

class Player:
    def __init__(self, x=50, y=50, team="Red"):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.team = team

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface):
        color = RED_TEAM_COLOR if self.team == "Red" else BLUE_TEAM_COLOR
        pygame.draw.rect(surface, color, self.rect)
