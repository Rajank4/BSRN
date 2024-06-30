import socket
import threading
import json
from datetime import datetime

# Globale Variable für den Spielstatus
spiel_status = {
    'board': [[None for _ in range(5)] for _ in range(5)],  # Beispiel: 5x5 Bingo-Board
    'winner': None
}

# Liste der verbundenen Clients
connected_clients = []

class GameServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server läuft auf {self.host}:{self.port}")

    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Neue Verbindung von {client_address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        connected_clients.append(client_socket)
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                state = json.loads(data)
                self.process_client_data(state, client_socket)
            except Exception as e:
                print(f"Fehler bei der Verarbeitung von Client-Daten: {e}")
                break
        client_socket.close()
        connected_clients.remove(client_socket)
        print("Client Verbindung geschlossen")

    def process_client_data(self, data, client_socket):
        action = data.get('action')
        if action == 'update_state':
            spiel_status['board'] = data['board']
            spiel_status['winner'] = data['winner']
            self.broadcast_state()
        elif action == 'end_game':
            spiel_status['winner'] = data['spielername']
            self.broadcast_state()
        elif action == 'exit':
            client_socket.close()
            connected_clients.remove(client_socket)

    def broadcast_state(self):
        for client_socket in connected_clients:
            try:
                client_socket.sendall(json.dumps(spiel_status).encode())
            except Exception as e:
                print(f"Fehler beim Senden an Client: {e}")

def main():
    server = GameServer()
    server.start()

if __name__ == "__main__":
    main()
