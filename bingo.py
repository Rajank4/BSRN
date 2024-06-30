import sys
import random
import argparse
import TermTk as ttk

class BingoButton(ttk.TTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clicked.connect(self.on_click)

    def on_click(self):
        # Bei Klick den Button-Text markieren oder unmarkieren
        if self.border():
            self.setBorder(False)
            self.setStyle(None)
        else:
            self.setBorder(True)
            self.setStyle(ttk.TTkColor.bg('#00FF00'))

# Funktion zum Einlesen der Buzzwords aus einer Datei
def read_buzzwords(filename):
    with open(filename, 'r') as file:
        buzzwords = [line.strip() for line in file if line.strip()]
    return buzzwords

# Funktion zum Erstellen einer zufälligen Bingo-Karte
def generate_bingo_card(buzzwords, rows, cols):
    if len(buzzwords) < rows * cols:
        raise ValueError("Nicht genug Buzzwords für die Bingo-Karte")
    return random.sample(buzzwords, rows * cols)

# Funktion zum Anzeigen der Bingo-Karte
def display_bingo_card(frame, card, rows, cols):
    grid_layout = frame.layout()
    for r in range(rows):
        for c in range(cols):
            button = BingoButton(text=card[r * cols + c], border=True)
            grid_layout.addWidget(button, row=r, col=c)

# Hauptfunktion
def main():
    # Kommandozeilenargumente parsen
    parser = argparse.ArgumentParser(description="Buzzword Bingo")
    parser.add_argument("file", help="Datei mit Buzzwords")
    parser.add_argument("rows", type=int, help="Anzahl der Zeilen der Bingo-Karte")
    parser.add_argument("cols", type=int, help="Anzahl der Spalten der Bingo-Karte")
    parser.add_argument("players", type=int, help="Anzahl der Spieler")

    args = parser.parse_args()

    # Buzzwords einlesen
    buzzwords = read_buzzwords(args.file)

    # GUI initialisieren
    root = ttk.TTk()
    root.setLayout(ttk.TTkGridLayout())

    # Für jeden Spieler eine Bingo-Karte generieren und anzeigen
    for player in range(args.players):
        player_frame = ttk.TTkFrame(title=f"Spieler {player + 1} Bingo-Karte:", layout=ttk.TTkGridLayout())
        card = generate_bingo_card(buzzwords, args.rows, args.cols)
        display_bingo_card(player_frame, card, args.rows, args.cols)
        root.layout().addWidget(player_frame, row=player, col=0)

    button = BingoButton(text="Beenden", border=True, command=ttk.TTkHelper.quit)
    root.layout().addWidget(button, row=args.players, col=0)

    root.mainloop()

if __name__ == "__main__":
    main()




#python3 bingo.py buzzwords.txt 3 3 2
