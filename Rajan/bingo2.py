import os
import sys
import logging
import random
from datetime import datetime
import TermTk as ttk
from TermTk.TTkCore.color import TTkColor
from TermTk.TTkWidgets.button import TTkButton
from TermTk.TTkWidgets.label import TTkLabel
from TermTk.TTkWidgets.window import TTkWindow
from TermTk.TTkWidgets.frame import TTkFrame
from TermTk.TTkLayouts.gridlayout import TTkGridLayout


class CustomTTkButton(TTkButton):
    def setBgColor(self, color):
        self.style()['default']['bg'] = TTkColor.fg(color) if color else None
        self.update()

class StartPage:
    def __init__(self, root, title):
        self.root = root
        self.title = title
        self.window = TTkWindow(parent=self.root, pos=(1, 1), size=(70, 10), title=self.title,
                                    layout=TTkGridLayout())

        # Welcome Label
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

        GamePage(self.root, spielername, roundfile, log_path, zeilen, spalten, titel)

    def spiel_beenden(self):
            now = datetime.now()
            logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Abbruch des Spiels von der Startseite aus")
            logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Ende des Spiels von der Startseite aus")
            sys.exit(0)


class GamePage:
    def __init__(self, root, spielername, roundfile, log_path, zeilen, spalten, titel):
        self.spielername = spielername
        self.roundfile = roundfile
        self.log_path = log_path
        self.zeilen = zeilen
        self.spalten = spalten
        self.titel = titel

        self.buzzwords = self.read_buzzword(self.roundfile)
        self.used_buzzwords = set()

        self.create_log_file()

        self.root = root
        window_width = spalten * 12 + 10  # Adjust width based on columns
        window_height = zeilen * 3 + 10   # Adjust height based on rows
        self.window = TTkWindow(parent=self.root, pos=(1, 1), size=(window_width, window_height), title=self.titel, layout=TTkGridLayout())

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
        if all(self.buttons[i][self.spalten - 1 - i].isChecked() for i in range(min(self.zeilen, self.spalten))):
            return True
        return False

    def log_buzzword(self, button, row, col):
        now = datetime.now()
        button_text = button.text()
        if button.isChecked():
            logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Button geklickt: {button_text}  (Zeile: {row + 1}, Spalte: {col + 1})")
            button.setBgColor('#88ffff')
        else:
            logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Button rückgängig: {button_text} (Zeile: {row + 1}, Spalte: {col + 1})")
            button.setBgColor(None)
        if self.check_win():
            self.show_winner()

    def show_winner(self):
        winner_window = TTkWindow(parent=self.root, pos=(10, 10), size=(50, 10), title="Gewinner!", layout=TTkGridLayout())
        winner_label = TTkLabel(parent=winner_window, text=f"Herzlichen Glückwunsch, {self.spielername}!", alignment=ttk.TTkK.CENTER)
        winner_window.layout().addWidget(winner_label, 0, 0, colspan=2)

        close_button = CustomTTkButton(border=True, text="Spiel beenden", checkable=True)
        close_button.clicked.connect(self.spiel_beenden)
        winner_window.layout().addWidget(close_button, 1, 0, colspan=2)

        self.root.addWidget(winner_window)
        winner_window.raiseWidget()

    def setup_game(self):
        for i in range(self.zeilen):
            for j in range(self.spalten):
                if self.zeilen % 2 != 0 and self.spalten % 2 != 0 and i == self.zeilen // 2 and j == self.spalten // 2:
                    btn = CustomTTkButton(border=True, text="Joker", checkable=True)
                    btn.setBgColor(color='#ff88ff')
                    self.window.layout().addWidget(btn, i, j)
                    self.buttons[i][j] = btn
                else:
                    buzzword = random.choice(self.buzzwords).strip()
                    while buzzword in self.used_buzzwords:
                        buzzword = random.choice(self.buzzwords).strip()
                    self.used_buzzwords.add(buzzword)
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
        print("Bitte geben Sie die notwendigen Argumente ein: [Spielername] [Pfad zur Buzzwords-Datei] [Log-Datei Speicherort] [Anzahl Zeilen] [Anzahl Spalten] [Titel]")
        sys.exit(1)
    titel = sys.argv[6]
    StartPage(root, titel)
    root.mainloop()


if __name__ == "__main__":
    main()
