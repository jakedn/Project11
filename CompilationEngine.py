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
    SUBROUTINE_SCOPE = ['STATIC', 'FIELD']
    CLASS_SCOPE = ['ARG', 'VAR']

    def __init__(self, tokens, file_path):
        self.tokens = tokens
        self.class_symboltable = SymbolTable()
        self.subroutine_symboltable = SymbolTable()
        self.cur_class = None
        self.cur_subroutine_type = None # for the compile return function
        self.vmwriter = VMWriter(file_path)

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
        self.vmwriter.write_function(self.cur_class + '.' + name_func, 0) # TODO : check num_locals
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
        paraout, tokens = self.compileparameterlist(tokens[:])
        # pops '{'
        tokens.pop(0)
        done = False
        while not done:
            done = True
            newout, newtokens = self.compilevardec(tokens[:])
            if newout is not None:
                done = False
                tokens = newtokens
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

    def compilevardec(self, tokens, numspaces):
        first = tokens.pop(0)
        if not (first.isa('KEYWORD') and first.value == 'var'):
            return None, None
        output = addspaces(numspaces) + '<varDec>\n'
        # adds 'var'
        output += addspaces(numspaces + 1) + str(first)
        # adds type
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        # adds name
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        while tokens[0].value == ',':
            # adds ','
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            # adds name
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
        # adds ';'
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        output += addspaces(numspaces) + '</varDec>\n'
        return output, tokens[:]

    def compilestatements(self, tokens, numspaces):
        output = addspaces(numspaces) + '<statements>\n'
        done = False
        while not done:
            done = True
            for func in self.getstatements():
                newout, newtokens = func(tokens[:], numspaces + 1)
                if newout is not None:
                    done = False
                    output += newout
                    tokens = newtokens
        output += addspaces(numspaces) + '</statements>\n'
        return output, tokens[:]

    def compiledo(self, tokens, numspaces):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'do':
            return None, None
        output = addspaces(numspaces) + '<doStatement>\n'
        # pops 'do'
        output += addspaces(numspaces + 1) + str(first)
        if tokens[1].value != '.' or not tokens[1].isa('SYMBOL'):
            # pops name
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            out_explist, tokens = self.compileexpressionlist(tokens[:], numspaces + 1)
            output += out_explist
        else:
            # pops name
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            # pops '.'
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            # pops subname
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            out_explist, tokens = self.compileexpressionlist(tokens[:], numspaces + 1)
            output += out_explist
        # pops ';'
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        output += addspaces(numspaces) + '</doStatement>\n'
        return output, tokens[:]


    def compilelet(self, tokens, numspaces):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'let':
            return None, None
        output = addspaces(numspaces) + '<letStatement>\n'
        # adds 'let'
        output += addspaces(numspaces + 1) + str(first)
        # checks if varName[expression] or varName
        if tokens[1].value == '[':
            # adds varName
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            # adds '['
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            outcomp, tokens = self.compileexpression(tokens[:], numspaces + 1)
            output += outcomp
            # adds ']'
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
        else:
            # adds varName
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
        # adds '='
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        out_expr, tokens = self.compileexpression(tokens[:], numspaces + 1)
        output += out_expr
        # adds ';'
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        output += addspaces(numspaces) + '</letStatement>\n'
        return output, tokens[:]

    def compilewhile(self, tokens, numspaces):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'while':
            return None, None
        output = addspaces(numspaces) + '<whileStatement>\n'
        # adds 'while'
        output += addspaces(numspaces + 1) + str(first)
        # adds '('
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        outputexp, tokens = self.compileexpression(tokens[:], numspaces + 1)
        output += outputexp
        # adds ')'
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        # adds '{'
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        # adds statements
        out_statements, tokens = self.compilestatements(tokens[:], numspaces + 1)
        output += out_statements
        # adds '}'
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        output += addspaces(numspaces) + '</whileStatement>\n'
        return output, tokens[:]



    def compilereturn(self, tokens, numspaces):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'return':
            return None, None
        output = addspaces(numspaces) + '<returnStatement>\n'
        # adds 'return'
        output += addspaces(numspaces + 1) + str(first)
        if tokens[0].value != ';':
            output_exp, tokens = self.compileexpression(tokens[:], numspaces + 1)
            output += output_exp
        # pops ';'
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        output += addspaces(numspaces) + '</returnStatement>\n'
        return output, tokens[:]


    def compileif(self, tokens, numspaces):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'if':
            return None, None
        output = addspaces(numspaces) + '<ifStatement>\n'
        # adds 'if'
        output += addspaces(numspaces + 1) + str(first)
        # adds '('
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        outputexp, tokens = self.compileexpression(tokens[:], numspaces + 1)
        output += outputexp
        # adds ')'
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        # adds '{'
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        # adds statements
        out_statements, tokens = self.compilestatements(tokens[:], numspaces + 1)
        output += out_statements
        # adds '}'
        output += addspaces(numspaces + 1) + str(tokens.pop(0))
        if tokens[0].isa('KEYWORD') and tokens[0].value == 'else':
            # adds 'else'
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            # adds '{'
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            # adds statements
            out_statements, tokens = self.compilestatements(tokens[:], numspaces + 1)
            output += out_statements
            # adds '}'
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
        output += addspaces(numspaces) + '</ifStatement>\n'
        return output, tokens[:]

    def compileexpression(self, tokens, numspaces):
        output = addspaces(numspaces) + '<expression>\n'
        term_out, tokens = self.compileterm(tokens[:], numspaces + 1)
        output += term_out
        done = False
        while not done:
            done = True
            if tokens[0].value in BINOP:
                done = False
                # adds the BINOP
                output += addspaces(numspaces + 1) + str(tokens.pop(0))
                # adds term
                term_output, tokens = self.compileterm(tokens[:], numspaces + 1)
                output += term_output
        output += addspaces(numspaces) + '</expression>\n'
        return output, tokens[:]


    def compileterm(self, tokens, numspaces):
        output = addspaces(numspaces) + '<term>\n'
        # if the term is varName[expression]
        if tokens[1].value == '[':
            # pops varName
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            # pops '['
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            expression_output, tokens = self.compileexpression(tokens[:], numspaces + 1)
            output += expression_output
            # pops ']'
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
        # if the term is subroutineName(expressionList)
        elif tokens[1].value == '(' and tokens[0].isa('IDENTIFIER'):
            # pops subroutineName
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            expressionl_output, tokens = self.compileexpressionlist(tokens[:], numspaces + 1)
            output += expressionl_output
        # if the term is (className|varName).subroutineName(expressionList)
        elif tokens[1].value == '.':
            # pops className|varName
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            while tokens[0].value == '.':
                # pops '.'
                output += addspaces(numspaces + 1) + str(tokens.pop(0))
                # pops subroutineName
                output += addspaces(numspaces + 1) + str(tokens.pop(0))
            out_expr, tokens = self.compileexpressionlist(tokens[:], numspaces + 1)
            output += out_expr
        # unary operator
        elif tokens[0].value == '~' or tokens[0].value == '-':
            # adds op
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            output_term, tokens = self.compileterm(tokens[:], numspaces + 1)
            output += output_term
        # (expression)
        elif tokens[0].value == '(':
            # pops '('
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
            output_expression, tokens = self.compileexpression(tokens[:], numspaces + 1)
            output += output_expression
            # pops ')'
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
        # includes integerConstant, stringConstant, keywordConstant, varName
        else:
            output += addspaces(numspaces + 1) + str(tokens.pop(0))
        output += addspaces(numspaces) + '</term>\n'
        return output, tokens[:]



    def compileexpressionlist(self, tokens, numspaces):
        # adds '('
        output = addspaces(numspaces) + str(tokens.pop(0))
        output += addspaces(numspaces) + '<expressionList>\n'
        firstiter = True
        while not (tokens[0].value == ')'):
            if tokens[0].value == ',' and not firstiter:
                # pops ','
                output += addspaces(numspaces + 1) + str(tokens.pop(0))
            firstiter = False
            exp_output, tokens = self.compileexpression(tokens[:], numspaces + 1)
            output += exp_output
        output += addspaces(numspaces) + '</expressionList>\n'
        # pops ')'
        output += addspaces(numspaces) + str(tokens.pop(0))
        return output, tokens[:]

    def getstatements(self):
        return [self.compiledo, self.compilelet, self.compileif, self.compilewhile, self.compilereturn]
