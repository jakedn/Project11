########################################################
# CompilationEngine Class
# nand project 10
#
########################################################

from SymbolTable import *
from VMWriter import *

BINOP = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
def addspaces(n):
    str = ''
    for i in range(n):
        str += ' '
    return str


class CompilationEngine:
    CONST = 1
    ARG = 2
    LOCAL = 3
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
    SUBROUTINE_SCOPE = ['STATIC', 'FIELD']
    CLASS_SCOPE = ['ARG', 'VAR']

    def __init__(self, tokens, file_path):
        self.tokens = tokens
        self.class_symboltable = SymbolTable()
        self.subroutine_symboltable = SymbolTable()
        self.cur_class = None
        self.cur_subroutine_type = None # for the compile return function
        self.vmwriter = VMWriter(file_path)
        self.labelcounter = 0

    def compileclass(self, tokens):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or not first.value == 'class':
            return None, None
        # adds class name
        self.cur_class = str(tokens.pop(0))
        # pops '{'
        tokens.pop(0)
        done = False
        while not done:
            done = True
            newout, newtokens = self.compileclassvar(tokens[:])
            if newout is not None:
                done = False
                tokens = newtokens
        done = False
        while not done:
            done = True
            newout, newtokens = self.compilesubroutine(tokens[:])
            if newout is not None:
                done = False
                tokens = newtokens
        # pops '}'
        tokens.pop(0)
        self.cur_class = None
        return 0, tokens[:]

    def compileclassvar(self, tokens):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or not (first.value == 'static' or first.value == 'field'):
            return None, None
        # type
        type = str(tokens.pop(0))
        # name
        name = str(tokens.pop(0))
        self.class_symboltable.define(name, type, first)
        while tokens[0].value == ',':
            # pops ','
            tokens.pop(0)
            # name
            name =  str(tokens.pop(0))
            self.class_symboltable.define(name, type, first)
        # pops ';'
        tokens.pop(0)
        return 0, tokens[:]

    def compilesubroutine(self, tokens):
        # TODO: make sure correctness
        first = tokens.pop(0)
        if not (first.isa('KEYWORD') and first.value in 'constructor'
                                                        'function'
                                                        'method'):
            return None, None
        # initializes symbol table
        self.subroutine_symboltable.start_subroutine()
        # adds void|type
        type_func = str(tokens.pop(0))
        self.cur_subroutine_type = type_func
        # adds subroutine name
        name_func = str(tokens.pop(0))
        paraout, tokens = self.compileparameterlist(tokens[:])
        # pops '{'
        tokens.pop(0)
        done = False
        numlocals = 0
        while not done:
            done = True
            newout, newtokens = self.compilevardec(tokens[:])
            if newout is not None:
                done = False
                tokens = newtokens
                numlocals += newout
        self.vmwriter.write_function(self.cur_class + '.' + name_func, numlocals)
        if first.value == 'constructor':
            push_index = self.class_symboltable.var_count('field')
            # push constant num_fields
            self.vmwriter.write_push(self.CONST, push_index)
            self.vmwriter.write_call('Memory.alloc', 1)
            self.vmwriter.write_pop(self.POINTER, 0)
        elif first.value == 'method':
            self.subroutine_symboltable.define('this', self.cur_class, 'argument')
            self.vmwriter.write_push(self.ARG, 0)
            self.vmwriter.write_pop(self.POINTER, 0)
        newout, newtokens = self.compilestatements(tokens[:])
        if newout is not None:
            tokens = newtokens
        # pops '}'
        tokens.pop(0)
        self.cur_subroutine_type = None
        return 0, tokens[:]

    def compileparameterlist(self, tokens):
        first = tokens.pop(0)
        # first token is '('
        if tokens[0].value != ')':
            # adds type
            type_param = str(tokens.pop(0))
            # adds varName
            name_param = str(tokens.pop(0))
            self.subroutine_symboltable.define(name_param, type_param, 'argument')
        while tokens[0].value == ',':
            # pops ','
            tokens.pop(0)
            # adds type
            type_param = str(tokens.pop(0))
            # adds varName
            name_param = str(tokens.pop(0))
            self.subroutine_symboltable.define(name_param, type_param, 'argument')
        # popping the ')'
        tokens.pop(0)
        return 0, tokens[:]

    def compilevardec(self, tokens):
        first = tokens.pop(0)
        if not (first.isa('KEYWORD') and first.value == 'var'):
            return None, None
        # adds type
        vartype = tokens.pop(0)
        # adds name
        varname = str(tokens.pop(0))
        varcount = 1
        self.subroutine_symboltable.define(varname, vartype, 'VAR')
        while tokens[0].value == ',':
            # pops ','
            tokens.pop(0)
            # adds name
            varname = str(tokens.pop(0))
            varcount += 1
            self.subroutine_symboltable.define(varname, vartype, 'VAR')
        # pops ';'
        tokens.pop(0)
        return varcount, tokens[:]

    def compilestatements(self, tokens):
        done = False
        while not done:
            done = True
            for func in self.getstatements():
                newout, newtokens = func(tokens[:])
                if newout is not None:
                    done = False
                    tokens = newtokens
        return 0, tokens[:]

    def compiledo(self, tokens):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'do':
            return None, None
        if tokens[1].value != '.' or not tokens[1].isa('SYMBOL'):
            # pops name
            name = tokens.pop(0)
            out_explist, tokens = self.compileexpressionlist(tokens[:])
            self.vmwriter.write_call(self.cur_class + '.' + name, out_explist)
        else:
            # pops name
            name = str(tokens.pop(0))
            # pops '.'
            tokens.pop(0)
            # pops subname
            subname = str(tokens.pop(0))
            out_explist, tokens = self.compileexpressionlist(tokens[:])
            self.vmwriter.write_call(name + '.' + subname, out_explist)
        self.vmwriter.write_pop(self.TEMP, 0)
        # pops ';'
        tokens.pop(0)
        return 0, tokens[:]

    def compilelet(self, tokens):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'let':
            return None, None
        # checks if varName[expression] or varName
        if tokens[1].value == '[':
            # adds varName
            varname = str(tokens.pop(0))
            varkind = self.subroutine_symboltable.kind_of(varname)
            if varkind is None:
                varkind = self.class_symboltable.kind_of(varname)
                varindex = self.class_symboltable.index_of(varname)
            else:
                varindex = self.subroutine_symboltable.index_of(varname)
            self.vmwriter.write_push(varkind, varindex)
            # adds '['
            tokens.pop(0)
            outcomp, tokens = self.compileexpression(tokens[:])  # pushes something
            # adds ']'
            tokens.pop(0)
            self.vmwriter.write_arithmetic(self.ADD)
            # pops '='
            tokens.pop(0)
            out_expr, tokens = self.compileexpression(tokens[:])  # pushes something
            self.vmwriter.write_pop(self.TEMP, 0)
            self.vmwriter.write_pop(self.POINTER, 1)
            self.vmwriter.write_push(self.TEMP, 0)
            self.vmwriter.write_pop(self.THAT, 0)
        else:
            # adds varName
            varname = str(tokens.pop(0))
            varkind = self.subroutine_symboltable.kind_of(varname)
            if varkind is None:
                varkind = self.class_symboltable.kind_of(varname)
                varindex = self.class_symboltable.index_of(varname)
            else:
                varindex = self.subroutine_symboltable.index_of(varname)
            # pops '='
            tokens.pop(0)
            out_expr, tokens = self.compileexpression(tokens[:])  # pushes something
            self.vmwriter.write_pop(varkind, varindex)
        # pops ';'
        tokens.pop(0)
        return 0, tokens[:]

    def compilewhile(self, tokens, numspaces):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'while':
            return None, None
        self.vmwriter.write_label('L' + str(self.labelcounter))
        # pops '('
        tokens.pop(0)
        outputexp, tokens = self.compileexpression(tokens[:], numspaces + 1)
        # adds ')'
        tokens.pop(0)
        self.vmwriter.write_arithmetic(self.NOT)
        self.vmwriter.write_if('L' + str(self.labelcounter + 1))
        # pops '{'
        tokens.pop(0)
        # adds statements
        out_statements, tokens = self.compilestatements(tokens[:], numspaces + 1)
        self.vmwriter.write_goto('L' + str(self.labelcounter))
        # pops '}'
        tokens.pop(0)
        self.labelcounter += 2
        return 0, tokens[:]

    def compilereturn(self, tokens, numspaces):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'return':
            return None, None
        if tokens[0].value != ';':
            output_exp, tokens = self.compileexpression(tokens[:], numspaces + 1)
        # pops ';'
        tokens.pop(0)
        if self.cur_subroutine_type == 'void':
            self.vmwriter.write_push(self.CONST, 0)
        self.vmwriter.write_return()
        return 0, tokens[:]


    def compileif(self, tokens):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'if':
            return None, None
        # pops '('
        tokens.pop(0)
        outputexp, tokens = self.compileexpression(tokens[:])
        # pops ')'
        tokens.pop(0)
        self.vmwriter.write_if('L' + str(self.labelcounter))
        # pops '{'
        tokens.pop(0)
        # adds statements
        out_statements, tokens = self.compilestatements(tokens[:])
        # pops '}'
        tokens.pop(0)
        self.vmwriter.write_goto('L' + str(self.labelcounter + 1))
        self.vmwriter.write_label('L' + str(self.labelcounter))
        if tokens[0].isa('KEYWORD') and tokens[0].value == 'else':
            # pops 'else'
            tokens.pop(0)
            # pops '{'
            tokens.pop(0)
            # adds statements
            out_statements, tokens = self.compilestatements(tokens[:])
            # pops '}'
            tokens.pop(0)
        self.vmwriter.write_label('L' + str(self.labelcounter + 1))
        self.labelcounter += 2
        return 0, tokens[:]

    def compileexpression(self, tokens):
        term_out, tokens = self.compileterm(tokens[:])
        done = False
        while not done:
            done = True
            if tokens[0].value in BINOP:
                done = False
                # adds the BINOP
                binop = str(tokens.pop(0))
                # adds term
                term_output, tokens = self.compileterm(tokens[:])
                if binop == '*':
                    self.vmwriter.write_call('Math.multiply', 2)
                elif binop == '/':
                    self.vmwriter.write_call('Math.divide', 2)
                else:
                    self.vmwriter.write_arithmetic(binop)
        return 0, tokens[:]


    def compileterm(self, tokens):
        # if the term is varName[expression]
        if tokens[1].value == '[':
            # pops varName
            varname = str(tokens.pop(0))
            varkind = self.subroutine_symboltable.kind_of(varname)
            if varkind is None:
                varkind = self.class_symboltable.kind_of(varname)
                varindex = self.class_symboltable.index_of(varname)
            else:
                varindex = self.subroutine_symboltable.index_of(varname)
            self.vmwriter.write_push(varkind, varindex)
            # pops '['
            tokens.pop(0)
            expression_output, tokens = self.compileexpression(tokens[:]) # pushes something
            # pops ']'
            tokens.pop(0)
            self.vmwriter.write_arithmetic(self.ADD)
            self.vmwriter.write_pop(self.POINTER, 1)
            self.vmwriter.write_push(self.THAT, 0)
        # if the term is subroutineName(expressionList)
        elif tokens[1].value == '(' and tokens[0].isa('IDENTIFIER'):
            # pops name
            name = tokens.pop(0)
            out_explist, tokens = self.compileexpressionlist(tokens[:])
            self.vmwriter.write_call(self.cur_class + '.' + name, out_explist)
        # if the term is (className|varName).subroutineName(expressionList)
        elif tokens[1].value == '.':
            # pops name
            name = str(tokens.pop(0))
            # pops '.'
            tokens.pop(0)
            # pops subname
            subname = str(tokens.pop(0))
            out_explist, tokens = self.compileexpressionlist(tokens[:])
            self.vmwriter.write_call(name + '.' + subname, out_explist)
        # unary operator
        elif tokens[0].value == '~' or tokens[0].value == '-':
            # adds op
            operator = str(tokens.pop(0))
            output_term, tokens = self.compileterm(tokens[:])  # pushes something
            if operator == '~':
                self.vmwriter.write_arithmetic(self.NOT)
            elif operator == '-':
                self.vmwriter.write_arithmetic(self.NEG)
        # (expression)
        elif tokens[0].value == '(':
            # pops '('
            tokens.pop(0)
            output_expression, tokens = self.compileexpression(tokens[:])
            # pops ')'
            tokens.pop(0)
        # includes integerConstant, stringConstant, keywordConstant, varName
        else:
            constant_token = tokens.pop(0)
            if constant_token.isa('STR_CONST'):
                string_const = constant_token.value
                self.vmwriter.write_call('String.new(' + str(len(string_const)) + ')', 1)
                for ch in string_const:
                    if ch == '\n':
                        self.vmwriter.write_push(self.CONST, ord('\\'))
                        self.vmwriter.write_call('String.appendChar', 2)
                        self.vmwriter.write_push(self.CONST,ord('n'))
                        self.vmwriter.write_call('String.appendChar', 2)
                    elif ch == '\t':
                        self.vmwriter.write_push(self.CONST, ord('\\'))
                        self.vmwriter.write_call('String.appendChar', 2)
                        self.vmwriter.write_push(self.CONST, ord('t'))
                        self.vmwriter.write_call('String.appendChar', 2)
                    elif ch == '\r':
                        self.vmwriter.write_push(self.CONST, ord('\\'))
                        self.vmwriter.write_call('String.appendChar', 2)
                        self.vmwriter.write_push(self.CONST, ord('r'))
                        self.vmwriter.write_call('String.appendChar', 2)
                    elif ch == '\b':
                        self.vmwriter.write_push(self.CONST, ord('\\'))
                        self.vmwriter.write_call('String.appendChar', 2)
                        self.vmwriter.write_push(self.CONST, ord('b'))
                        self.vmwriter.write_call('String.appendChar', 2)
                    else:
                        self.vmwriter.write_push(self.CONST, ord(ch))
                        self.vmwriter.write_call('String.appendChar', 2)
            elif constant_token.isa('INT_CONST'):
                self.vmwriter.write_push(self.CONST, constant_token.value)
            # var name
            elif constant_token.isa('IDENTIFIER'):
                varname = constant_token.value
                varkind = self.subroutine_symboltable.kind_of(varname)
                if varkind is None:
                    varkind = self.class_symboltable.kind_of(varname)
                    varindex = self.class_symboltable.index_of(varname)
                varindex = self.subroutine_symboltable.index_of(varname)
                self.vmwriter.write_push(varkind, varindex)
            elif constant_token.isa('KEYWORD'):
                keyword = constant_token.value
                if keyword == 'true':
                    self.vmwriter.write_push(self.CONST, 0)
                    self.vmwriter.write_arithmetic(self.NOT)
                elif keyword == 'false' or keyword == 'null':
                    self.vmwriter.write_push(self.CONST, 0)
                elif keyword == 'this':
                    self.vmwriter.write_push('argument', 0)  # TODO: make sure correctness


        return 0, tokens[:]

    def compileexpressionlist(self, tokens):
        # pops '('
        tokens.pop(0)
        args_count = 0
        firstiter = True
        while not (tokens[0].value == ')'):
            if tokens[0].value == ',' and not firstiter:
                # pops ','
                tokens.pop(0)
            firstiter = False
            exp_output, tokens = self.compileexpression(tokens[:])
            args_count += 1
        # pops ')'
        tokens.pop(0)
        return args_count, tokens[:]

    def getstatements(self):
        return [self.compiledo, self.compilelet, self.compileif, self.compilewhile, self.compilereturn]
