import random
import argparse
from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer
from textual.containers import Container
from textual.widget import Widget

class BingoGrid(Widget):
    def __init__(self, buzzwords, grid_columns, grid_rows):
        super().__init__()
        self.buzzwords = buzzwords
        self.grid_columns = grid_columns
        self.grid_rows = grid_rows
        self.selected = set()

    def create_grid(self):
        used_words = set()
        for _ in range(self.grid_columns * self.grid_rows):
            while True:
                word = random.choice(self.buzzwords)
                if word not in used_words:
                    used_words.add(word)
                    break
            button = Button(label=word)
            button.on_click = lambda b=button: self.button_click(b)
            self.mount(button)

    def button_click(self, button):
        if button not in self.selected:
            button.styles.background = "red"
            button.styles.color = "white"
            self.selected.add(button)
        else:
            button.styles.background = "white"
            button.styles.color = "black"
            self.selected.remove(button)

    async def on_mount(self):
        self.create_grid()

class BingoApp(App):
    # CSS_PATH = "styles.css"

    def __init__(self, buzzword_file, grid_columns, grid_rows, player_name, num_players):
        super().__init__()
        self.buzzword_file = buzzword_file
        self.grid_columns = grid_columns
        self.grid_rows = grid_rows
        self.player_name = player_name
        self.num_players = num_players

    def load_buzzwords(self):
        with open(self.buzzword_file, 'r') as file:
            return [line.strip() for line in file]

    async def on_mount(self):
        buzzwords = self.load_buzzwords()

        header = Header()
        footer = Footer()
        bingo_grid = BingoGrid(buzzwords, self.grid_columns, self.grid_rows)

        await self.mount(header)
        await self.mount(footer)
        await self.mount(bingo_grid)

def main():
    parser = argparse.ArgumentParser(description="Buzzword Bingo Spiel")
    parser.add_argument('--buzzword_file', required=True, help='Pfad zur Buzzword-Datei')
    parser.add_argument('--grid_columns', type=int, required=True, help='Anzahl der Spalten im Bingofeld')
    parser.add_argument('--grid_rows', type=int, required=True, help='Anzahl der Reihen im Bingofeld')
    parser.add_argument('--player_name', required=True, help='Name des Spielers')
    parser.add_argument('--num_players', type=int, default=1, help='Anzahl der Spieler')

    args = parser.parse_args()

    app = BingoApp(
        buzzword_file=args.buzzword_file,
        grid_columns=args.grid_columns,
        grid_rows=args.grid_rows,
        player_name=args.player_name,
        num_players=args.num_players
    )
    app.run()

if __name__ == "__main__":
    main()
