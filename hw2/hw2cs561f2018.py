import time
# from parser import Node, Parser

spla_leaf_nodes = {}
lahsa_leaf_nodes = {}
node_set = set()


class Node:
    def __init__(self, all_applicants, applicants_selected,
                 spla_blacklist, lahsa_blacklist, spla_capacity,
                 lahsa_capacity, depth, num_spla, num_lahsa, num_both,
                 move_taken, num_parking_spots, num_beds):

        self.all_applicants = all_applicants  # list of all applicants
        self.applicants_selected = applicants_selected  # list of indices
        self.spla_capacity = spla_capacity  # capacities for spla
        self.lahsa_capacity = lahsa_capacity  # capacities for lahsa
        self.num_spla = num_spla  # remaining number of spla_pool
        self.num_lahsa = num_lahsa  # remaining number of lahsa_pool
        self.num_both = num_both  # remaining number of both_pool
        self.depth = depth  # depth in the tree (used for turns)
        self.children = []  # list of child nodes
        self.move_taken = move_taken
        self.spla_score = None
        self.lahsa_score = None
        self.num_beds = num_beds
        self.num_parking_spots = num_parking_spots
        self.spla_blacklist = spla_blacklist
        self.lahsa_blacklist = lahsa_blacklist

        self.create_children()

    def __str__(self):
        return 'Children: {}, SPLA Cap: {}, LAHSA Cap: {}, num_spla: {}, num_lahsa: {}, num_both: {}, applicants_selected: {}, depth: {}, move: {}'.format(
                    self.children, self.spla_capacity, self.lahsa_capacity,
                    self.num_spla, self.num_lahsa, self.num_both,
                    self.applicants_selected, self.depth,
                    self.move_taken
                )

    def _create_hash_str(self, spla_capacity, lahsa_capacity,
                         applicants_selected, depth):
        return hash(str(spla_capacity) + str(lahsa_capacity)
                    + str(sorted(applicants_selected)) + str(depth))

    def _insert_applicant_into_spla(self, applicant):
        """ Tries to insert an applicant into SPLA capacities
            Returns a new capacities list if possible
            Returns none if not possible
        """
        new_capacities = [None] * 7
        for i in range(0, len(self.spla_capacity)):
            new_capacities[i] = self.spla_capacity[i]
            if applicant.days_needed[i] == '1':
                new_capacities[i] -= 1
            if new_capacities[i] < 0:
                return None
        return new_capacities

    def _insert_applicant_into_lahsa(self, applicant):
        """ Tries to insert an applicant into LAHSA capacities
            Returns a new capacities list if possible
            Returns none if not possible
        """
        new_capacities = [None] * 7
        for i in range(0, len(self.lahsa_capacity)):
            new_capacities[i] = self.lahsa_capacity[i]
            if applicant.days_needed[i] == '1':
                new_capacities[i] -= 1
            if new_capacities[i] < 0:
                return None
        return new_capacities

    def check_greedy_insert_spla(self):
        """
        Returns (True, first_applicant) and sets new capacities if greedy
        insertion works
        Else returns (False, None)
        """
        if len(self.all_applicants) - len(self.applicants_selected) - len(self.spla_blacklist) > 7 * self.num_parking_spots:
            return False, None

        tally = [0] * 7
        first_applicant = None
        # count up days across remaining applicants
        for i in range(0, len(self.all_applicants)):
            applicant = self.all_applicants[i]
            if applicant.is_spla and i not in self.applicants_selected:
                if first_applicant is None:
                    first_applicant = applicant
                for j in range(0, len(applicant.days_needed)):
                    if applicant.days_needed[j] == '1':
                        tally[j] += 1
                    if tally[j] > self.num_parking_spots:
                        return False, None

        # see if we can accommodate
        for i in range(0, len(self.spla_capacity)):
            if self.spla_capacity[i] - tally[i] < 0:
                return False, None

        # actually set the subtraction value if we can accommodate
        for i in range(0, len(self.spla_capacity)):
            self.spla_capacity[i] -= tally[i]

        return True, first_applicant

    def check_greedy_insert_lahsa(self):
        """
        Returns True, first_applicant and sets new capacities if greedy
        insertion works
        Else returns False, None
        """
        if len(self.all_applicants) - len(self.applicants_selected) - len(self.lahsa_blacklist) > 7 * self.num_beds:
            return False, None

        tally = [0] * 7
        first_applicant = None
        # count up days across remaining applicants
        for i in range(0, len(self.all_applicants)):
            applicant = self.all_applicants[i]
            if applicant.is_lahsa and i not in self.applicants_selected:
                if first_applicant is None:
                    first_applicant = applicant
                for j in range(0, len(applicant.days_needed)):
                    if applicant.days_needed[j] == '1':
                        tally[j] += 1
                    if tally[j] > self.num_beds:
                        return False, None

        # see if we can accommodate
        for i in range(0, len(self.lahsa_capacity)):
            if self.lahsa_capacity[i] - tally[i] < 0:
                return False, None

        # actually set the subtraction value if we can accommodate
        for i in range(0, len(self.lahsa_capacity)):
            self.lahsa_capacity[i] -= tally[i]

        return True, first_applicant

    def _insert_qualifying_into_spla(self):
        """ Insert the remaining qualifying SPLA applicants into SPLA """
        global spla_leaf_nodes

        can_insert_greedy, first_applicant = self.check_greedy_insert_spla()
        if can_insert_greedy is True:  # greedy worked
            if self.depth == 0:
                self.move_taken = first_applicant.applicant_id
        else:  # do recursive selection
            capacity_hash = str(self.spla_capacity)
            selected_hash = str(sorted(self.applicants_selected))

            if spla_leaf_nodes.get(capacity_hash) is None:
                spla_leaf_nodes[capacity_hash] = {}

            if spla_leaf_nodes.get(capacity_hash).get(selected_hash) is None:
                # compute leaf node for the first time
                answer = self._get_min_score(0, self._get_eligible_spla(),
                                             self.spla_capacity, [])
                spla_leaf_nodes[capacity_hash][selected_hash] = answer

            s = spla_leaf_nodes.get(capacity_hash).get(selected_hash)
            self.spla_score = s[0]
            if len(s[1]) > 0:
                self.move_taken = sorted(s[1])[0].applicant_id

    def _get_eligible_spla(self):
        """ Filters out selected applicants and lahsa applicants """
        a = []
        for i in range(0, len(self.all_applicants)):
            applicant = self.all_applicants[i]
            if i not in self.applicants_selected and i not in self.spla_blacklist and applicant.is_spla:
                a.append(applicant)
        return a

    def _get_eligible_lahsa(self):
        """ Filters out selected applicants and spla applicants """
        a = []
        for i in range(0, len(self.all_applicants)):
            applicant = self.all_applicants[i]
            if i not in self.applicants_selected and i not in self.lahsa_blacklist and applicant.is_lahsa:
                a.append(applicant)
        return a

    def _insert_qualifying_into_lahsa(self):
        """ Insert the reamining qualifying LAHSA applicants into LAHSA """
        global lahsa_leaf_nodes

        can_insert_greedy, _ = self.check_greedy_insert_lahsa()
        if can_insert_greedy is True:  # greedy worked
            return
        else:  # do recursive selection
            capacity_hash = str(self.lahsa_capacity)
            selected_hash = str(sorted(self.applicants_selected))

            if lahsa_leaf_nodes.get(capacity_hash) is None:
                lahsa_leaf_nodes[capacity_hash] = {}

            if lahsa_leaf_nodes.get(capacity_hash).get(selected_hash) is None:
                # compute leaf node for the first time
                answer = self._get_min_score(0, self._get_eligible_lahsa(),
                                             self.lahsa_capacity, [])
                lahsa_leaf_nodes[capacity_hash][selected_hash] = answer

            s = lahsa_leaf_nodes.get(capacity_hash).get(selected_hash)
            self.lahsa_score = s[0]
            if len(s[1]) > 0:
                self.move_taken = sorted(s[1])[0].applicant_id

    def _get_min_score(self, j, applicants,
                       curr_capacities, applicants_selected):
        """ Computes leaf node score when greedy placement fails """
        if curr_capacities is None:
            return float('inf'), applicants_selected
        if j >= len(applicants):
            return sum(curr_capacities), applicants_selected

        applicant = applicants[j]
        applicants_selected.append(applicant)
        without_applicant = [a for a in applicants_selected if a != applicant]

        curr_capacities_with_j = [None] * 7

        for i in range(0, len(curr_capacities)):
            curr_capacities_with_j[i] = curr_capacities[i]
            if applicant.days_needed[i] == '1':
                curr_capacities_with_j[i] -= 1
            if curr_capacities_with_j[i] < 0:
                curr_capacities_with_j = None
                break

        return min(
            self._get_min_score(j + 1,
                                applicants,
                                curr_capacities,
                                without_applicant
                                ),
            self._get_min_score(j + 1,
                                applicants,
                                curr_capacities_with_j,
                                applicants_selected
                                )
        )

    def create_children(self):
        if self.num_both <= 0:
            if sum(self.spla_capacity) > 0 and self.num_spla > 0:
                self._insert_qualifying_into_spla()
            if sum(self.lahsa_capacity) > 0 and self.num_lahsa > 0:
                self._insert_qualifying_into_lahsa()  # lahsa has space
            return

        if sum(self.spla_capacity) == 0:
            self._insert_qualifying_into_lahsa()
            return
        if sum(self.lahsa_capacity) == 0:
            self._insert_qualifying_into_spla()
            return

        # does not satisfy the base cases, keep building the tree
        self._create_children_driver()

    def _create_children_driver(self):
        global node_set
        spla_can_fit = False
        lahsa_can_fit = False
        new_spla_bl = None
        new_lahsa_bl = None
        for i in range(0, len(self.all_applicants)):
            if i in self.applicants_selected:  # already selected
                continue
            applicant = self.all_applicants[i]
            if self.depth % 2 == 0 and applicant.is_spla:  # spla or both
                if i in self.spla_blacklist:
                    continue
                new_capacities = self._insert_applicant_into_spla(applicant)
                if new_capacities is None:
                    new_spla_bl = list(self.spla_blacklist)
                    new_spla_bl.append(i)
                if new_capacities is not None:  # can place this person
                    spla_can_fit = True
                    new_selected = list(self.applicants_selected)
                    new_selected.append(i)
                    hash = self._create_hash_str(
                        spla_capacity=new_capacities,
                        lahsa_capacity=self.lahsa_capacity,
                        applicants_selected=new_selected,
                        depth=self.depth + 1
                    )
                    if hash not in node_set:
                        node_set.add(hash)
                        self.children.append(
                            Node(
                                all_applicants=self.all_applicants,
                                applicants_selected=new_selected,
                                spla_blacklist=(new_spla_bl
                                                or self.spla_blacklist),
                                lahsa_blacklist=self.lahsa_blacklist,
                                spla_capacity=new_capacities,
                                lahsa_capacity=self.lahsa_capacity,
                                num_spla=(self.num_spla - 1 if not
                                          applicant.is_lahsa
                                          else self.num_spla),
                                num_lahsa=self.num_lahsa,
                                num_both=(self.num_both - 1 if
                                          applicant.is_lahsa
                                          else self.num_both),
                                num_beds=self.num_beds,
                                num_parking_spots=self.num_parking_spots,
                                depth=self.depth + 1,
                                move_taken=applicant.applicant_id
                            )
                        )
            elif self.depth % 2 == 1 and applicant.is_lahsa:
                if i in self.lahsa_blacklist:
                    continue
                new_capacities = self._insert_applicant_into_lahsa(applicant)
                if new_capacities is None:
                    new_lahsa_bl = list(self.lahsa_blacklist)
                    new_lahsa_bl.append(i)
                if new_capacities is not None:
                    lahsa_can_fit = True
                    new_selected = list(self.applicants_selected)
                    new_selected.append(i)
                    hash = self._create_hash_str(
                        spla_capacity=self.spla_capacity,
                        lahsa_capacity=new_capacities,
                        applicants_selected=new_selected,
                        depth=self.depth + 1
                    )
                    if hash not in node_set:
                        node_set.add(hash)
                        self.children.append(
                            Node(
                                all_applicants=self.all_applicants,
                                applicants_selected=new_selected,
                                spla_blacklist=self.spla_capacity,
                                lahsa_blacklist=(new_lahsa_bl
                                                 or self.lahsa_blacklist),
                                spla_capacity=self.spla_capacity,
                                lahsa_capacity=new_capacities,
                                num_spla=self.num_spla,
                                num_lahsa=(self.num_lahsa - 1 if not
                                           applicant.is_spla
                                           else self.num_lahsa),
                                num_both=(self.num_both - 1 if
                                          applicant.is_spla
                                          else self.num_both),
                                num_beds=self.num_beds,
                                num_parking_spots=self.num_parking_spots,
                                depth=self.depth + 1,
                                move_taken=applicant.applicant_id
                            )
                        )
        if not spla_can_fit and self.depth % 2 == 0:
            self._insert_qualifying_into_lahsa()
        if not lahsa_can_fit and self.depth % 2 == 1:
            self._insert_qualifying_into_spla()


