import pygame
from config.settings import WIDTH, HEIGHT

# Map layout definitions and boundaries
MAPS = {
    "Arena": [
        pygame.Rect(200, 150, 40, 420),
        pygame.Rect(1040, 150, 40, 420),
        pygame.Rect(440, 200, 400, 40),
        pygame.Rect(440, 480, 400, 40)
    ]
}

# Team spawn locations per map (Red on left, Blue on right)
SPAWN_POINTS = {
    "Arena": {
        "Red": (100, HEIGHT // 2 - 20),
        "Blue": (WIDTH - 140, HEIGHT // 2 - 20)
    }
}

def get_spawn_point(map_name, team):
    map_spawns = SPAWN_POINTS.get(map_name, SPAWN_POINTS["Arena"])
    return map_spawns.get(team, (100, 100))

def draw_map(surface, map_name):
    surface.fill((30, 30, 40))
    walls = MAPS.get(map_name, [])
    for wall in walls:
        pygame.draw.rect(surface, (80, 90, 110), wall)

def move_with_collisions(rect, dx, dy, map_name):
    walls = MAPS.get(map_name, [])
    
    # Move X and check collisions
    rect.x += dx
    for wall in walls:
        if rect.colliderect(wall):
            if dx > 0: rect.right = wall.left
            elif dx < 0: rect.left = wall.right

    # Move Y and check collisions
    rect.y += dy
    for wall in walls:
        if rect.colliderect(wall):
            if dy > 0: rect.bottom = wall.top
            elif dy < 0: rect.top = wall.bottom

    # Keep inside screen bounds
    rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
    return rect.x, rect.y

def check_bullet_wall_collision(bullet_rect, map_name):
    walls = MAPS.get(map_name, [])
    return any(bullet_rect.colliderect(wall) for wall in walls)
