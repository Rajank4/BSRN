import random
import argparse
from textual.app import App
from textual.widgets import Button, Header, Footer
from textual.containers import Grid, Vertical


class BingoGrid:
    def __init__(self, buzzwords, grid_columns, grid_rows):
        self.buzzwords = buzzwords
        self.grid_columns = grid_columns
        self.grid_rows = grid_rows
        self.selected = set()

    def create_grid(self):
        used_words = set()
        rows = []
        for _ in range(self.grid_rows):
            row_buttons = []
            for _ in range(self.grid_columns):
                while True:
                    word = random.choice(self.buzzwords)
                    if word not in used_words:
                        used_words.add(word)
                        break
                button = Button(label=word)
                button.on_click = lambda b=button: self.button_click(b)
                row_buttons.append(button)
            row = Grid(*row_buttons)
            rows.append(row)
        grid = Vertical(*rows)
        return grid

    def button_click(self, button):
        if button not in self.selected:
            button.add_class("selected")
            self.selected.add(button)
        else:
            button.remove_class("selected")
            self.selected.remove(button)


class BingoApp(App):
    CSS_PATH = ("styles.tcss")

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

    async def on_mount(self) -> None:
        buzzwords = self.load_buzzwords()

        header = Header()
        footer = Footer()
        bingo_grid = BingoGrid(buzzwords, self.grid_columns, self.grid_rows)
        grid = bingo_grid.create_grid()

        main_view = Vertical(
            header,
            grid,
            footer
        )

        await self.mount(main_view)


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