class Parser:
    def __init__(self, INPUT_FILE):
        lines = [line.rstrip('\n') for line in open(INPUT_FILE)]
        self.b = int(lines[0])  # number of beds LAHSA
        self.p = int(lines[1])  # number of parking spaces SPLA
        self.l = int(lines[2])
        self.s = int(lines[3 + self.l])

        self.a = int(lines[3 + self.l + 1 + self.s])

        # List of all applicants
        self.all_applicants = [Applicant(a) for a in
                               lines[(3 + self.l + 1 + self.s + 1):]]

        # List of Applicants that were preselected
        self._lahsa_preselected = self._get_applicants_by_ids(lines[3:
                                                              (3 + self.l)])
        self._spla_preselected = self._get_applicants_by_ids(lines[
                                                            (3 + self.l + 1):
                                                            (3 + self.l + 1 +
                                                             self.s)])
        # Removes preselected applicants from all_applicants, sorts list
        self._remove_preselected_applicants()
        self._remove_dummy_applicants()
        self._order_applicants()

        # Arrays of Capacities for each day, counting down
        self.lahsa_capacity = [self.b] * 7
        self.spla_capacity = [self.p] * 7

        # Accounts for preselected applicants, updating the capacities
        self._set_initial_capacities()

        # number of eligible candidates in both pools
        self.num_spla = 0
        self.num_lahsa = 0
        self.num_both = 0

        # sets the number of applicants in each pool
        self._set_pool_counts()

    def _order_applicants(self):
        """ Order by Days Needed (descending). Break ties by applicant ID """

        days_to_applicants = {}
        days_to_applicants_single = {}
        all_applicants = []

        for applicant in self.all_applicants:
            num_days = applicant.days_needed.count('1')
            if applicant.is_lahsa and applicant.is_spla:
                if num_days not in days_to_applicants:
                    days_to_applicants[num_days] = []
                days_to_applicants[num_days].append(applicant)
            else:
                if num_days not in days_to_applicants_single:
                    days_to_applicants_single[num_days] = []
                days_to_applicants_single[num_days].append(applicant)

        for i in range(0, 8)[::-1]:
            if i in days_to_applicants:
                applicants = days_to_applicants[i]
                all_applicants.extend(sorted(applicants))

        for i in range(0, 8)[::-1]:
            if i in days_to_applicants_single:
                applicants = days_to_applicants_single[i]
                all_applicants.extend(sorted(applicants))

        self.all_applicants = all_applicants

    def _remove_dummy_applicants(self):
        """ Remove applicants that dont qualify for either
            and dont request any days
        """
        new_applicants = []
        for applicant in self.all_applicants:
            if not applicant.is_lahsa and not applicant.is_spla:
                continue
            if '1' not in applicant.days_needed:
                continue
            new_applicants.append(applicant)
        new_applicants.sort()
        self.all_applicants = new_applicants

    def _remove_preselected_applicants(self):
        """ Removes preselected applicants from the list of all applicants """
        for applicant in self._lahsa_preselected:
            if applicant in self.all_applicants:
                self.all_applicants.remove(applicant)
        for applicant in self._spla_preselected:
            if applicant in self.all_applicants:
                self.all_applicants.remove(applicant)
        self.all_applicants.sort()

    def _set_initial_capacities(self):
        """ Updates the capicities for each day for the pre-selected
            applicants
        """
        for pick in self._lahsa_preselected:
            for i in range(0, len(pick.days_needed)):
                if pick.days_needed[i] == '1':
                    self.lahsa_capacity[i] -= 1
        for pick in self._spla_preselected:
            for i in range(0, len(pick.days_needed)):
                if pick.days_needed[i] == '1':
                    self.spla_capacity[i] -= 1

    def _get_applicants_by_ids(self, ids):
        """ Returns a list of Applicant objects given a list of ids """
        s = []
        for id in ids:
            for a in self.all_applicants:
                if a.applicant_id == id:
                    a.is_taken = True
                    s.append(a)
        return s

    def _set_pool_counts(self):
        """
        Sets the number of applicants in each pool
        """
        for applicant in self.all_applicants:
            if applicant.is_spla and not applicant.is_lahsa:
                self.num_spla += 1
            elif applicant.is_lahsa and not applicant.is_spla:
                self.num_lahsa += 1
            elif applicant.is_spla and applicant.is_lahsa:
                self.num_both += 1


