from connect_4.game import Board, Disc, AIAgent
import random
import copy


class AlphaBetaAgent(AIAgent):
    def __init__(self, color: str, min_color: str):
        super().__init__(color)
        self.min_color = min_color

    def drop_disc(self, slot: int):
        _, slot = AlphaBetaPruning(self.board,
                                   max_color=self.color,
                                   min_color=self.min_color,
                                   cut_off_depth=3).search()
        return super().drop_disc(slot)


def heuristic(board: Board, color: str) -> int:
    if win(board, color,4) or horz(board, color, 3, adjacent=2):
        return 1000
    return (
        horz(board, color, 3, adjacent=1) +
        vert(board, color, 3) +
        horz(board, color, 3, adjacent=0)
    ) * 90 + (
        vert(board, color, 2) +
        horz(board, color, 2, adjacent=2)
    ) * 5 + horz(board, color, 2, adjacent=1) * 3


def win(board: Board, color: str, n: int) -> bool:
    # Vertical connect
    for slot in board:
        count = 0
        for disc in slot:
            if disc and disc.color == color:
                count += 1
            else:
                count = 0
            if count >= n:
                return True

    # Horizontal connect
    for i in range(board.max_depth):
        count = 0
        for slot in board:
            if slot[i] and slot[i].color == color:
                count += 1
            else:
                count = 0
            if count >= n:
                return True

    # Diagonal connect
    for i in range(board.max_depth - 3):
        for j in range(len(board[0]) - 3):
            count = 0
            for k in range(4):
                if board[i + k][j + k] and board[i + k][j + k].color == color:
                    count += 1
                else:
                    count = 0
                if count >= n:
                    return True

    # Diagonal connect
    for i in range(board.max_depth - 3):
        for j in range(3, len(board[0])):
            count = 0
            for k in range(4):
                if board[i + k][j - k] and board[i + k][j - k].color == color:
                    count += 1
                else:
                    count = 0
                if count >= n:
                    return True

    return False


def vert(board: Board, color: str, n: int) -> int:
    sum_of_connects = 0
    # Vertical connect
    for slot in board:
        count = 0
        for disc in slot:
            if disc and disc.color == color:
                count += 1
            else:
                count = 0
        if count >= n and not slot[-1]:
            sum_of_connects += 1
    return sum_of_connects


def horz(board: Board, color: str, n: int, adjacent: int = 0) -> int:
    sum_of_connects = 0
    # Horizontal connect
    for i in range(board.max_depth):
        count = 0
        for slot in board:
            if slot[i] and slot[i].color == color:
                count += 1
            else:
                count = 0
            if count >= n:
                if not adjacent or (
                    i == 0 or not slot[i - 1] or slot[i - 1].color == color
                ) and (
                    i == board.max_depth - 1 or not slot[i + 1] or slot[i + 1].color == color
                ):
                    sum_of_connects += 1
    return sum_of_connects


def diagonal(board: Board, color: str, n: int, adjacent: int = 0) -> int:
    sum_of_connects = 0
    # Diagonal connect
    for i in range(board.max_depth - 3):
        for j in range(len(board[0]) - 3):
            count = 0
            for k in range(4):
                if board[i + k][j + k] and board[i + k][j + k].color == color:
                    count += 1
                else:
                    count = 0
                if count >= n:
                    if not adjacent or (
                        (i == 0 or j == 0) or
                        (not board[i - 1][j - 1] or board[i - 1][j - 1].color != color) and
                        (not board[i + 1][j + 1] or board[i + 1][j + 1].color != color)
                    ) and (
                        (i + k == board.max_depth - 1 or j + k == len(board[0]) - 1) or
                        (not board[i + k + 1][j + k + 1] or board[i + k + 1][j + k + 1].color != color) and
                        (not board[i + k - 3][j + k - 3] or board[i + k - 3][j + k - 3].color != color)
                    ):
                        sum_of_connects += 1

    # Diagonal connect
    for i in range(board.max_depth - 3):
        for j in range(3, len(board[0])):
            count = 0
            for k in range(4):
                if board[i + k][j - k] and board[i + k][j - k].color == color:
                    count += 1
                else:
                    count = 0
                if count >= n:
                    if not adjacent or (
                        (i == 0 or j == len(board[0]) - 1) or
                        (not board[i - 1][j + 1] or board[i - 1][j + 1].color != color) and
                        (not board[i + 1][j - 1] or board[i + 1][j - 1].color != color)
                    ) and (
                        (i + k == board.max_depth - 1 or j - k == 0) or
                        (not board[i + k + 1][j - k - 1] or board[i + k + 1][j - k - 1].color != color) and
                        (not board[i + k - 3][j - k + 3] or board[i + k - 3][j - k + 3].color != color)
                    ):
                        sum_of_connects += 1

    return sum_of_connects

def action_space(board: Board, shuffle: bool = True) -> list:
    action_space_list = []
    for i, slot in enumerate(board):
        if len(slot) < board.max_depth:
            action_space_list.append(i)
    if shuffle:
        random.shuffle(action_space_list)
    return action_space_list


# Applies actions to a state
def successors(board: Board, color: str, shuffle: bool = True) -> list:
    new_states = []
    for column in action_space(board, shuffle):
        board_copy = copy.deepcopy(board)
        i = board_copy[column].fill(Disc(color, column=column))
        board_copy[column][i].row = i
        new_states.append((board_copy, column))
    return new_states




class AlphaBetaPruning:
    def __init__(self, initial_state: Board, max_color: str, min_color: str, cut_off_depth=3):
        self.initial_state = initial_state
        self.cut_off_depth = cut_off_depth
        self.max_color = max_color
        self.min_color = min_color

    def search(self) -> (int, int):
        value, action = self.__max_value(self.initial_state, -1000000, 1000000, 0)
        return value, action

    def __max_value(self, state, alpha, beta, depth) -> (int, int):
        utility = self.__utility(state, depth)
        if utility is not None:
            return utility
        best_action = None
        default_action = None  # If the final returning action is None, this default action will be replaced
        for successor, action in successors(state, self.max_color):
            default_action = action if default_action is None else default_action
            value, _ = self.__min_value(successor, alpha, beta, depth + 1)
            if value > alpha:
                alpha = value
                best_action = action
            if alpha >= beta:
                # Pruning
                return alpha, best_action
        return alpha, default_action if best_action is None else best_action

    def __min_value(self, state, alpha, beta, depth) -> (int, int):
        utility = self.__utility(state, depth)
        if utility is not None:
            return utility
        best_action = None
        default_action = None  # If the final returning action is None, this default action will be replaced
        for successor, action in successors(state, self.min_color):
            default_action = action if default_action is None else default_action
            value, _ = self.__max_value(successor, alpha, beta, depth + 1)
            if value < beta:
                beta = value
                best_action = action
            if alpha >= beta:
                # Pruning
                return beta, best_action
        return beta, default_action if best_action is None else best_action

    def __utility(self, state, depth) -> (int, int):
        if depth >= self.cut_off_depth:
            return heuristic(state, self.max_color) - heuristic(state, self.min_color), None
        if win(state, self.max_color,4):
            return 100000000, None
        if win(state, self.min_color,4):
            return -1 * 100000000, None
        return None



