import pygame
from config.settings import WIDTH, HEIGHT, DEFAULT_MAX_PLAYERS, RED_TEAM_COLOR, BLUE_TEAM_COLOR
from world.maps import MAPS

class MainMenu:
    def __init__(self):
        self.title_font = pygame.font.SysFont(None, 64)
        self.button_font = pygame.font.SysFont(None, 36)
        self.host_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 40, 240, 60)
        self.join_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 40, 240, 60)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.host_btn.collidepoint(pos):
                    return "HOST"
                if self.join_btn.collidepoint(pos):
                    return "JOIN"
        return None

    def draw(self, surface):
        surface.fill((20, 20, 30))
        title_text = self.title_font.render("2D Local Shooter", True, (255, 255, 255))
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 120))

        pygame.draw.rect(surface, (50, 150, 250), self.host_btn, border_radius=10)
        host_text = self.button_font.render("Host Game", True, (255, 255, 255))
        surface.blit(host_text, (self.host_btn.centerx - host_text.get_width() // 2, self.host_btn.centery - host_text.get_height() // 2))

        pygame.draw.rect(surface, (50, 200, 100), self.join_btn, border_radius=10)
        join_text = self.button_font.render("Join Game", True, (255, 255, 255))
        surface.blit(join_text, (self.join_btn.centerx - join_text.get_width() // 2, self.join_btn.centery - join_text.get_height() // 2))


class MapSelectMenu:
    def __init__(self):
        self.title_font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 32)
        self.map_buttons = []
        self.selected_map = "Arena"
        self.max_players = DEFAULT_MAX_PLAYERS

        map_names = list(MAPS.keys())
        for i, name in enumerate(map_names):
            btn = pygame.Rect(WIDTH // 2 - 220 + i * 220, 200, 200, 60)
            self.map_buttons.append((btn, name))

        self.minus_btn = pygame.Rect(WIDTH // 2 - 80, 340, 40, 40)
        self.plus_btn = pygame.Rect(WIDTH // 2 + 40, 340, 40, 40)
        self.continue_btn = pygame.Rect(WIDTH // 2 - 120, 460, 240, 60)
        self.back_btn = pygame.Rect(20, 20, 100, 40)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT", None, self.max_players

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.back_btn.collidepoint(pos):
                    return "BACK", None, self.max_players

                for btn, map_name in self.map_buttons:
                    if btn.collidepoint(pos):
                        self.selected_map = map_name

                if self.minus_btn.collidepoint(pos) and self.max_players > 2:
                    self.max_players -= 1
                elif self.plus_btn.collidepoint(pos) and self.max_players < 10:
                    self.max_players += 1

                if self.continue_btn.collidepoint(pos):
                    return "CONTINUE", self.selected_map, self.max_players

        return None, None, self.max_players

    def draw(self, surface):
        surface.fill((20, 20, 30))
        title = self.title_font.render("Select Map & Game Options", True, (255, 255, 255))
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        # Map Selection Buttons
        for btn, name in self.map_buttons:
            color = (50, 180, 100) if name == self.selected_map else (70, 80, 100)
            pygame.draw.rect(surface, color, btn, border_radius=8)
            text = self.button_font.render(name, True, (255, 255, 255))
            surface.blit(text, (btn.centerx - text.get_width() // 2, btn.centery - text.get_height() // 2))

        # Max Players Controls
        lbl = self.button_font.render(f"Max Players: {self.max_players}", True, (255, 255, 255))
        surface.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, 305))

        pygame.draw.rect(surface, (180, 60, 60), self.minus_btn, border_radius=6)
        pygame.draw.rect(surface, (60, 180, 60), self.plus_btn, border_radius=6)
        
        minus_txt = self.button_font.render("-", True, (255, 255, 255))
        plus_txt = self.button_font.render("+", True, (255, 255, 255))
        surface.blit(minus_txt, (self.minus_btn.centerx - minus_txt.get_width() // 2, self.minus_btn.centery - minus_txt.get_height() // 2))
        surface.blit(plus_txt, (self.plus_btn.centerx - plus_txt.get_width() // 2, self.plus_btn.centery - plus_txt.get_height() // 2))

        # Continue Button
        pygame.draw.rect(surface, (50, 150, 250), self.continue_btn, border_radius=10)
        cont_text = self.button_font.render("Continue", True, (255, 255, 255))
        surface.blit(cont_text, (self.continue_btn.centerx - cont_text.get_width() // 2, self.continue_btn.centery - cont_text.get_height() // 2))

        pygame.draw.rect(surface, (150, 50, 50), self.back_btn, border_radius=6)
        back_text = self.button_font.render("Back", True, (255, 255, 255))
        surface.blit(back_text, (self.back_btn.centerx - back_text.get_width() // 2, self.back_btn.centery - back_text.get_height() // 2))


class TeamSetupMenu:
    def __init__(self):
        self.title_font = pygame.font.SysFont(None, 48)
        self.font = pygame.font.SysFont(None, 32)
        self.start_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT - 100, 240, 50)

    def handle_input(self, is_host, world_state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if is_host and self.start_btn.collidepoint(pos):
                    return "START"

                # Host can click on a player entry to swap their team
                if is_host:
                    y_offset = 180
                    for p_id in sorted(world_state.keys()):
                        item_rect = pygame.Rect(WIDTH // 2 - 200, y_offset, 400, 40)
                        if item_rect.collidepoint(pos):
                            current_team = world_state[p_id].get("team", "Red")
                            new_team = "Blue" if current_team == "Red" else "Red"
                            return f"SWAP_TEAM:{p_id}:{new_team}"
                        y_offset += 50
        return None

    def draw(self, surface, is_host, world_state, max_players):
        surface.fill((20, 20, 30))
        title = self.title_font.render(f"Team Assignment Lobby ({len(world_state)}/{max_players})", True, (255, 255, 255))
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        y_offset = 180
        for p_id in sorted(world_state.keys()):
            p_data = world_state[p_id]
            team = p_data.get("team", "Red")
            color = RED_TEAM_COLOR if team == "Red" else BLUE_TEAM_COLOR

            card = pygame.Rect(WIDTH // 2 - 200, y_offset, 400, 40)
            pygame.draw.rect(surface, (40, 40, 50), card, border_radius=6)
            pygame.draw.rect(surface, color, card, 2, border_radius=6)

            txt = self.font.render(f"Player {p_id} - Team: {team}", True, color)
            surface.blit(txt, (card.x + 15, card.centery - txt.get_height() // 2))

            if is_host:
                hint = self.font.render("Click to Swap", True, (150, 150, 150))
                surface.blit(hint, (card.right - hint.get_width() - 15, card.centery - hint.get_height() // 2))

            y_offset += 50

        if is_host:
            pygame.draw.rect(surface, (50, 200, 100), self.start_btn, border_radius=8)
            btn_text = self.font.render("Start Match", True, (255, 255, 255))
            surface.blit(btn_text, (self.start_btn.centerx - btn_text.get_width() // 2, self.start_btn.centery - btn_text.get_height() // 2))
        else:
            wait_text = self.font.render("Waiting for host to start the match...", True, (200, 200, 200))
            surface.blit(wait_text, (WIDTH // 2 - wait_text.get_width() // 2, HEIGHT - 80))


class LobbyMenu:
    def __init__(self, default_ip="127.0.0.1"):
        self.title_font = pygame.font.SysFont(None, 48)
        self.input_font = pygame.font.SysFont(None, 36)
        self.ip_address = default_ip
        self.input_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 30, 300, 50)
        self.connect_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 50, 240, 50)
        self.back_btn = pygame.Rect(20, 20, 100, 40)
        self.active = True

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT", None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                self.active = self.input_rect.collidepoint(pos)
                if self.connect_btn.collidepoint(pos):
                    return "CONNECT", self.ip_address
                if self.back_btn.collidepoint(pos):
                    return "BACK", None

            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    return "CONNECT", self.ip_address
                elif event.key == pygame.K_BACKSPACE:
                    self.ip_address = self.ip_address[:-1]
                else:
                    if len(self.ip_address) < 15 and (event.unicode.isdigit() or event.unicode == '.'):
                        self.ip_address += event.unicode

        return None, None

    def draw(self, surface):
        surface.fill((20, 20, 30))
        title = self.title_font.render("Enter Host IP Address", True, (255, 255, 255))
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        border_color = (100, 200, 255) if self.active else (100, 100, 100)
        pygame.draw.rect(surface, (40, 40, 50), self.input_rect)
        pygame.draw.rect(surface, border_color, self.input_rect, 2)

        txt_surface = self.input_font.render(self.ip_address, True, (255, 255, 255))
        surface.blit(txt_surface, (self.input_rect.x + 10, self.input_rect.y + 12))

        pygame.draw.rect(surface, (50, 200, 100), self.connect_btn, border_radius=8)
        btn_text = self.input_font.render("Connect", True, (255, 255, 255))
        surface.blit(btn_text, (self.connect_btn.centerx - btn_text.get_width() // 2, self.connect_btn.centery - btn_text.get_height() // 2))

        pygame.draw.rect(surface, (150, 50, 50), self.back_btn, border_radius=6)
        back_text = self.input_font.render("Back", True, (255, 255, 255))
        surface.blit(back_text, (self.back_btn.centerx - back_text.get_width() // 2, self.back_btn.centery - back_text.get_height() // 2))
