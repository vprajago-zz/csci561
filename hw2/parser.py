from applicant import Applicant

spla_leaf_nodes = {}
lahsa_leaf_nodes = {}
node_to_children = {}


class Node:
    def __init__(self, all_applicants, applicants_selected,
                 spla_blacklist, lahsa_blacklist, spla_capacity,
                 lahsa_capacity, depth, num_spla, num_lahsa, num_both,
                 move_taken, num_parking_spots, num_beds,
                 will_create_children=True):

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

        if will_create_children:
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
        return (str(spla_capacity) + str(lahsa_capacity) + str(sorted(applicants_selected)) + str(depth))

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
                                             self.spla_capacity, set())
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
                                             self.lahsa_capacity, set())
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
        applicants_selected.add(applicant)
        without_applicant = {a for a in applicants_selected if a != applicant}

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
        global node_to_children
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
                    # The following nodes have the same children
                    # SPLA 1, LAHSA 2, SPLA 3 ....
                    # SPLA 3, LAHSA 2, SPLA 1 ....
                    if hash not in node_to_children:
                        node = Node(
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
                        self.children.append(node)
                        node_to_children[hash] = node.children

                    # seen a node like this before, dont create children
                    else:
                        # create the node (without children)
                        node = Node(
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
                            move_taken=applicant.applicant_id,
                            will_create_children=False
                        )
                        # set children
                        node.children = list(node_to_children[hash])
                        # append node to current node's children
                        self.children.append(node)

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
                    if hash not in node_to_children:
                        node = Node(
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
                        node_to_children[hash] = node.children
                        self.children.append(node)
                    else:
                        node = Node(
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
                            move_taken=applicant.applicant_id,
                            will_create_children=False
                        )
                        node.children = list(node_to_children[hash])
                        self.children.append(node)

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
