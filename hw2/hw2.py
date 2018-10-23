import time

from parser import Node, Parser


class MultiAgentMinMax:
    def __init__(self, root):
        self.root = root

    def utility(self, state):
        """
        Returns tuple of scores: (spla, lahsa)
        """
        s, l = sum(state.spla_capacity), sum(state.lahsa_capacity)
        if not state.spla_score:
            state.spla_score = s
        else:
            s = state.spla_score
        if not state.lahsa_score:
            state.lahsa_score = l
        else:
            l = state.lahsa_score
        return s, l

    def lahsa_min_value(self, state):
        """ Find node with min lahsa value """
        v = float('inf'), float('inf')
        for child in state.children:
            v = min(v, self.minimax(child), key=lambda t: (t[1], -t[0]))
        state.spla_score = v[0]
        state.lahsa_score = v[1]

        return v

    def spla_min_value(self, state):
        """ Find node with min lahsa value """
        v = float('inf'), float('inf')
        for child in state.children:
            v = min(v, self.minimax(child))
        state.spla_score = v[0]
        state.lahsa_score = v[1]
        return v

    def minimax(self, state):
        if len(state.children) == 0:  # leaf node
            return self.utility(state)
        if state.depth % 2 == 0:  # spla -> min node for spla score
            return self.spla_min_value(state)
        elif state.depth % 2 == 1:  # lahsa -> min node for lahsa score
            return self.lahsa_min_value(state)

    def run_minimax(self):
        scores = self.minimax(self.root)
        if len(self.root.children) == 0:
            return self.root.move_taken
        best_moves = []
        for child in self.root.children:
            if child.spla_score == scores[0]:
                best_moves.append(child.move_taken)
        print('Best Moves: {}'.format(best_moves))
        return sorted(best_moves)[0], scores


def print_initial_state(p):
    print('All Applicants (Excluding preselected): ')
    for applicant in p.all_applicants:
        print(applicant)
    print('--' * 50)

    print('Existing SPLA Applicants')
    for a in p._spla_preselected:
        print(a)
    print('--' * 50)

    print('Existing LAHSA Applicants')
    for a in p._lahsa_preselected:
        print(a)
    print('--' * 50)

    print('SPLA Capacities')
    print(p.spla_capacity)
    print('--' * 50)

    print('LAHSA capicities')
    print(p.lahsa_capacity)
    print('--' * 50)

    print('num_spla: {}, num_lahsa: {}, num_both: {}'.format(p.num_spla,
                                                             p.num_lahsa,
                                                             p.num_both))
    print('--' * 50)


if __name__ == '__main__':
    INPUT = 'test/input0134.txt'
    p = Parser(INPUT)

    print_initial_state(p)
    start = time.time()
    root = Node(
            all_applicants=p.all_applicants,
            applicants_selected=[],
            spla_blacklist=[], lahsa_blacklist=[],
            spla_capacity=p.spla_capacity, lahsa_capacity=p.lahsa_capacity,
            num_spla=p.num_spla, num_lahsa=p.num_lahsa, num_both=p.num_both,
            depth=0, move_taken='', num_beds=p.b, num_parking_spots=p.p
            )
    end = time.time()

    print('Root: {}'.format(root))

    print('Tree Building Done: {}'.format(end - start))
    solver = MultiAgentMinMax(root)
    answer = solver.run_minimax()
    print('MultiAgentMinMax: {}'.format(answer))

    with open('output0.txt', 'w') as f:
        if len(answer) > 0:
            f.write(str(answer[0]))
        else:
            f.write("")
