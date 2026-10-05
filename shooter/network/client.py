import socket
import json

class NetworkClient:
    def __init__(self, host_ip, port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host_ip, port))
        self.id = json.loads(self.client.recv(1024).decode())["id"]

    def sync(self, local_data):
        try:
            self.client.sendall(json.dumps(local_data).encode())
            data = self.client.recv(4096).decode()
            return json.loads(data)
        except Exception:
            return {}