import Queue
from copy import deepcopy

from square import Square
from board import Board as BoardNode


def parse_file(INPUT):
    lines = [line.rstrip('\n') for line in open(INPUT)]
    N = int(lines[0])
    P = int(lines[1])
    S = int(lines[2])
    coordinates = []
    for line in lines[3:]:
        split = line.split(',')
        coordinates.append([int(split[0]), int(split[1])])
    return {
        "N": N,
        "P": P,
        "S": S,
        "C": coordinates
    }


def build_initial_board(coordinates):
    # only create squares for coordinates that scooters have visited
    board = {}
    for coordinate in coordinates:
        row = coordinate[1]
        col = coordinate[0]
        if row not in board:
            board[row] = {}

        if board[row].get(col) is None:
            board[row][col] = Square()
            board[row][col].value = 1
        else:
            board[row][col].value += 1
    return BoardNode(board=board)


def construct_graph(root, P):
    max = root.score
    q = Queue.Queue()
    q.put(root)
    q.put(None)  # marks the end of level 0
    while P > 0:
        curr_node = q.get()
        if curr_node is None:
            P -= 1
            q.put(None)
            # print('----' * 25)
            if q.queue[0] is None:  # two consecutive None markers
                break
            else:
                continue

        for i, col_dict in curr_node.board.items():
            for j in col_dict:
                if curr_node.board[i][j].valid:
                    child_node = BoardNode(
                                board=deepcopy(curr_node.board),
                                score=curr_node.score,
                                queen_coordinates=curr_node.queen_coordinates
                                )

                    # updates validity and score, sets queen coordinate
                    child_node.place_officer(i, j)

                    if child_node.score > max:
                        max = child_node.score

                    curr_node.add_child(child_node)
                    q.put(child_node)
    return root


def get_max_score(root, P):
    q = Queue.Queue()
    curr_max = root.score
    max_node = root
    q.put(root)
    while not q.empty():
        curr_node = q.get()
        if curr_node.score > curr_max:
            curr_max = curr_node.score
            max_node = curr_node
        for child in curr_node.children:
            q.put(child)
    print(max_node.queen_coordinates)
    return curr_max


def print_board(coordinates, N):
    board = []
    for i in range(0, N):
        board.append([0] * N)
    for coordinate in coordinates:
        row = coordinate[1]
        col = coordinate[0]
        board[row][col] += 1

    for row in board:
        print(row)


if __name__ == '__main__':
    INPUT = "input3.txt"
    inputs = parse_file(INPUT)
    N = inputs['N']
    P = inputs['P']
    S = inputs['S']
    coordinates = inputs['C']

    print('P: {}'.format(P))
    print_board(coordinates, N)
    print('\n')

    b = build_initial_board(coordinates)
    root = construct_graph(b, P)
    print("MAX: {}".format(get_max_score(root, P)))
