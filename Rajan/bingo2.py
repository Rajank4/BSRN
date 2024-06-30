import random
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Label, Footer, Button, Static, Header
import sys
import os
import time

print(100 * "\n" + "<......Bingo Game......>")

buzzword_Wörter = []

while True:
    spielname = input("Bitte geben Sie den Spielnamen ein, mit dem Sie sich verbinden wollen: ")
    spielname = spielname.replace("/", "").replace("\\", "")
    if os.path.exists(f"{spielname}.txt"):
        eingabe = input(
            f"Das Spiel {spielname} läuft bereits.\nSie werden dem Spiel {spielname} beitreten.\n\nBestätigen Sie mit Enter.\n'exit' wird den Prozess beenden. Jede andere Eingabe lässt Sie einen neuen Spielnamen eingeben.")
        if eingabe == "":
            with open(f"{spielname}.txt", 'r') as file:
                size = int(file.readline().strip())
                buzzword_Wörter = [zeile.strip() for zeile in file]
            break
        elif eingabe == "exit":
            sys.exit()
        else:
            continue
    else:
        eingabe = input(
            f"Das Spiel {spielname} existiert noch nicht.\nSie werden das Spiel {spielname} erstellen und hosten.\n\nBestätigen Sie mit Enter.\n'exit' wird den Prozess beenden. Jede andere Eingabe lässt Sie einen neuen Spielnamen eingeben.")
        if eingabe == "":
            while True:
                try:
                    size = int(input("Bitte gebe die Spielfeldgröße ein: "))
                    if size < 3 or size > 7:
                        print("Ungültige Größe: Erlaubt ist eine Größe von 3 - 7 und sie darf keine Dezimalzahl sein")
                    else:
                        break
                except ValueError:
                    continue
            while True:
                try:
                    eingabe = input(
                        "Möchtest du die standard Buzzwords-Datei verwenden, drücke Enter. Sonst gib den Pfad an.\nDiese Funktion steht nur zur Verfügung, wenn das Spiel direkt aus dem Ordner gestartet wird.")
                    if eingabe == "":
                        dateipfad = "buzzwords.txt"
                    else:
                        dateipfad = eingabe
                    buzzword_Wörter = []
                    with open(dateipfad, 'r') as file:
                        buzzword_Wörter = [zeile.strip() for zeile in file]
                    if len(buzzword_Wörter) < size * size:
                        print("Die Anzahl der Wörter in der Datei ist zu gering!")
                        continue
                    with open(f"{spielname}.txt", 'w') as file:
                        file.write(f"{size}\n")
                        for wort in buzzword_Wörter:
                            file.write(f"{wort}\n")
                    break
                except Exception:
                    print("Der Dateipfad ist ungültig!")
            break
        elif eingabe == "exit":
            sys.exit()
        else:
            continue


