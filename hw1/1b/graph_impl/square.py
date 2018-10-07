class Square:
    def __init__(self):
        self.value = 0
        self.valid = True
        self.has_queen = False
        self.row = None
        self.col = None

    def str(self):
        return '(value: {}, valid: {}, queen: {})'.format(self.value, self.valid, self.has_queen)
