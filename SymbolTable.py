class SymbolTable:

    KIND = {'static': 'static', 'field': 'field', 'VAR': 'local', 'argument': 'argument'}
    COUNTER = {'static': 0, 'field': 0}
    def __init__(self):
        self.type = dict()
        self.kind = dict()
        self.number = dict()
        self.counter = {'static': 0, 'field': 0, 'local': 0, 'argument': 0}

    def start_subroutine(self):
        """
        Resets dictionaries for a new subroutine
        """
        self.type = dict()
        self.kind = dict()
        self.number = dict()
        self.counter = {'static': 0, 'field': 0, 'local': 0, 'argument': 0}

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