class Bingo(App):
    CSS_PATH = "styles.tcss"
    spielname = spielname
    size = size
    buzzword_Wörter = buzzword_Wörter
    button_status = {}
    SiegerProzess = False
    SpielVorbei = False

    def bingo_felder_erstellen(self, size):
        self.grid_container.remove_children()  # Entfernt das alte Grid

        self.button_name_Liste = []  # Liste zum Speichern der Wörter

        benutzte_wörter = []
        for y in range(size):
            for x in range(size):
                if size in {5, 7} and y == size // 2 and x == size // 2:
                    button_name = "Joker Feld"
                else:
                    while True:
                        button_name = random.choice(self.buzzword_Wörter)
                        if button_name not in benutzte_wörter:
                            benutzte_wörter.append(button_name)
                            break
                self.button_name_Liste.append(button_name)
                button_id = f"button_{y}_{x}"
                self.button_status[button_id] = False  # Initialer Status des Buttons ist False (nicht durchgestrichen)
                if size in {5, 7} and y == size // 2 and x == size // 2:
                    self.button_status[button_id] = True  # Joker Feld ist automatisch durchgestrichen
                    button = Button(button_name, id=button_id, classes="Joker")
                    button.disabled = True
                else:
                    button = Button(button_name, id=button_id, classes="bingo-button")
                self.grid_container.mount(button)

        self.grid_container.styles.grid_size_columns = size  # Formatiert in CSS
        self.grid_container.styles.grid_size_rows = size

    def überprüfe_bingo(self):
        # Horizontale Überprüfung
        for y in range(self.size):
            if all(self.button_status.get(f"button_{y}_{x}", False) for x in range(self.size)):
                self.bingo_confirm_button.add_class("bingoconf")  # Fügt die "bingoconf"-Klasse zum Button hinzu
                return True

        # Vertikale Überprüfung
        for x in range(self.size):
            if all(self.button_status.get(f"button_{y}_{x}", False) for y in range(self.size)):
                self.bingo_confirm_button.add_class("bingoconf")  # Fügt die "bingoconf"-Klasse zum Button hinzu
                return True

        # Diagonale Überprüfung (von links oben nach rechts unten)
        if all(self.button_status.get(f"button_{i}_{i}", False) for i in range(self.size)):
            self.bingo_confirm_button.add_class("bingoconf")  # Fügt die "bingoconf"-Klasse zum Button hinzu
            return True

        # Diagonale Überprüfung (von rechts oben nach links unten)
        if all(self.button_status.get(f"button_{i}_{self.size - 1 - i}", False) for i in range(self.size)):
            self.bingo_confirm_button.add_class("bingoconf")  # Fügt die "bingoconf"-Klasse zum Button hinzu
            return True

        self.bingo_confirm_button.remove_class("bingoconf")  # Entfernt die "bingoconf"-Klasse vom Button
        return False

    def compose(self):
        self.zufallswort_label = Label("", id="zufallswort_label")
        self.error_message = Label("", id="error_message")
        self.zufallswort_button = Button("Wort generieren", id="zufallswort")
        self.grid_container = Static(classes="bingo-grid")
        self.gewonnen_label = Label("", id="gewonnen_label")
        self.bingo_confirm_button = Button("Bingo bestätigen", id="bingo_confirm")
        self.quit_button = Button("Quit", id="quit", classes="quit-button")
        self.getWort = Label("", id="getWort")
        self.wortlisteTitel = Label("\nListe bisheriger Wörter:\n", id="wortlisteTitel", classes="wortlisteTitel")
        self.wortliste_label = Label("", id="wortliste_label")
        self.CheckBingo_label = Label("", id="CheckBingo_label")
        self.title = f"Spielname: {self.spielname} \t" + f"\tSpielerID: {os.getpid()}"

        yield Header("", id="header-ID", classes="header")
        yield self.error_message
        yield self.zufallswort_label
        yield self.zufallswort_button
        yield self.grid_container
        yield self.CheckBingo_label
        yield self.gewonnen_label
        yield self.bingo_confirm_button
        yield self.quit_button
        yield self.wortlisteTitel
        yield self.wortliste_label
        yield Footer()

    def on_mount(self):
        self.bingo_felder_erstellen(self.size)

    @on(Button.Pressed)
    def wort_streiche(self, event: Button.Pressed):
        buttonName = str(event.button.label)
        button_id = str(event.button.id)
        if button_id.startswith("button_"):
            if button_id in self.button_status:
                self.button_status[button_id] = not self.button_status[button_id]
                if self.button_status[button_id]:
                    event.button.add_class("strikethrough")
                else:
                    event.button.remove_class("strikethrough")
                if self.überprüfe_bingo():
                    self.update_gewonnen_label("")

    @on(Button.Pressed, "#zufallswort")
    def zufallswort_generieren(self):
        zufallswort = random.choice(self.buzzword_Wörter)
        self.zufallswort_label.update(zufallswort)

    @on(Button.Pressed, "#bingo_confirm")
    def on_bingo_confirm(self, event):
        if self.überprüfe_bingo():
            self.update_gewonnen_label("Bingo!")
            self.SiegerProzess = True
        else:
            self.update_gewonnen_label("Noch kein Bingo. Versuche es weiter!")

    @on(Button.Pressed, "#quit")
    def quit_game(self):
        self.exit("Quit")

    def update_gewonnen_label(self, text):
        self.gewonnen_label.update(text)


if __name__ == "__main__":
    Bingo().run()
