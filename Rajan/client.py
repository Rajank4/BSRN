import os
import sys
import logging
import random
import socket
import threading
import json
from datetime import datetime
import TermTk as ttk
from TermTk.TTkCore.color import TTkColor
from TermTk.TTkWidgets.button import TTkButton
from TermTk.TTkWidgets.label import TTkLabel
from TermTk.TTkWidgets.window import TTkWindow
from TermTk.TTkWidgets.frame import TTkFrame
from TermTk.TTkLayouts.gridlayout import TTkGridLayout

# Globale Variable für den Spielstatus
spiel_status = {
    'board': [[None for _ in range(5)] for _ in range(5)],  # Beispiel: 5x5 Bingo-Board
    'winner': None
}

class CustomTTkButton(TTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_joker = False  # Flag, um zu identifizieren, ob dieser Button ein Joker ist

    def setBgColor(self, color):
        self.style()['default']['bg'] = TTkColor.fg(color) if color else None
        self.update()

    def setJoker(self, is_joker):
        self.is_joker = is_joker
        if is_joker:
            self.setChecked(True)  # Joker als ausgewählt markieren
            self.setEnabled(False)  # Joker-Button deaktivieren
            self.setBgColor(color='#87feff')  # Hintergrundfarbe für Joker setzen
        else:
            self.setChecked(False)  # Stellen Sie sicher, dass der Joker-Button nicht ausgewählt ist
            self.setEnabled(True)  # Button aktivieren, falls kein Joker


class GameClient:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.callbacks = []

    def send(self, data):
        self.sock.sendall(json.dumps(data).encode())

    def receive(self):
        while True:
            data = self.sock.recv(1024).decode()
            if data:
                state = json.loads(data)
                for callback in self.callbacks:
                    callback(state)

    def register_callback(self, callback):
        self.callbacks.append(callback)


class StartPage:
    def __init__(self, root, title, client, spielername):
        self.root = root
        self.title = title
        self.client = client
        self.spielername = spielername
        self.window = TTkWindow(parent=self.root, pos=(1, 1), size=(70, 10), title=self.title,
                                layout=TTkGridLayout())

        # Willkommenslabel
        welcome_label = TTkLabel(parent=self.window, text="Willkommen zum Buzzword Bingo!",
                                 alignment=ttk.TTkK.CENTER)
        self.window.layout().addWidget(welcome_label, 0, 0)

        # Buttons
        button_frame = TTkFrame(parent=self.window, border=False, layout=TTkGridLayout(), size=(70, 5))
        start_button = CustomTTkButton(border=True, text="Spiel starten", checkable=True)
        start_button.clicked.connect(self.start_game)
        button_frame.layout().addWidget(start_button, 0, 0)

        close_button = CustomTTkButton(border=True, text="Spiel beenden", checkable=True)
        close_button.clicked.connect(self.spiel_beenden)
        button_frame.layout().addWidget(close_button, 0, 1)

        self.window.layout().addWidget(button_frame, 1, 0, colspan=2)

    def start_game(self):
        self.window.close()
        if len(sys.argv) != 7:
            print(
                "Bitte geben Sie die notwendigen Argumente ein: [Spielername] [Pfad zur Buzzwords-Datei] [Log-Datei Speicherort] [Anzahl Zeilen] [Anzahl Spalten] [Titel]")
            sys.exit(1)

        spielername = sys.argv[1]
        roundfile = sys.argv[2]
        log_path = sys.argv[3]
        zeilen = int(sys.argv[4])
        spalten = int(sys.argv[5])
        titel = sys.argv[6]

        self.client.send({'action': 'start_game', 'spielername': spielername, 'roundfile': roundfile,
                          'log_path': log_path, 'zeilen': zeilen, 'spalten': spalten, 'titel': titel})
        GamePage(self.root, self.client, spielername, roundfile, log_path, zeilen, spalten, titel)

    def spiel_beenden(self):
        now = datetime.now()
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Abbruch des Spiels von der Startseite aus")
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Ende des Spiels von der Startseite aus")
        self.client.send({'action': 'exit'})
        sys.exit(0)


class GamePage:
    def __init__(self, root, client, spielername, roundfile, log_path, zeilen, spalten, titel):
        self.client = client
        self.client.register_callback(self.update_game_state)
        self.spielername = spielername
        self.roundfile = roundfile
        self.log_path = log_path
        self.zeilen = zeilen
        self.spalten = spalten
        self.titel = titel

        self.buzzwords = self.read_buzzword(self.roundfile)
        self.used_buzzwords = set()

        self.log_file = self.create_log_file()  # Log-Datei erstellen

        self.root = root
        window_width = spalten * 12 + 10  # Breite anpassen basierend auf den Spalten
        window_height = zeilen * 3 + 10   # Höhe anpassen basierend auf den Zeilen
        self.window = TTkWindow(parent=self.root, pos=(1, 1), size=(window_width, window_height), title=self.titel,
                                layout=TTkGridLayout())

        self.buttons = [[None for _ in range(self.spalten)] for _ in range(self.zeilen)]

        self.setup_game()

    def create_log_file(self):
        os.makedirs(self.log_path, exist_ok=True)
        now = datetime.now()
        date_string = now.strftime('%Y-%m-%d-%H-%M-%S')
        log_file_name = os.path.join(self.log_path, f"log-{date_string}-{self.spielername}.txt")
        logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.info(f"Spiel gestartet von {self.spielername} - {self.zeilen}x{self.spalten}")
        return logging.getLogger(log_file_name)

    def read_buzzword(self, roundfile):
        with open(roundfile, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return lines

    def spiel_beenden(self):
        now = datetime.now()
        logging.info(f"Ende des Spiels - {self.spielername} hat gewonnen!")
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Spiel beendet")
        self.client.send({'action': 'end_game', 'spielername': self.spielername})
        sys.exit(0)

    def check_win(self, row, col, checked):
        # Überprüfen, ob eine Zeile vollständig markiert ist
        if all(self.buttons[row][j].isChecked() for j in range(self.spalten)):
            return True
        # Überprüfen, ob eine Spalte vollständig markiert ist
        if all(self.buttons[i][col].isChecked() for i in range(self.zeilen)):
            return True
        # Überprüfen, ob die Hauptdiagonale vollständig markiert ist
        if row == col and all(self.buttons[i][i].isChecked() for i in range(self.zeilen)):
            return True
        # Überprüfen, ob die Nebendiagonale vollständig markiert ist
        if row + col == self.zeilen - 1 and all(self.buttons[i][self.spalten - 1 - i].isChecked() for i in range(self.zeilen)):
            return True
        return False

    def log_buzzword(self, button, row, col):
        now = datetime.now()
        button_text = button.text()
        if button.isChecked():
            self.log_file.info(
                f"{now.strftime('%H:%M:%S')} - {self.spielername} hat das folgende Feld ausgewählt: Zeile {row + 1}, Spalte {col + 1}, Wort: {button_text}")
            button.setBgColor('#87feff')
        else:
            self.log_file.info(
                f"{now.strftime('%H:%M:%S')} - {self.spielername} hat das folgende Feld rückgängig gemacht: Zeile {row + 1}, Spalte {col + 1}, Wort: {button_text}")
            button.setBgColor(None)

        if self.check_win(row, col, button.isChecked()):  # Überprüfen, ob das Spiel gewonnen wurde
            spiel_status['winner'] = self.spielername  # Gewinner setzen
            self.client.send({'action': 'update_state', 'board': [[btn.isChecked() for btn in row] for row in self.buttons], 'winner': self.spielername})
            self.show_winner()  # Gewinnermeldung anzeigen

    def show_winner(self):
        winner_window = TTkWindow(parent=self.root, pos=(10, 10), size=(50, 10), title="Gewinner!",
                                  layout=TTkGridLayout())
        winner_label = TTkLabel(parent=winner_window)
        winner_label.setText(f"Herzlichen Glückwunsch, {self.spielername}!")
        winner_label.setAlignment(ttk.TTkK.CENTER)

        winner_window.layout().addWidget(winner_label, 0, 0, rowspan=2)

        close_button = CustomTTkButton(border=True, text="Spiel beenden", checkable=True)
        close_button.clicked.connect(self.spiel_beenden)
        winner_window.layout().addWidget(close_button, 1, 0, colspan=2)

        self.root.addWidget(winner_window)
        winner_window.raiseWidget()

    def update_game_state(self, state):
        # Überprüfen, ob der Schlüssel 'board' im empfangenen Zustand vorhanden ist
        if 'board' in state:
            for i in range(self.zeilen):
                for j in range(self.spalten):
                    if state['board'][i][j] is not None:
                        self.buttons[i][j].setChecked(state['board'][i][j])
                        self.buttons[i][j].setBgColor('#87feff' if self.buttons[i][j].isChecked() else None)
        if 'winner' in state:
            spiel_status['winner'] = state['winner']
            self.show_winner()

    def setup_game(self):
        # Variablen initialisieren, um die Joker-Platzierung zu verfolgen
        joker_row = -1
        joker_col = -1

        # Überprüfen, ob die Rastergröße ungerade und >= 5x5 ist, um den Joker zu platzieren
        if self.zeilen >= 5 and self.spalten >= 5 and self.zeilen % 2 != 0 and self.spalten % 2 != 0:
            joker_row = self.zeilen // 2
            joker_col = self.spalten // 2

        for i in range(self.zeilen):
            for j in range(self.spalten):
                if i == joker_row and j == joker_col:
                    buzzword = "Joker"
                    # Einen nicht anklickbaren Joker-Button erstellen
                    btn = CustomTTkButton(border=True, text=buzzword, checkable=True)
                    btn.setJoker(True)  # Diesen Button als Joker markieren
                else:
                    buzzword = random.choice(self.buzzwords).strip()
                    while buzzword in self.used_buzzwords:
                        buzzword = random.choice(self.buzzwords).strip()
                    btn = CustomTTkButton(border=True, text=buzzword, checkable=True)
                    btn.clicked.connect(lambda b=btn, row=i, col=j: self.log_buzzword(b, row, col))

                self.window.layout().addWidget(btn, i, j)
                self.buttons[i][j] = btn

        close_button = CustomTTkButton(border=True, text="Spiel beenden", checkable=True)
        close_button.clicked.connect(self.spiel_beenden)
        self.window.layout().addWidget(close_button, self.zeilen, self.spalten - 1)


def main():
    root = ttk.TTk()
    if len(sys.argv) != 7:
        print(
            "Bitte geben Sie die notwendigen Argumente ein: [Spielername] [Pfad zur Buzzwords-Datei] [Log-Datei Speicherort] [Anzahl Zeilen] [Anzahl Spalten] [Titel]")
        sys.exit(1)
    titel = sys.argv[6]
    spielername = sys.argv[1]
    client = GameClient()
    threading.Thread(target=client.receive).start()
    StartPage(root, titel, client, spielername)
    root.mainloop()


if __name__ == "__main__":
    main()
