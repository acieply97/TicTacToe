from random import choice


class GameEngine():
    def __init__(self):
        self.symbol = 'x'
        self.board_state = ['' for _ in range(9)]

    def check_win(self):
        """
            Sprawdzenie czy na tablicy jest kombinacja wygrywająca partie, jeśli tak zwracany jest symbol gracza który wygrał
        """
        # Sprawdzenie możliwych kombinacji wygranej
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]

        for combination in winning_combinations:
            a, b, c = combination
            if self.board_state[a] == self.board_state[b] == self.board_state[c] != '':
                return self.board_state[a]  # Zwracamy symbol wygrywającego gracza

        if '' not in self.board_state:
            return False  # Remis, plansza zapełniona

    def switch_symbol(self):
        if self.symbol == 'x':
            self.symbol = 'o'
        else:
            self.symbol = 'x'

    def write_symbol_on_board(self, idx):
        if self.board_state[idx] == '':
            self.board_state[idx] = self.symbol
            self.check_win()
            self.switch_symbol()

    def clear_board_state(self):
        """
            Czyszczenie tablicy po skończonej grze
        """
        for _ in range(len(self.board_state)):
            self.board_state = ''
