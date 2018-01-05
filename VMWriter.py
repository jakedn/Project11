from os.path import basename


class VMWriter:

    SEGMENTS = {1: 'constant', 2: 'argument', 3: 'local', 4: 'static', 5: 'this', 6: 'that', 7: 'pointer', 8: 'temp'}
    ARITHMETIC = {'+': 'add', '-': 'sub', '~': 'neg', '=': 'eq', '>': 'gt', '<': 'lt', '&': 'and', '|': 'or', '!': 'not'}

    def __init__(self, file_path):
        """
        constructor
        :param file_path: file directory path
        """
        self.file_name = basename(file_path)[:-3]
        self.file = open(file_path[0:-3]+'.vm', "w")

    def write_push(self, segment, index):
        towrite = 'push ' + self.SEGMENTS[segment] + ' ' + str(index) + '\n'
        self.file.write(towrite)

    def write_pop(self, segment, index):
        towrite = 'pop ' + self.SEGMENTS[segment] + ' ' + str(index) + '\n'
        self.file.write(towrite)

    def write_arithmetic(self, command):
        towrite = self.ARITHMETIC[command] + '\n'
        self.file.write(towrite)

    def write_label(self, label):
        towrite = 'label ' + label + '\n'
        self.file.write(towrite)

    def write_goto(self, label):
        towrite = 'goto ' + label + '\n'
        self.file.write(towrite)

    def write_if(self, label):
        towrite = 'if-goto ' + label + '\n'
        self.file.write(towrite)

    def write_call(self, name, nargs):
        towrite = 'call ' + name + ' ' + str(nargs) + '\n'
        self.file.write(towrite)

    def write_function(self, name, nlocals):
        towrite = 'function ' + name + ' ' + str(nlocals) + '\n'
        self.file.write(towrite)

    def write_return(self):
        towrite = 'return\n'
        self.file.write(towrite)

    def close(self):
        self.file.close()