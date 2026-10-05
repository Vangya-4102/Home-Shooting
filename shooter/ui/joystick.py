import pygame
import math
from config.settings import WIDTH, HEIGHT, PLAYER_SPEED, SHOOT_COOLDOWN

class DualJoystick:
    def __init__(self):
        self.move_center = (150, HEIGHT - 150)
        self.shoot_center = (WIDTH - 150, HEIGHT - 150)
        self.radius = 70
        self.threshold = 25
        
        self.move_knob = list(self.move_center)
        self.shoot_knob = list(self.shoot_center)
        
        self.cooldown = 0
        self.last_shoot_dir = (1.0, 0.0)
        self.mouse_pressed = False
        self.mouse_pos = (0, 0)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse_pressed = True
            self.mouse_pos = event.pos
        elif event.type == pygame.MOUSEMOTION and self.mouse_pressed:
            self.mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_pressed = False

    def get_input(self):
        move_dx, move_dy = 0.0, 0.0
        shoot_dx, shoot_dy = 0.0, 0.0
        shooting = False
        
        self.move_knob = list(self.move_center)
        self.shoot_knob = list(self.shoot_center)

        if self.mouse_pressed:
            mx, my = self.mouse_pos
            if mx < WIDTH / 2:
                dist_move = math.hypot(mx - self.move_center[0], my - self.move_center[1])
                clamp_dist = min(dist_move, self.radius)
                if dist_move > 0:
                    move_dx = ((mx - self.move_center[0]) / dist_move) * (clamp_dist / self.radius)
                    move_dy = ((my - self.move_center[1]) / dist_move) * (clamp_dist / self.radius)
                    self.move_knob = [
                        self.move_center[0] + move_dx * self.radius,
                        self.move_center[1] + move_dy * self.radius
                    ]
            else:
                dist_shoot = math.hypot(mx - self.shoot_center[0], my - self.shoot_center[1])
                clamp_dist = min(dist_shoot, self.radius)
                if dist_shoot > 0:
                    s_x = (mx - self.shoot_center[0]) / dist_shoot
                    s_y = (my - self.shoot_center[1]) / dist_shoot
                    
                    self.shoot_knob = [
                        self.shoot_center[0] + s_x * clamp_dist,
                        self.shoot_center[1] + s_y * clamp_dist
                    ]
                    
                    if dist_shoot >= self.threshold:
                        shooting = True
                        shoot_dx, shoot_dy = s_x, s_y

        keys = pygame.key.get_pressed()
        kb_move_x, kb_move_y = 0, 0
        if keys[pygame.K_a]: kb_move_x -= 1
        if keys[pygame.K_d]: kb_move_x += 1
        if keys[pygame.K_w]: kb_move_y -= 1
        if keys[pygame.K_s]: kb_move_y += 1

        if kb_move_x != 0 or kb_move_y != 0:
            length = math.hypot(kb_move_x, kb_move_y)
            move_dx, move_dy = kb_move_x / length, kb_move_y / length

        kb_shoot_x, kb_shoot_y = 0, 0
        if keys[pygame.K_LEFT]:  kb_shoot_x -= 1
        if keys[pygame.K_RIGHT]: kb_shoot_x += 1
        if keys[pygame.K_UP]:    kb_shoot_y -= 1
        if keys[pygame.K_DOWN]:  kb_shoot_y += 1

        if kb_shoot_x != 0 or kb_shoot_y != 0:
            length = math.hypot(kb_shoot_x, kb_shoot_y)
            shoot_dx, shoot_dy = kb_shoot_x / length, kb_shoot_y / length
            shooting = True

        can_shoot = False
        if self.cooldown > 0:
            self.cooldown -= 1

        if shooting and self.cooldown == 0:
            can_shoot = True
            self.cooldown = SHOOT_COOLDOWN
            self.last_shoot_dir = (shoot_dx, shoot_dy)

        return move_dx * PLAYER_SPEED, move_dy * PLAYER_SPEED, can_shoot, self.last_shoot_dir

    def draw(self, surface):
        pygame.draw.circle(surface, (80, 80, 100), self.move_center, self.radius, 3)
        pygame.draw.circle(surface, (120, 120, 160), (int(self.move_knob[0]), int(self.move_knob[1])), 25)

        pygame.draw.circle(surface, (100, 80, 80), self.shoot_center, self.radius, 3)
        pygame.draw.circle(surface, (160, 80, 80), self.shoot_center, self.threshold, 1)
        pygame.draw.circle(surface, (220, 80, 80), (int(self.shoot_knob[0]), int(self.shoot_knob[1])), 25)
