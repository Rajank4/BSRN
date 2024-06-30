import os
import sys
import logging
import random
import time
from datetime import datetime
import TermTk as ttk
from TermTk.TTkCore.color import TTkColor
from TermTk.TTkWidgets.button import TTkButton

class CustomTTkButton(TTkButton):
    def setBgColor(self, color):
        self.style()['default']['bg'] = TTkColor.fg(color) if color else None
        self.update()

class StartPage:
    def __init__(self, root):
        self.root = root
        self.window = ttk.TTkWindow(parent=self.root, pos=(1,1), size=(70,30), title="Buzzword Bingo :)")
        self.winLayout = ttk.TTkGridLayout()
        self.window.setLayout(self.winLayout)

        welcome_label = ttk.TTkLabel(parent=self.window, pos=(1,1), text="Willkommen zum Buzzword Bingo!", font=("Times New Roman", 24))
        self.winLayout.addWidget(welcome_label, 0, 0, colspan=2)

        start_button = CustomTTkButton(border=True, text="Spiel starten", font=("Times New Roman", 24), checkable=True)
        start_button.clicked.connect(self.start_game)
        self.winLayout.addWidget(start_button, 1, 0)

        close_button = CustomTTkButton(border=True, text="Spiel beenden", font=("Times New Roman", 24), checkable=True)
        close_button.clicked.connect(self.spiel_beenden)
        self.winLayout.addWidget(close_button, 1, 1)

    def start_game(self):
        self.window.close()
        if len(sys.argv) != 6:
            print("Bitte geben Sie die notwendigen Argumente ein: [Spielername] [Pfad zur Buzzwords-Datei] [Log-Datei Speicherort] [Anzahl Zeilen] [Anzahl Spalten]")
            sys.exit(1)

        spielername = sys.argv[1]
        roundfile = sys.argv[2]
        log_path = sys.argv[3]
        zeilen = int(sys.argv[4])
        spalten = int(sys.argv[5])

        GamePage(self.root, spielername, roundfile, log_path, zeilen, spalten)

    def spiel_beenden(self):
        now = datetime.now()
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Abbruch des Spiels von der Startseite aus")
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Ende des Spiels von der Startseite aus")
        sys.exit(0)

class GamePage:
    def __init__(self, root, spielername, roundfile, log_path, zeilen, spalten):
        self.spielername = spielername
        self.roundfile = roundfile
        self.log_path = log_path
        self.zeilen = zeilen
        self.spalten = spalten

        self.buzzwords = self.read_buzzword(self.roundfile)
        self.used_buzzwords = set()

        self.create_log_file()

        self.root = root
        self.window = ttk.TTkWindow(parent=self.root, pos=(1,1), size=(70,30), title="Buzzword Bingo :)")
        self.winLayout = ttk.TTkGridLayout()
        self.window.setLayout(self.winLayout)

        self.buttons = [[None for _ in range(self.spalten)] for _ in range(self.zeilen)]

        self.setup_game()

    def create_log_file(self):
        os.makedirs(self.log_path, exist_ok=True)
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        log_file_name = os.path.join(self.log_path, f"log-{date_string}-{self.spielername}.txt")
        logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info(f"Log-Datei für {self.spielername} erstellt.")
        logging.info(f"Größe des Spielfelds Zeilen: {self.zeilen}, Spalten: {self.spalten}")

    def read_buzzword(self, roundfile):
        with open(roundfile, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return lines

    def spiel_beenden(self):
        now = datetime.now()
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Abbruch des Spiels von der Spielseite aus")
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Ende des Spiels von der Spielseite aus")
        sys.exit(0)

    def check_win(self):
        for i in range(self.zeilen):
            if all(self.buttons[i][j].isChecked() for j in range(self.spalten)):
                return True
        for j in range(self.spalten):
            if all(self.buttons[i][j].isChecked() for i in range(self.zeilen)):
                return True
        if all(self.buttons[i][i].isChecked() for i in range(min(self.zeilen, self.spalten))):
            return True
        if all(self.buttons[i][self.spalten-1-i].isChecked() for i in range(min(self.zeilen, self.spalten))):
            return True
        return False

    def log_buzzword(self, button, row, col):
        now = datetime.now()
        button_text = button.text()
        if button.isChecked():
            logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Button geklickt: {button_text}  (Zeile: {row+1}, Spalte: {col+1})")
            button.setBgColor('#88ffff')
        else:
            logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Button rückgängig: {button_text} ( Zeile: {row+1}, Spalte: {col+1})")
            button.setBgColor(None)
        if self.check_win():
            self.show_winner()
            self.spiel_beenden()

    def show_winner(self):
        winner_window = ttk.TTkWindow(parent=self.root, pos=(1,1), size=(50,10), title="Gewinner!")
        winner_layout = ttk.TTkGridLayout()
        winner_window.setLayout(winner_layout)

        winner_label = ttk.TTkLabel(parent=winner_window, pos=(1,1), text=f"Herzlichen Glückwunsch, {self.spielername}!")
        winner_layout.addWidget(winner_label, 0, 0, colspan=2)

        close_button = CustomTTkButton(border=True, text="Spiel beenden", font=("Times New Roman", 24), checkable=True)
        close_button.clicked.connect(self.spiel_beenden)
        winner_layout.addWidget(close_button, 1, 0, colspan=2)

    def setup_game(self):
        for i in range(self.zeilen):
            for j in range(self.spalten):
                if self.zeilen % 2 != 0 and self.spalten % 2 != 0 and i == self.zeilen // 2 and j == self.spalten // 2:
                    btn = CustomTTkButton(border=True, text="Joker", font=("Times New Roman", 24), checkable=True)
                    btn.setBgColor(color='#ff88ff')
                    self.winLayout.addWidget(btn, i, j)
                    self.buttons[i][j] = btn
                else:
                    buzzword = random.choice(self.buzzwords).strip()
                    while buzzword in self.used_buzzwords:
                        buzzword = random.choice(self.buzzwords).strip()
                    self.used_buzzwords.add(buzzword)
                    btn = CustomTTkButton(border=True, text=buzzword, font=("Times New Roman", 24), checkable=True)
                    btn.clicked.connect(lambda b=btn, row=i, col=j: self.log_buzzword(b, row, col))
                    self.winLayout.addWidget(btn, i, j)
                    self.buttons[i][j] = btn

        close_button = CustomTTkButton(border=True, text="Spiel beenden", font=("Times New Roman", 24), checkable=True)
        close_button.clicked.connect(self.spiel_beenden)
        self.winLayout.addWidget(close_button, self.zeilen, self.spalten-1)

def main():
    root = ttk.TTk()
    StartPage(root)
    root.mainloop()

if __name__ == "__main__":
    main()
