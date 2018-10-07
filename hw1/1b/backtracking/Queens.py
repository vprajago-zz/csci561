import itertools


class Queens:
    def __init__(self, N, P, S, coordinates):
        self.N = N
        self.P = P
        self.S = S
        self.coordinates = coordinates
        self.max_score = 0

        self._score = 0
        self._board = self._build_initial_board()
        self._row = []
        self._anti_diag = []
        self._diag = []
        self._col_sequences = list(itertools.combinations(range(N), P))

    def print_initial_board(self):
        for row in self._board:
            print(row)
        print('\n')

    def print_matrix(self, matrix):
        for row in matrix:
            print(row)

    def solve_queens(self):
        self._row = [False] * self.N
        self._anti_diag = [False] * (2 * self.N - 1)
        self._diag = [False] * (2 * self.N - 1)
        matrix = []

        for i in range(0, self.N):
            matrix.append(['.'] * self.N)

        # try every possible unique combination of columns (N choose P)
        # greatly narrows down the search space
        for col_seq in self._col_sequences:
            self._solve_queens_util(col_seq=col_seq, col_seq_index=0,
                                    matrix=matrix, remaining_queens=self.P)
        return self.max_score

    def _solve_queens_util(self, col_seq, col_seq_index,
                           matrix, remaining_queens):
        # Base Case 1: no more queens
        if remaining_queens == 0:
            if self.max_score < self._score:
                self.max_score = self._score
            return

        # Base Case 2: ran out of columns in the sequence
        if col_seq_index >= len(col_seq):
            return

        col_index = col_seq[col_seq_index]  # the current column we are placing
        for i in range(0, self.N):
            if self._is_valid(i, col_index):
                self._row[i] = True
                self._diag[i - col_index] = True
                self._anti_diag[i + col_index] = True
                matrix[i][col_index] = 'Q'
                self._score += self._board[i][col_index]

                self._solve_queens_util(col_seq=col_seq,
                                        col_seq_index=col_seq_index + 1,
                                        matrix=matrix,
                                        remaining_queens=remaining_queens - 1)

                # BACKTRACK
                matrix[i][col_index] = '.'
                self._row[i] = False
                self._diag[i - col_index] = False
                self._anti_diag[i + col_index] = False
                self._score -= self._board[i][col_index]

    def _build_initial_board(self):
        # N x N grid of values
        board = []
        for i in range(0, self.N):
            board.append([0] * self.N)

        for coordinate in self.coordinates:
            row = coordinate[0]
            col = coordinate[1]
            board[row][col] += 1
        return board

    def _is_valid(self, i, j):
        case_1 = self._row[i]
        case_2 = self._diag[i - j]
        case_3 = self._anti_diag[i + j]
        return not case_1 and not case_2 and not case_3