class Applicant:
    def __init__(self, record_string):
        self.applicant_id = record_string[0:5]
        self.gender = record_string[5]
        self.age = int(record_string[6:9])
        self.has_pets = record_string[9] is 'Y'
        self.has_medical_conditions = record_string[10] is 'Y'
        self.has_car = record_string[11] is 'Y'
        self.has_license = record_string[12] is 'Y'
        self.days_needed = list(record_string[13:].rstrip())

        # Qualification Checks
        self.is_spla = (not self.has_medical_conditions
                        and self.has_car and self.has_license)
        self.is_lahsa = (self.gender is 'F' and self.age > 17
                         and not self.has_pets)

    def __str__(self):
        return 'Applicant ID: {}, \
        is_spla: {}, \
        is_lahsa: {} \
        days_needed: {}'.format(self.applicant_id, self.is_spla,
                                self.is_lahsa, self.days_needed)

    def __eq__(self, other):
        return (self.applicant_id == other.applicant_id)

    def __lt__(self, other):
        return self.applicant_id < other.applicant_id

    def __hash__(self):
        return hash(self.applicant_id)


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
    INPUT = 'grading_case/input3.txt'
    p = Parser(INPUT)

    start = time.time()

    print_initial_state(p)

    print_initial_state(p)
    root = Node(
            all_applicants=p.all_applicants,
            applicants_selected=[],
            spla_blacklist=[], lahsa_blacklist=[],
            spla_capacity=p.spla_capacity, lahsa_capacity=p.lahsa_capacity,
            num_spla=p.num_spla, num_lahsa=p.num_lahsa, num_both=p.num_both,
            depth=0, move_taken='', num_beds=p.b, num_parking_spots=p.p
            )

    solver = MultiAgentMinMax(root)
    answer = solver.run_minimax()

    with open('output.txt', 'w') as f:
        if isinstance(answer, tuple):
            f.write(str(answer[0]))
        else:
            f.write(answer)

    end = time.time()
    print('Time Elapsed: {}'.format(end - start))
    print('Answer: {}'.format(answer))
