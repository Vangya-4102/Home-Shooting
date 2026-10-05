import pygame
import sys
import time
from config.settings import (
    WIDTH, HEIGHT, FPS, PORT, PLAYER_SIZE, BULLET_SIZE, 
    MATCH_DURATION_SECONDS, RED_TEAM_COLOR, BLUE_TEAM_COLOR
)
from network.utils import get_local_ip
from network.server import NetworkServer
from network.client import NetworkClient
from entities.player import Player
from entities.bullet import Bullet
from ui.joystick import DualJoystick
from ui.menus import MainMenu, MapSelectMenu, LobbyMenu, TeamSetupMenu
from world.maps import draw_map, move_with_collisions, check_bullet_wall_collision, get_spawn_point

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Team Shooter")
clock = pygame.time.Clock()

local_ip = get_local_ip()
main_menu = MainMenu()
map_select_menu = MapSelectMenu()
lobby_menu = LobbyMenu(default_ip=local_ip)
team_setup_menu = TeamSetupMenu()
controls = DualJoystick()

state = "MENU"
client = None
server = None
is_host = False
selected_map = "Arena"
max_players = 4
player = Player(100, 100)
local_bullets = []
match_start_time = 0
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 64)

running = True
while running:
    if state == "MENU":
        action = main_menu.handle_input()
        if action == "QUIT": running = False
        elif action == "HOST": state = "MAP_SELECT"
        elif action == "JOIN": state = "LOBBY_SELECT"
        main_menu.draw(screen)

    elif state == "MAP_SELECT":
        action, map_choice, max_p = map_select_menu.handle_input()
        max_players = max_p
        if action == "QUIT": running = False
        elif action == "BACK": state = "MENU"
        elif action == "CONTINUE":
            selected_map = map_choice
            try:
                server = NetworkServer(port=PORT, max_players=max_players)
                server.start()
                is_host = True
            except OSError:
                pass
            client = NetworkClient(local_ip, port=PORT)
            state = "TEAM_SETUP"
        map_select_menu.draw(screen)

    elif state == "LOBBY_SELECT":
        action, target_ip = lobby_menu.handle_input()
        if action == "QUIT": running = False
        elif action == "BACK": state = "MENU"
        elif action == "CONNECT":
            try:
                client = NetworkClient(target_ip, port=PORT)
                is_host = False
                state = "TEAM_SETUP"
            except Exception as e:
                print(f"Connection failed: {e}")
        lobby_menu.draw(screen)

    elif state == "TEAM_SETUP":
        response = client.sync({"x": player.rect.x, "y": player.rect.y, "map": selected_map})
        players_state = response.get("players", {})
        game_started = response.get("game_started", False)

        action = team_setup_menu.handle_input(is_host, players_state)
        if action == "QUIT":
            running = False
        elif is_host and action == "START":
            client.sync({"action": "START_GAME"})
            game_started = True
        elif is_host and action and action.startswith("SWAP_TEAM"):
            _, target_id, new_team = action.split(":")
            client.sync({"action": "SWAP_TEAM", "target_id": target_id, "new_team": new_team})

        if client.id in players_state:
            player.team = players_state[client.id].get("team", "Red")

        # Start match & position player at team spawn point
        if game_started:
            spawn_x, spawn_y = get_spawn_point(selected_map, player.team)
            player.set_position(spawn_x, spawn_y)
            client.sync({"x": player.rect.x, "y": player.rect.y, "team": player.team})
            match_start_time = time.time()
            state = "GAME"

        team_setup_menu.draw(screen, is_host, players_state, max_players)

    elif state == "GAME":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            controls.handle_event(event)

        dx, dy, can_shoot, shoot_dir = controls.get_input()
        player.rect.x, player.rect.y = move_with_collisions(player.rect, dx, dy, selected_map)

        if can_shoot:
            spawn_x = player.rect.centerx - BULLET_SIZE // 2
            spawn_y = player.rect.centery - BULLET_SIZE // 2
            local_bullets.append(Bullet(spawn_x, spawn_y, shoot_dir[0], shoot_dir[1]))

        active_bullets = []
        for bullet in local_bullets:
            bullet.update()
            if not bullet.is_out_of_bounds() and not check_bullet_wall_collision(bullet.rect, selected_map):
                active_bullets.append(bullet)
        local_bullets = active_bullets

        response = client.sync({
            "x": player.rect.x,
            "y": player.rect.y,
            "team": player.team,
            "bullets": [{"x": b.rect.x, "y": b.rect.y} for b in local_bullets]
        })

        players_state = response.get("players", {})
        red_kills = response.get("red_kills", 0)
        blue_kills = response.get("blue_kills", 0)

        draw_map(screen, selected_map)
        controls.draw(screen)

        for p_id, p_data in players_state.items():
            if "x" not in p_data or "y" not in p_data:
                continue
            color = RED_TEAM_COLOR if p_data.get("team") == "Red" else BLUE_TEAM_COLOR
            pygame.draw.rect(screen, color, (p_data["x"], p_data["y"], PLAYER_SIZE, PLAYER_SIZE))

            for bullet in p_data.get("bullets", []):
                pygame.draw.rect(screen, color, (bullet["x"], bullet["y"], BULLET_SIZE, BULLET_SIZE))

        elapsed = time.time() - match_start_time
        remaining_seconds = max(0, int(MATCH_DURATION_SECONDS - elapsed))
        mins, secs = divmod(remaining_seconds, 60)

        timer_text = font.render(f"Time: {mins:02d}:{secs:02d}", True, (255, 255, 255))
        score_text = font.render(f"RED: {red_kills}  |  BLUE: {blue_kills}", True, (255, 255, 255))
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 10))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 40))

        if remaining_seconds <= 0:
            state = "GAME_OVER"

    elif state == "GAME_OVER":
        screen.fill((20, 20, 30))
        if red_kills > blue_kills:
            winner_text = "RED TEAM WINS!"
            win_color = RED_TEAM_COLOR
        elif blue_kills > red_kills:
            winner_text = "BLUE TEAM WINS!"
            win_color = BLUE_TEAM_COLOR
        else:
            winner_text = "IT'S A DRAW!"
            win_color = (255, 255, 255)

        title = big_font.render(winner_text, True, win_color)
        sub = font.render(f"Final Score - Red: {red_kills} | Blue: {blue_kills}", True, (200, 200, 200))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 30))

        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                running = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
