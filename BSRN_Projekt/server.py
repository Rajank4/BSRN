import socket  # Modul für Netzwerk-Socket-Kommunikation
import threading  # Modul für Multithreading
import json  # Modul für JSON-Codierung und -Decodierung


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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP/IP-Socket erstellen
        self.server_socket.bind((self.host, self.port))  # Socket an Adresse und Port binden
        self.server_socket.listen(5)    # Auf eingehende Verbindungen lauschen, mit einer maximalen Warteschlange von 5
        print(f"Server läuft auf {self.host}:{self.port}")

    def start(self):
        while True:
            client_socket, client_address = self.server_socket.accept()     # Auf neue Verbindungen warten
            print(f"Neue Verbindung von {client_address}")      # Thread für jeden Client erstellen
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))  # Thread für jeden
            # Client erstellen
            client_thread.start()   # Thread starten, um Client zu behandeln

    def handle_client(self, client_socket):
        connected_clients.append(client_socket)  # Client-Socket zur Liste der verbundenen Clients hinzufügen
        while True:
            try:
                data = client_socket.recv(1024).decode()   # Daten vom Client empfangen
                if not data:
                    break  # Wenn keine Daten empfangen wurden, Verbindung beenden
                state = json.loads(data)  # JSON-Daten decodieren
                self.process_client_data(state, client_socket)  # Client-Daten verarbeiten
            except Exception as e:
                print(f"Fehler bei der Verarbeitung von Client-Daten: {e}")
                break
        client_socket.close()  # Client-Socket schließen
        connected_clients.remove(client_socket)  # Client-Socket aus der Liste der verbundenen Clients entfernen
        print("Client Verbindung geschlossen")

    def process_client_data(self, data, client_socket):
        action = data.get('action')  # Aktion aus den empfangenen Daten extrahieren
        if action == 'update_state':
            spiel_status['board'] = data['board']  # Spielbrett aktualisieren
            spiel_status['winner'] = data['winner']  # Gewinner aktualisieren
            self.broadcast_state()  # Aktualisierten Spielzustand an alle Clients senden
        elif action == 'end_game':
            spiel_status['winner'] = data['spielername']  # Gewinner des Spiels setzen
            self.broadcast_state()  # Aktualisierten Spielzustand an alle Clients senden
        elif action == 'exit':
            client_socket.close()  # Verbindung mit Client schließen
            connected_clients.remove(client_socket)  # Client-Socket aus der Liste der verbundenen Clients entfernen

    def broadcast_state(self):
        for client_socket in connected_clients:
            try:
                client_socket.sendall(json.dumps(spiel_status).encode())  # Aktuellen Spielstatus an jeden Client senden
            except Exception as e:
                print(f"Fehler beim Senden an Client: {e}")

def main():
    server = GameServer()  # GameServer-Objekt erstellen
    server.start()  # Server starten, um auf eingehende Verbindungen zu warten

if __name__ == "__main__":
    main()  # Hauptfunktion aufrufen, um den Server zu starten