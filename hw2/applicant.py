class Applicant:
    def __init__(self, record_string):
        self.applicant_id = record_string[0:5]
        self.gender = record_string[5]
        self.age = int(record_string[6:9])
        self.has_pets = record_string[9] is 'Y'
        self.has_medical_conditions = record_string[10] is 'Y'
        self.has_car = record_string[11] is 'Y'
        self.has_license = record_string[12] is 'Y'
        self.days_needed = list(record_string[13:])

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
