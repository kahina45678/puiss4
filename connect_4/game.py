from abc import ABC
from multipledispatch import dispatch


class Player(ABC):
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color
        self.board = None

    def __eq__(self, value):
        return isinstance(value, Player) and self.name == value.name and self.color == value.color

    def __dict__(self):
        return {'name': self.name, 'color': self.color, 'instance': self.__class__.__name__}

    def __repr__(self):
        return f'name={self.name} color={self.color}'

    def drop_disc(self, slot: int) -> (int, int):
        disc = Disc(self.color, column=slot)
        y = self.board[slot].fill(disc)
        disc.row = y
        return disc


class AIAgent(Player):
    def __init__(self, color):
        super(AIAgent, self).__init__('AI', color)


class HumanAgent(Player):
    def __init__(self, name: str, color: str):
        super(HumanAgent, self).__init__(name, color)


class Disc:
    def __init__(self, color: str, row=None, column=None):
        self.color = color
        self.row = row
        self.column = column

    def __repr__(self):
        return f'{self.color}({self.row},{self.column})'


class Board:
    def __init__(self, max_slots: int, max_depth: int):
        self.max_slots = max_slots
        self.max_depth = max_depth
        self.slots = [Slot(max_depth) for _ in range(max_slots)]

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        i = self.index
        if i >= self.max_slots:
            raise StopIteration
        self.index += 1
        return self.slots[i]

    def __getitem__(self, item):
        return self.slots[item]

    def __len__(self):
        return self.max_slots

    def __repr__(self):
        return str(self.slots)


class Slot:
    def __init__(self, max_depth: int):
        self.max_depth = max_depth
        self.holes = [None for _ in range(max_depth)]

    def __len__(self):
        return len(list(filter(lambda x: x is not None, self.holes)))

    def __getitem__(self, item):
        return self.holes[item]

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        i = self.index
        if i >= self.__len__():
            raise StopIteration
        self.index += 1
        return self.holes[i]

    def __repr__(self):
        return str(self.holes)

    def fill(self, disc: Disc) -> int:
        if self.__len__() == self.max_depth:
            raise IndexError('The slot is full!')
        i = self.holes.index(None)
        # noinspection PyTypeChecker
        self.holes[i] = disc
        return i


class Game:
    def __init__(self, player1: Player, player2: Player, slots=7, depth=6):
        self.board = Board(slots, depth)
        if type(player1) == type(player2):
            self.mode = 'multi'
        elif isinstance(player1, AIAgent) and isinstance(player2, AIAgent):
            self.mode = 'ai_vs_ai'
        else:
            self.mode = 'single'
        player1.board = self.board
        player2.board = self.board
        self.players = (player1, player2)
        self.turn = 0

    def __dict__(self):
        return {
            'mode': self.mode,
            'players': [i.__dict__() for i in self.players],
            'turn': self.turn
        }

    @dispatch(int)
    def drop_disc(self, slot: int) -> Disc:
        disc = self.players[self.turn].drop_disc(slot)
        self.turn = self.turn ^ 1
        return disc

    @dispatch(list)
    def drop_disc(self, slots: list) -> list:
        disc = []
        for slot in slots:
            self.players[self.turn].drop_disc(slot)
            self.turn = ~self.turn
        return disc

    def win(self) -> Player | None:
        for p in self.players:
            if win(self.board, p.color,4):
                return p
        return None

    def draw(self) -> bool:
        return len(action_space(self.board)) == 0


from .ai.adversarial import win, action_space
