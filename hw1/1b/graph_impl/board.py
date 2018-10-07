class Board:
    def __init__(self, board, score=0, queen_coordinates=[]):
        self.score = score
        self.board = board  # N x N grid of Squares
        self.children = []  # list of Board objects
        self.queen_coordinates = list(set(queen_coordinates))

    def add_child(self, board_child):
        self.children.append(board_child)

    def place_officer(self, i, j):
        # updates score of board configuration and updates square validities
        self.score += self.board[i][j].value
        self.queen_coordinates.append((i, j))
        self.board[i][j].has_queen = True
        self.board[i][j].row = i
        self.board[i][j].col = j
        self.board[i][j].valid = False
        diag1 = i - j
        diag2 = i + j

        for row_number, col_dict in self.board.items():
            for col_number in col_dict:
                if row_number - col_number == diag1:
                    self.board[row_number][col_number].valid = False
                if row_number + col_number == diag2:
                    self.board[row_number][col_number].valid = False
                if row_number == i or col_number == j:
                    self.board[row_number][col_number].valid = False

    def print_board(self):
        for row in self.board:
            l = []
            for col_number, entry in self.board[row].items():
                l.append(entry.str())
            print(l)
