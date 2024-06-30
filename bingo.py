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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_joker = False  # Flag to identify if this button is a Joker

    def setBgColor(self, color):
        self.style()['default']['bg'] = TTkColor.fg(color) if color else None
        self.update()

    def setJoker(self, is_joker):
        self.is_joker = is_joker
        if is_joker:
            self.setChecked(True)  # Automatically mark the Joker as checked
            self.setEnabled(False)  # Disable the Joker button
            self.setBgColor(color='#87feff')  # Set background color for the Joker
        else:
            self.setChecked(False)  # Ensure the Joker button starts unchecked
            self.setEnabled(True)  # Enable the button if it's not a Joker


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
        if len(sys.argv) < 7:
            print(
                "Bitte geben Sie die notwendigen Argumente ein: [Anzahl Spieler] [Spielername1] [Spielername2] ... [Pfad zur Buzzwords-Datei] [Log-Datei Speicherort] [Anzahl Zeilen] [Anzahl Spalten] [Titel]")
            sys.exit(1)

        anzahl_spieler = int(sys.argv[1])
        spielernamen = sys.argv[2:2 + anzahl_spieler]
        roundfile = sys.argv[2 + anzahl_spieler]
        log_path = sys.argv[3 + anzahl_spieler]
        zeilen = int(sys.argv[4 + anzahl_spieler])
        spalten = int(sys.argv[5 + anzahl_spieler])
        titel = sys.argv[6 + anzahl_spieler]

        self.games = []
        for i, spielername in enumerate(spielernamen):
            x_offset = 10 + i * (spalten * 12 + 20)
            y_offset = 10
            game = GamePage(self.root, spielername, roundfile, log_path, zeilen, spalten, titel, pos=(x_offset, y_offset))
            self.games.append(game)

    def spiel_beenden(self):
        now = datetime.now()
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Abbruch des Spiels von der Startseite aus")
        logging.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Ende des Spiels von der Startseite aus")
        sys.exit(0)


class GamePage:
    def __init__(self, root, spielername, roundfile, log_path, zeilen, spalten, titel, pos):
        self.spielername = spielername
        self.roundfile = roundfile
        self.log_path = log_path
        self.zeilen = zeilen
        self.spalten = spalten
        self.titel = titel

        self.buzzwords = self.read_buzzword(self.roundfile)
        self.used_buzzwords = set()

        self.log_file = self.create_log_file()  # Create log file object

        self.root = root
        window_width = spalten * 12 + 10  # Adjust width based on columns
        window_height = zeilen * 3 + 10   # Adjust height based on rows
        self.window = TTkWindow(parent=self.root, pos=pos, size=(window_width, window_height), title=f"{self.titel} - {self.spielername}",
                                layout=TTkGridLayout())

        self.buttons = [[None for _ in range(self.spalten)] for _ in range(self.zeilen)]

        self.setup_game()

    def create_log_file(self):
        os.makedirs(self.log_path, exist_ok=True)
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d-%H-%M-%S")
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
        sys.exit(0)

    def check_win(self):
        # Check if all buttons in any row, column, or diagonal are checked
        for i in range(self.zeilen):
            if all(self.buttons[i][j].isChecked() for j in range(self.spalten) if self.buttons[i][j]):
                return True

        for j in range(self.spalten):
            if all(self.buttons[i][j].isChecked() for i in range(self.zeilen) if self.buttons[i][j]):
                return True

        if all(self.buttons[i][i].isChecked() for i in range(min(self.zeilen, self.spalten)) if self.buttons[i][i]):
            return True

        if all(self.buttons[i][self.spalten - 1 - i].isChecked() for i in range(min(self.zeilen, self.spalten)) if self.buttons[i][self.spalten - 1 - i]):
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

        if self.check_win():  # Check if the game has been won
            self.show_winner()  # Display the winner message

    def show_winner(self):
        # Check if there is a winner before showing the winner window
        if self.check_win():
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
            winner_window.raiseWidget()  # Bring the winner window to the top
            winner_window.update()
            self.root.update()

    def setup_game(self):
        # Initialize variables to track the Joker placement
        joker_row = -1
        joker_col = -1

        # Check if the grid size is odd and >= 5x5 to place the Joker
        if self.zeilen >= 5 and self.spalten >= 5 and self.zeilen % 2 != 0 and self.spalten % 2 != 0:
            joker_row = self.zeilen // 2
            joker_col = self.spalten // 2

        for i in range(self.zeilen):
            for j in range(self.spalten):
                if i == joker_row and j == joker_col:
                    buzzword = "Joker"
                    # Create a non-clickable Joker button
                    btn = CustomTTkButton(border=True, text=buzzword, checkable=True)
                    btn.setJoker(True)  # Mark this button as a Joker
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
    if len(sys.argv) < 7:
        print("Bitte geben Sie die notwendigen Argumente ein: [Anzahl Spieler] [Spielername1] [Spielername2] ... [Pfad zur Buzzwords-Datei] [Log-Datei Speicherort] [Anzahl Zeilen] [Anzahl Spalten] [Titel]")
        sys.exit(1)
    titel = sys.argv[-1]
    StartPage(root, titel)
    root.mainloop()


if __name__ == "__main__":
    main()


#python3 bingo.py 2 Spieler1 Spieler2 buzzwords.txt logs/ 5 5 "Buzzword Bingo"

