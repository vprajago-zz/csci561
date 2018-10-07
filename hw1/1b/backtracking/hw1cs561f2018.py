from Queens import Queens as QueenSolver


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


if __name__ == '__main__':
    INPUT = "input3.txt"
    inputs = parse_file(INPUT)
    N = inputs['N']
    P = inputs['P']
    S = inputs['S']
    coordinates = inputs['C']

    solver = QueenSolver(N=N, P=P, S=S, coordinates=coordinates)
    max_score = solver.solve_queens()

    with open('output.txt', 'w') as f:
        f.write(str(max_score))
