import socket
import threading
import json

# Spielstatus initialisieren
spiel_status = {
    'board': [[None for _ in range(5)] for _ in range(5)],  # Beispiel: 5x5 Bingo-Board
    'winner': None
}

# Liste der verbundenen Clients
clients = []


def handle_client(client_socket, addr):
    global spiel_status
    print(f"Verbunden mit {addr}")

    # Client in die Liste aufnehmen
    clients.append(client_socket)

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                print(f"Verbindung zu {addr} unterbrochen")
                break

            # Daten von JSON decodieren
            message = json.loads(data.decode())
            action = message.get('action')

            if action == 'update_board':
                row = message.get('row')
                col = message.get('col')
                checked = message.get('checked')
                spiel_status['board'][row][col] = checked

                # Überprüfen, ob jemand gewonnen hat
                if check_win(row, col, checked):
                    spiel_status['winner'] = message.get('spielername')

                # Nachricht an alle Clients senden
                send_to_all_clients(spiel_status)

            elif action == 'end_game':
                print(f"Spiel beendet von {message.get('spielername')}")
                send_to_all_clients({'action': 'end_game', 'spielername': message.get('spielername')})
                break

    finally:
        clients.remove(client_socket)
        client_socket.close()


def check_win(row, col, checked):
    # Einfache Überprüfung: Hier könnte die Logik für Bingo-Regeln eingefügt werden
    return checked


def send_to_all_clients(data):
    serialized_data = json.dumps(data).encode()
    for client in clients:
        client.send(serialized_data)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 65432))
    server_socket.listen()

    print("Server gestartet. Warte auf Verbindungen...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr)).start()
    except KeyboardInterrupt:
        print("Server wird heruntergefahren.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
