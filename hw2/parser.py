from applicant import Applicant


class Node:
    def __init__(self, all_applicants, applicants_selected, spla_capacity,
                 lahsa_capacity, depth, num_spla, num_lahsa, num_both,
                 move_taken):

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

        self.create_children()

    def __str__(self):
        return 'Children: {}, SPLA Cap: {}, LAHSA Cap: {}, num_spla: {}, num_lahsa: {}, num_both: {}, depth: {}, move: {}'.format(
                    self.children, self.spla_capacity, self.lahsa_capacity,
                    self.num_spla, self.num_lahsa, self.num_both, self.depth,
                    self.move_taken
                )

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

    def _insert_qualifying_into_spla(self):
        """ Insert the remaining qualifying SPLA applicants into SPLA """
        for i in range(0, len(self.all_applicants)):
            if i in self.applicants_selected:  # already selected this person
                continue
            applicant = self.all_applicants[i]
            if applicant.is_spla:  # spla or both
                new_cap = self._insert_applicant_into_spla(applicant)
                if new_cap is not None:
                    if applicant.is_lahsa:  # is both
                        self.num_both -= 1
                    else:
                        self.num_spla -= 1
                    self.spla_capacity = new_cap
                    self.applicants_selected.append(i)

    def _insert_qualifying_into_lahsa(self):
        """ Insert the reamining qualifying LAHSA applicants into LAHSA """
        for i in range(0, len(self.all_applicants)):
            if i in self.applicants_selected:  # already selected this person
                continue
            applicant = self.all_applicants[i]
            if applicant.is_lahsa:  # lahsa or both
                new_cap = self._insert_applicant_into_lahsa(applicant)
                if new_cap is not None:
                    if applicant.is_spla:
                        self.num_both -= 1
                    else:
                        self.num_lahsa -= 1
                    self.spla_capacity = new_cap
                    self.applicants_selected.append(i)

    def create_children(self):
        if self.num_both <= 0:
            if sum(self.spla_capacity) != 0:  # spla has space
                self._insert_qualifying_into_spla()
            if sum(self.lahsa_capacity) != 0:
                self._insert_qualifying_into_lahsa()  # lahsa has space
            return

        # spla ran out, append rest to lahsa
        elif sum(self.spla_capacity) <= 0 and self.num_both <= 0:
            self._insert_qualifying_into_lahsa()
            return

        # lahsa ran out, append rest to spla
        if sum(self.lahsa_capacity) <= 0 and self.num_both <= 0:
            self._insert_qualifying_into_spla()
            return

        # does not satisfy the base cases, keep building the tree
        self._create_children_driver()

    def _create_children_driver(self):
        can_place_something_spla = False
        can_place_something_lahsa = False

        for i in range(0, len(self.all_applicants)):
            if i in self.applicants_selected:  # already selected
                continue
            applicant = self.all_applicants[i]
            if self.depth % 2 == 0 and applicant.is_spla:  # spla or both
                new_capacities = self._insert_applicant_into_spla(applicant)
                if new_capacities is not None:  # can place this person
                    can_place_something_spla = True
                    new_selected = list(self.applicants_selected)
                    new_selected.append(i)
                    self.children.append(
                        Node(
                            all_applicants=self.all_applicants,
                            applicants_selected=new_selected,
                            spla_capacity=new_capacities,
                            lahsa_capacity=self.lahsa_capacity,
                            num_spla=(self.num_spla - 1 if not
                                      applicant.is_lahsa else self.num_spla),
                            num_lahsa=self.num_lahsa,
                            num_both=(self.num_both - 1 if
                                      applicant.is_lahsa else self.num_both),
                            depth=self.depth + 1,
                            move_taken=applicant.applicant_id
                        )
                    )
            elif self.depth % 2 == 1 and applicant.is_lahsa:
                new_capacities = self._insert_applicant_into_lahsa(applicant)
                if new_capacities is not None:
                    can_place_something_lahsa = True
                    new_selected = list(self.applicants_selected)
                    new_selected.append(i)
                    self.children.append(
                        Node(
                            all_applicants=self.all_applicants,
                            applicants_selected=new_selected,
                            spla_capacity=self.spla_capacity,
                            lahsa_capacity=new_capacities,
                            num_spla=self.num_spla,
                            num_lahsa=(self.num_lahsa - 1 if not
                                       applicant.is_spla else self.num_lahsa),
                            num_both=(self.num_both - 1 if
                                      applicant.is_spla else self.num_both),
                            depth=self.depth + 1,
                            move_taken=applicant.applicant_id
                        )
                    )
        # nothing fits into spla
        if not can_place_something_spla and self.depth % 2 == 0:
            self._insert_qualifying_into_lahsa()
        # nothing fits into lahsa
        elif not can_place_something_lahsa and self.depth % 2 == 1:
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
