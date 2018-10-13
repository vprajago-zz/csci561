# def _try_capacities_insert(self, applicant, is_spla_capacities):
#     """ Returns new capacity list if possible to insert
#         Returns None if not possible
#         is_spla_capacities: switch for picking the capacities list
#     """
#
#     # knows which capacity to insert into depending on depth
#     cap = deepcopy(self.spla_capacity) if is_spla_capacities \
#         else deepcopy(self.lahsa_capacity)
#
#     for i in range(0, len(cap)):
#         if applicant.days_needed[i] == '1':
#             cap[i] -= 1
#         if cap[i] < 0:
#             return None
#     return cap
#
# def _insert_remaining_applicants(self, is_spla_capacities):
#     """
#     Inserts the remaining applicants into the given accommodation
#     is_spla_capacities: switch for picking the capacities list
#     """
#     for applicant in self.all_applicants:
#         new_capacities = self._try_capacities_insert(applicant,
#                                                      is_spla_capacities)
#         # we can accommodate this applicant
#         if new_capacities is not None:
#             if is_spla_capacities:
#                 self.spla_capacity = new_capacities
#             else:
#                 self.lahsa_capacity = new_capacities
#
# def _check_both_pool(self):
#     """
#     - Returns true if both pool is not empty AND spla or lahsa can
#     accommodate at least one person in the both pool
#     - Else returns false
#     """
#     if self.num_both <= 0:
#         return False
#
#     for applicant in self.all_applicants:
#         if applicant.is_spla and applicant.is_lahsa:
#             try_spla = self._try_capacities_insert(applicant, True)
#             try_lahsa = self._try_capacities_insert(applicant, False)
#             # this applicant can be inserted in one or the other
#             if try_spla is not None or try_lahsa is not None:
#                 return True
#     return False
#
#
# def create_children(self):
#     """ Checks for end game condition and initiates normal condition """
#
#     # 1. No more applicants left at all
#     if self.num_spla == 0 and self.num_lahsa == 0 and self.num_both == 0:
#         return
#
#     # 2. SPLA has reached capacity, insert remaining into LAHSA
#     elif sum(self.spla_capacity) == 0:
#         self._insert_remaining_applicants(False)
#
#     # 3. LAHSA has reached capacity, insert remaining into SPLA
#     elif sum(self.lahsa_capacity) == 0:
#         self._insert_remaining_applicants(True)
#
#     # 4. Both pool runs out OR (SPLA cannot accommodate anyone from
#     # both pool AND LAHSA cannot accommodate anyone from the both pool)
#     if not self._check_both_pool():
#         if self.num_spla > 0:
#             # append remaining spla
#             self._insert_remaining_applicants(True)
#             pass
#         if self.num_lahsa > 0:
#             # append remaining to lahsa
#             self._insert_remaining_applicants(False)
#         return
#
#     # Normal Case: spla and lahsa have options, either through their
#     # individual pools or through the both pool
#     self._create_children_driver()
#
# def _create_children_driver(self):
#     for i in range(0, len(self.all_applicants)):
#         applicant = self.all_applicants[i]
#
#         if self.depth % 2 == 0 and applicant.is_spla:
#             new_capacities = self._try_capacities_insert(applicant, True)
#             if new_capacities is not None:  # we are able to accomodate
#                 if applicant.is_lahsa:  # applicant is in the both pool
#                     self.num_both -= 1
#                 else:  # applicant is only in spla_pool
#                     self.num_spla -= 1
#
#                 self.children.append(
#                     Node(
#                         all_applicants=deepcopy(
#                             self.all_applicants.remove(applicant)
#                             ),
#                         spla_capacity=new_capacities,
#                         lahsa_capacity=deepcopy(self.lahsa_capacity),
#                         depth=self.depth + 1,
#                         num_spla=self.num_spla,
#                         num_lahsa=self.num_lahsa,
#                         num_both=self.num_both
#                     )
#                 )
#
#         elif self.depth % 2 != 0 and applicant.is_lahsa:
#             new_capacities = self._try_capacities_insert(applicant,False)
#             if new_capacities is not None:
#                 if applicant.is_spla:  # applicant is in both pool
#                     self.num_both -= 1
#                 else:  # applicant is only in lahsa_pool
#                     self.num_lahsa -= 1
#
#                 self.children.append(
#                     Node(
#                         all_applicants=deepcopy(
#                             self.all_applicants.remove(applicant)
#                             ),
#                         spla_capacity=deepcopy(self.spla_capacity),
#                         lahsa_capacity=new_capacities,
#                         depth=self.depth + 1,
#                         num_spla=self.num_spla,
#                         num_lahsa=self.num_lahsa,
#                         num_both=self.num_both
#                     )
#                 )
