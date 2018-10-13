# General Notes
- both pick from the same applicant pool
- SPLA and LAHSA alternate choosing applicants one by one
- They must choose an applicant if there is still aa qualified one on the list
 (no passing)
- Efficiency is calculated by how many of the spaces are used during the week
  - a function of how many spots are occupied

# SPLA Requirements
- no medical conditions
- has car and drivers license

# LAHSA Requirements
- women only
- over 17 years old
- no pets

# Input Format
- first line: `b`, number of beds in the shelter (LAHSA)
- second line: `p`, the number of spaces in the parking lot (SPLA)
- third line: `l`: number of applicants chosen by LAHSA so far
- next `l` lines: applicant IDs
- next line: `s`, number of applicants chosen by SPLA so far
- next `s` lines: applicant IDs
- next line: `a`, total number of applicants
- next `a` lines: applicant information



## Questions
- For the end condition when one org runs out of choices – how does the other
organization choose the remaining qualifying applicants? What if it doesn't have
space to accommodate all of them?

- Are we keeping track of per day capacity or overall capacity?

- SPLA tries to maximize its Efficiency, but what is LAHSA trying to do?
If LAHSA is trying to maximize its own Efficiency as well, that doesn't
always translate to minimizing SPLA. This game is not 0-sum.

No matter how LAHSA picks, SPLA should pick the first move that will yield the greatest chance of
maximizing its Efficiency? There's no guarantee on SPLA getting the absolute max Efficiency since the game is not 0-sum

- End conditions:
  1. Both pool runs out OR (SPLA cannot accommodate anyone from both pool AND LAHSA cannot accommodate anyone from the both pool) – No shared resources
    - Append spla pool ppl to SPLA
    - Append lahsa pool ppl to LAHSA

  2. (SPLA pool runs out OR cannot accommodate anyone from SPLA pool) and (SPLA cannot accommodate anyone in the both pool) – No choices left for SPLA
    - Append qualified lahsa pool and both pool applicants to LAHSA

  3. (LAHSA pool runs out OR cannot accommodate anyone from LAHSA pool) and (LAHSA cannot accommodate anyone in the both pool) – No choices left for LAHSA
    - Append qualified spla pool and both pool applicants to spla

  4. SPLA has reached capacity ✅
    - Append remaining qualified to LAHSA

  5. LAHSA has reached capacity ✅
    - Append remaining to SPLA





# Exploring Other Ideas

1. The number of people I can select from the both_pool ranges from: 0 to both_pool
  - Suppose you select 0, but the game rules ENFORCE you take a person if they are an eligible choice
    - Then the select 0 case would never win – it would have a lower Efficiency rate pick 1 or pick 2 or ...
2. The max amount of people I can possibly select from spla_pool is : len(spla_pool)


subsets = []  <- contains all possible combinations of selections from the both_pool

for i in range(0, both_pool):
  both_pool_choose_i = list(itertools.combinations(both_pool_applicants, i))  # list of lists of all possible combinations of choosing i
  subsets.append(both_pool_choose_i)

score_to_selection = {}

for c_i in subsets:
  for combination in c_i:
    possible_applicants = spla_pool + combination  <- unselected spla applicants merged with a combination from the both pool
    score = get_best_selection_from_applicants(possible_applicants, 0, [10] * 7)


def get_best_selection_from_applicants(possible_applicants, i, curr_capacities):
  # TODO: THIS NEEDS TO RETURN THE LIST OF SELECTIONS
  """ Given list of candidates, return the maximum possible score (ideal selection) """

  - Base Cases:
    - i >= len(possible_applicants)
    - curr_capacities is invalid

  - max(picking the candidate, skipping the candidate)
  - max(
      get_max_score_from_applicants(possible_applicants, i + 1, curr_capacities=insert_candidate(possible_applicants, i)),
      get_max_score_from_applicants(possible_applicants, i + 1, curr_capacities=curr_capacities)
    )
