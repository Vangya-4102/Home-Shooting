import socket
import json
import threading

class NetworkServer:
    def __init__(self, host='0.0.0.0', port=5555, max_players=4):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        self.max_players = max_players
        self.state = {}
        self.teams = {}
        self.game_started = False
        self.red_kills = 0
        self.blue_kills = 0
        self.lock = threading.Lock()

    def start(self):
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        player_counter = 0
        while True:
            try:
                conn, _ = self.server.accept()
                with self.lock:
                    if len(self.state) >= self.max_players or self.game_started:
                        conn.close()
                        continue
                    player_counter += 1
                    p_id = str(player_counter)
                    red_count = sum(1 for t in self.teams.values() if t == "Red")
                    blue_count = sum(1 for t in self.teams.values() if t == "Blue")
                    self.teams[p_id] = "Red" if red_count <= blue_count else "Blue"
                    
                    # Initialize default state with position coordinates
                    self.state[p_id] = {"x": 100, "y": 100, "team": self.teams[p_id], "bullets": []}

                threading.Thread(target=self._client_handler, args=(conn, p_id), daemon=True).start()
            except Exception:
                break

    def _client_handler(self, conn, p_id):
        try:
            conn.sendall(json.dumps({"id": p_id}).encode())
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                p_data = json.loads(data.decode())
                
                with self.lock:
                    if p_data.get("action") == "SWAP_TEAM":
                        target_id = str(p_data.get("target_id"))
                        new_team = p_data.get("new_team")
                        self.teams[target_id] = new_team
                        if target_id in self.state:
                            self.state[target_id]["team"] = new_team

                    elif p_data.get("action") == "START_GAME":
                        self.game_started = True

                    elif p_data.get("action") == "KILL_SCORED":
                        scoring_team = p_data.get("team")
                        if scoring_team == "Red": self.red_kills += 1
                        elif scoring_team == "Blue": self.blue_kills += 1

                    # Update position and bullet state without overwriting the entire dict
                    if p_id in self.state:
                        for key in ("x", "y", "bullets"):
                            if key in p_data:
                                self.state[p_id][key] = p_data[key]
                        self.state[p_id]["team"] = self.teams.get(p_id, "Red")

                    payload = {
                        "players": self.state,
                        "game_started": self.game_started,
                        "red_kills": self.red_kills,
                        "blue_kills": self.blue_kills,
                        "max_players": self.max_players
                    }
                    conn.sendall(json.dumps(payload).encode())
        except Exception:
            pass
        finally:
            with self.lock:
                self.state.pop(p_id, None)
                self.teams.pop(p_id, None)
            conn.close()