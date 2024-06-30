import sys
import random
import argparse
import TermTk as ttk

class BingoButton(ttk.TTkButton):
    def __init__(self, *args, **kwargs):
        self.row = kwargs.pop('row')
        self.col = kwargs.pop('col')
        self.game = kwargs.pop('game')
        self.buzzword = kwargs.pop('buzzword')
        super().__init__(*args, **kwargs)
        self.clicked.connect(self.on_click)
        self.setText(self.buzzword)  # Initialize the text to the buzzword

    def on_click(self):
        if self.text() == self.buzzword:
            self.setText("X")
            self.game.marked[self.row][self.col] = True
        else:
            self.setText(self.buzzword)
            self.game.marked[self.row][self.col] = False

        if self.game.check_win():
            print(f"Spieler {self.game.current_player} hat gewonnen!")
            ttk.TTkHelper.quit()

class BingoGame:
    def __init__(self, rows, cols, players):
        self.rows = rows
        self.cols = cols
        self.players = players
        self.current_player = 1
        self.marked = [[False] * cols for _ in range(rows)]

    def check_win(self):
        for row in self.marked:
            if all(row):
                return True

        for col in range(self.cols):
            if all(self.marked[row][col] for row in range(self.rows)):
                return True

        if all(self.marked[i][i] for i in range(self.rows)):
            return True

        if all(self.marked[i][self.cols - i - 1] for i in range(self.rows)):
            return True

        return False

    def switch_player(self):
        self.current_player = (self.current_player % self.players) + 1

def read_buzzwords(filename):
    with open(filename, 'r') as file:
        buzzwords = [line.strip() for line in file if line.strip()]
    return buzzwords

def generate_bingo_card(buzzwords, rows, cols):
    if len(buzzwords) < rows * cols:
        raise ValueError("Nicht genug Buzzwords für die Bingo-Karte")
    return random.sample(buzzwords, rows * cols)

def display_bingo_card(frame, card, game, rows, cols):
    grid_layout = frame.layout()
    for r in range(rows):
        for c in range(cols):
            button = BingoButton(row=r, col=c, game=game, buzzword=card[r * cols + c], border=True)
            grid_layout.addWidget(button, row=r, col=c)

def main():
    parser = argparse.ArgumentParser(description="Buzzword Bingo")
    parser.add_argument("file", help="Datei mit Buzzwords")
    parser.add_argument("rows", type=int, help="Anzahl der Zeilen der Bingo-Karte")
    parser.add_argument("cols", type=int, help="Anzahl der Spalten der Bingo-Karte")
    parser.add_argument("players", type=int, help="Anzahl der Spieler")
    args = parser.parse_args()

    buzzwords = read_buzzwords(args.file)

    root = ttk.TTk()
    root.setLayout(ttk.TTkGridLayout())

    game = BingoGame(args.rows, args.cols, args.players)

    for player in range(args.players):
        player_frame = ttk.TTkFrame(title=f"Spieler {player + 1} Bingo-Karte:", layout=ttk.TTkGridLayout())
        card = generate_bingo_card(buzzwords, args.rows, args.cols)
        display_bingo_card(player_frame, card, game, args.rows, args.cols)
        root.layout().addWidget(player_frame, row=player, col=0)

    button = ttk.TTkButton(text="Beenden", border=True, command=ttk.TTkHelper.quit)
    root.layout().addWidget(button, row=args.players, col=0)

    root.mainloop()

if __name__ == "__main__":
    main()

#python3 bingo.py buzzwords.txt 3 3 2