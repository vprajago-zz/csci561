import time

from parser import Node, Parser


class MultiAgentMinMax:
    def __init__(self, root):
        self.root = root

    def utility(self, state):
        """ Returns tuple of scores: (spla, lahsa) """
        s, l = sum(state.spla_capacity), sum(state.lahsa_capacity)
        state.spla_score = s
        state.lahsa_score = l
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
        best_moves = []
        for child in self.root.children:
            if child.spla_score == scores[0]:
                best_moves.append(child.move_taken)
        print('Best Moves: {}'.format(best_moves))
        return sorted(best_moves)[0], scores


class ExpectiminmaxSolver:
    def __init__(self, root):
        self.root = root

    def utility(self, state):
        """
        Returns the score(s) for a leaf node
        """
        s = sum(state.spla_capacity)
        print('Leaf Node: {}, Score: {}'.format(state, s))
        state.spla_score = s
        return s

    def min_value(self, state):
        print('Calculating Min Score: {}'.format(state))
        v = float('inf')
        for child in state.children:
            v = min(v, self.expectiminmax(child))
        print('Min Value Node: {}, Score: {}'.format(state, v))
        state.spla_score = v

        return v

    def expected_value(self, state):
        print('Calculating Chance Val: {}'.format(state))
        v = 0
        for child in state.children:
            pr = 1.0/len(state.children)  # each child is equally probable
            v += pr * self.expectiminmax(child)
        print('Chance Node: {}, Score: {}'.format(state, v))
        state.spla_score = v
        return v

    def run_expectiminmax(self):
        """
        Runs expectiminmax
        returns (best first move, score)
        """
        score = self.expectiminmax(self.root)
        best_moves = []
        for child in self.root.children:
            if child.spla_score == score:
                best_moves.append(child.move_taken)

        return sorted(best_moves)[0], score

    def expectiminmax(self, state):
        print('\nCurr Node: {}'.format(state))
        if len(state.children) == 0:  # leaf node
            return self.utility(state)
        if state.depth % 2 == 0:  # spla -> min node (good scores are small)
            return self.min_value(state)
        elif state.depth % 2 == 1:  # lahsa -> chance node (expected value)
            return self.expected_value(state)


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
    INPUT = 'input3.txt'
    p = Parser(INPUT)

    print_initial_state(p)

    start = time.time()

    root = Node(
            all_applicants=p.all_applicants,
            applicants_selected=[],
            spla_capacity=p.spla_capacity, lahsa_capacity=p.lahsa_capacity,
            num_spla=p.num_spla, num_lahsa=p.num_lahsa, num_both=p.num_both,
            depth=0, move_taken=''
            )
    end = time.time()

    print('Tree Building Done: {}'.format(end - start))

    solver = MultiAgentMinMax(root)
    print('MultiAgentMinMax: {}'.format(solver.run_minimax()))
