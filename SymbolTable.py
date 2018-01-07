CONST = 1
ARG = 2
LCL = 3
STATIC = 4
THIS = 5
THAT = 6
POINTER = 7
TEMP = 8

ADD = '+'
SUB = '-'
NEG = '~'
EQ = '='
GT = '>'
LT = '<'
AND = '&'
OR = '|'
NOT = '!'
DIVIDE = '/'
MULTIPLY = '*'

class SymbolTable:

    KIND = {'static': STATIC, 'field': THIS, 'VAR': LCL, 'argument': ARG}
    COUNTER = {'static': 0, 'field': 0}     #todo is this needed??
    def __init__(self):
        self.type = dict()
        self.kind = dict()
        self.number = dict()
        self.counter = {STATIC: 0, THIS: 0, LCL: 0, ARG: 0}

    def start_subroutine(self):
        """
        Resets dictionaries for a new subroutine
        """
        self.type = dict()
        self.kind = dict()
        self.number = dict()
        self.counter = {STATIC: 0, THIS: 0, LCL: 0, ARG: 0}

    def define(self, name, type, kind):
        self.type[name] = type
        self.kind[name] = self.KIND[kind]
        self.number[name] = self.counter[self.KIND[kind]]
        self.counter[self.KIND[kind]] += 1

    def var_count(self, kind):
        return self.counter[self.KIND[kind]]

    def kind_of(self, name):
        if name in self.kind.keys():
            return self.kind[name]
        return None

    def type_of(self, name):
        return self.type[name]

    def index_of(self, name):
        return self.number[name]