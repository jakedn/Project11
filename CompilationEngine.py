########################################################
# CompilationEngine Class
# nand project 10
# HI MARIA
########################################################

from SymbolTable import *
from VMWriter import *

BINOP = [ADD, SUB, MULTIPLY, DIVIDE, AND, OR, LT, GT, EQ]
def addspaces(n):
    str = ''
    for i in range(n):
        str += ' '
    return str


class CompilationEngine:

    def __init__(self, tokens, file_path):
        self.tokens = tokens
        self.class_symboltable = SymbolTable()
        self.subroutine_symboltable = SymbolTable()
        self.cur_class = None
        self.cur_subroutine_type = None  # for the compile return function
        self.vmwriter = VMWriter(file_path)
        self.labelcounter = 0

    def compileclass(self, tokens):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or not first.value == 'class':
            return None, None
        # adds class name
        self.cur_class = tokens.pop(0).value
        # pops '{'
        tokens.pop(0)
        # deals with classVar
        done = False
        while not done:
            done = True
            newout, newtokens = self.compileclassvar(tokens[:])
            if newout is not None:
                done = False
                tokens = newtokens

        # subroutines
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
        type = tokens.pop(0).value
        # name
        name = tokens.pop(0).value
        self.class_symboltable.define(name, type, first.value)
        while tokens[0].value == ',':
            # pops ','
            tokens.pop(0)
            # name
            name = tokens.pop(0).value
            self.class_symboltable.define(name, type, first.value)
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
        type_func = tokens.pop(0).value
        self.cur_subroutine_type = type_func
        if first.value == 'method':
            self.subroutine_symboltable.define('this', self.cur_class, 'argument')
        # adds subroutine name
        name_func = tokens.pop(0).value
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
            self.vmwriter.write_push(CONST, push_index)
            self.vmwriter.write_call('Memory.alloc', 1)
            self.vmwriter.write_pop(POINTER, 0)
        elif first.value == 'method':
            #self.subroutine_symboltable.define('this', self.cur_class, 'argument')
            self.vmwriter.write_push(ARG, 0)
            self.vmwriter.write_pop(POINTER, 0)
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
            type_param = tokens.pop(0).value
            # adds varName
            name_param = tokens.pop(0).value
            self.subroutine_symboltable.define(name_param, type_param, 'argument')
        while tokens[0].value == ',':
            # pops ','
            tokens.pop(0)
            # adds type
            type_param = tokens.pop(0).value
            # adds varName
            name_param = tokens.pop(0).value
            self.subroutine_symboltable.define(name_param, type_param, 'argument')
        # popping the ')'
        tokens.pop(0)
        return 0, tokens[:]

    def compilevardec(self, tokens):
        first = tokens.pop(0)
        if not (first.isa('KEYWORD') and first.value == 'var'):
            return None, None
        # adds type
        vartype = tokens.pop(0).value
        # adds name
        varname = tokens.pop(0).value
        varcount = 1
        self.subroutine_symboltable.define(varname, vartype, 'VAR')
        while tokens[0].value == ',':
            # pops ','
            tokens.pop(0)
            # adds name
            varname = tokens.pop(0).value
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
            name = tokens.pop(0).value
            # get expressions
            self.vmwriter.write_push(POINTER, 0)
            out_explist, tokens = self.compileexpressionlist(tokens[:])
            self.vmwriter.write_call(self.cur_class + '.' + name, out_explist + 1)

        else:
            addthis = 0
            # pops name
            name = tokens.pop(0).value
            # pops '.'
            tokens.pop(0)
            # pops subname
            subname = tokens.pop(0).value
            kind = self.subroutine_symboltable.kind_of(name)
            if kind == None:
                kind = self.class_symboltable.kind_of(name)
                if kind != None:
                    index = self.class_symboltable.index_of(name)
                    class_kind = self.class_symboltable.type_of(name)

            else:
                index = self.subroutine_symboltable.index_of(name)
                class_kind = self.subroutine_symboltable.type_of(name)
            if kind != None:
                self.vmwriter.write_push(kind, index)
                addthis = 1
            else:
                # it isnt a variable meaning it must be a class
                class_kind = name
            # getting the list
            out_explist, tokens = self.compileexpressionlist(tokens[:])

            self.vmwriter.write_call(class_kind + '.' + subname, out_explist + addthis)
        self.vmwriter.write_pop(TEMP, 0)
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
            varname = tokens.pop(0).value
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
            self.vmwriter.write_arithmetic(ADD)
            # pops '='
            tokens.pop(0)
            out_expr, tokens = self.compileexpression(tokens[:])  # pushes something
            self.vmwriter.write_pop(TEMP, 0)
            self.vmwriter.write_pop(POINTER, 1)
            self.vmwriter.write_push(TEMP, 0)
            self.vmwriter.write_pop(THAT, 0)
        else:
            # adds varName
            varname = tokens.pop(0).value
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

    def compilewhile(self, tokens):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'while':
            return None, None
        label1 = self.labelcounter
        label2 = self.labelcounter + 1
        self.labelcounter += 2
        self.vmwriter.write_label('L' + str(label1))
        # pops '('
        tokens.pop(0)
        outputexp, tokens = self.compileexpression(tokens[:])
        # adds ')'
        tokens.pop(0)
        self.vmwriter.write_arithmetic(NOT)
        self.vmwriter.write_if('L' + str(label2))
        # pops '{'
        tokens.pop(0)
        # adds statements
        out_statements, tokens = self.compilestatements(tokens[:])
        self.vmwriter.write_goto('L' + str(label1))
        self.vmwriter.write_label('L' + str(label2))
        # pops '}'
        tokens.pop(0)
        return 0, tokens[:]

    def compilereturn(self, tokens):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'return':
            return None, None
        if tokens[0].value != ';':
            output_exp, tokens = self.compileexpression(tokens[:])
        # pops ';'
        tokens.pop(0)
        if self.cur_subroutine_type == 'void':
            self.vmwriter.write_push(CONST, 0)
        self.vmwriter.write_return()
        return 0, tokens[:]


    def compileif(self, tokens):
        first = tokens.pop(0)
        if not first.isa('KEYWORD') or first.value != 'if':
            return None, None
        # pops '('
        tokens.pop(0)
        label1 = self.labelcounter
        label2 = self.labelcounter + 1
        self.labelcounter += 2
        outputexp, tokens = self.compileexpression(tokens[:])
        # pops ')'
        tokens.pop(0)
        self.vmwriter.write_arithmetic(NOT)
        self.vmwriter.write_if('L' + str(label1))
        # pops '{'
        tokens.pop(0)
        # adds statements
        out_statements, tokens = self.compilestatements(tokens[:])
        # pops '}'
        tokens.pop(0)
        self.vmwriter.write_goto('L' + str(label2))
        self.vmwriter.write_label('L' + str(label1))
        if tokens[0].isa('KEYWORD') and tokens[0].value == 'else':
            # pops 'else'
            tokens.pop(0)
            # pops '{'
            tokens.pop(0)
            # adds statements
            out_statements, tokens = self.compilestatements(tokens[:])
            # pops '}'
            tokens.pop(0)
        self.vmwriter.write_label('L' + str(label2))
        return 0, tokens[:]

    def compileexpression(self, tokens):
        term_out, tokens = self.compileterm(tokens[:])
        done = False
        while not done:
            done = True
            if tokens[0].value in BINOP:
                done = False
                # adds the BINOP
                binop = self.symboltostring(tokens.pop(0).value)
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
            varname = tokens.pop(0).value
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
            self.vmwriter.write_arithmetic(ADD)
            self.vmwriter.write_pop(POINTER, 1)
            self.vmwriter.write_push(THAT, 0)
        # if the term is subroutineName(expressionList)
        elif tokens[1].value == '(' and tokens[0].isa('IDENTIFIER'):
            # pops name
            name = tokens.pop(0).value
            out_explist, tokens = self.compileexpressionlist(tokens[:])
            self.vmwriter.write_push(POINTER, 0)  # TODO : check
            self.vmwriter.write_call(self.cur_class + '.' + name, out_explist + 1)
        # if the term is (className|varName).subroutineName(expressionList)
        elif tokens[1].value == '.':
            # pops name
            name = tokens.pop(0).value
            # pops '.'
            tokens.pop(0)
            # pops subname
            subname = tokens.pop(0).value
            out_explist, tokens = self.compileexpressionlist(tokens[:])
            varkind = self.subroutine_symboltable.kind_of(name)
            if varkind is None:
                varkind = self.class_symboltable.kind_of(name)
                if varkind is None:
                    1
                    # self.vmwriter.write_push(self.POINTER, 0)
                    # out_explist += 1
                else:
                    varindex = self.class_symboltable.index_of(name)
                    self.vmwriter.write_push(varkind, varindex)
                    name = self.class_symboltable.type_of(name)  # TODO: check
                    out_explist += 1
            else:
                varindex = self.subroutine_symboltable.index_of(name)
                self.vmwriter.write_push(varkind, varindex)
                name = self.subroutine_symboltable.type_of(name)  # TODO: check
                out_explist += 1
            self.vmwriter.write_call(name + '.' + subname, out_explist)
        # unary operator
        elif tokens[0].value == '~' or tokens[0].value == '-':
            # adds op
            operator = tokens.pop(0).value
            output_term, tokens = self.compileterm(tokens[:])  # pushes something
            if operator == '~':
                self.vmwriter.write_arithmetic(NOT)
            elif operator == '-':
                self.vmwriter.write_arithmetic(NEG)
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
                self.vmwriter.write_push(CONST, len(string_const))
                self.vmwriter.write_call('String.new', 1)
                for ch in string_const:
                    if ch == '\n':
                        self.vmwriter.write_push(CONST, ord('\\'))
                        self.vmwriter.write_call('String.appendChar', 2)
                        self.vmwriter.write_push(CONST, ord('n'))
                        self.vmwriter.write_call('String.appendChar', 2)
                    elif ch == '\t':
                        self.vmwriter.write_push(CONST, ord('\\'))
                        self.vmwriter.write_call('String.appendChar', 2)
                        self.vmwriter.write_push(CONST, ord('t'))
                        self.vmwriter.write_call('String.appendChar', 2)
                    elif ch == '\r':
                        self.vmwriter.write_push(CONST, ord('\\'))
                        self.vmwriter.write_call('String.appendChar', 2)
                        self.vmwriter.write_push(CONST, ord('r'))
                        self.vmwriter.write_call('String.appendChar', 2)
                    elif ch == '\b':
                        self.vmwriter.write_push(CONST, ord('\\'))
                        self.vmwriter.write_call('String.appendChar', 2)
                        self.vmwriter.write_push(CONST, ord('b'))
                        self.vmwriter.write_call('String.appendChar', 2)
                    else:
                        self.vmwriter.write_push(CONST, ord(ch))
                        self.vmwriter.write_call('String.appendChar', 2)
            elif constant_token.isa('INT_CONST'):
                self.vmwriter.write_push(CONST, constant_token.value)
            # var name
            elif constant_token.isa('IDENTIFIER'):
                varname = constant_token.value
                varkind = self.subroutine_symboltable.kind_of(varname)
                if varkind is None:
                    varkind = self.class_symboltable.kind_of(varname)
                    varindex = self.class_symboltable.index_of(varname)
                else:
                    varindex = self.subroutine_symboltable.index_of(varname)
                self.vmwriter.write_push(varkind, varindex)
            elif constant_token.isa('KEYWORD'):
                keyword = constant_token.value
                if keyword == 'true':
                    self.vmwriter.write_push(CONST, 0)
                    self.vmwriter.write_arithmetic(NOT)
                elif keyword == 'false' or keyword == 'null':
                    self.vmwriter.write_push(CONST, 0)
                elif keyword == 'this':
                    self.vmwriter.write_push(POINTER, 0)  # TODO: make sure correctness


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

    def symboltostring(self, str1):
        #todo maybe erase
        # if str1 == '&gt;':
        #     return '>'
        # if str1 == '&lt;':
        #     return '<'
        # if str1 == '&amp;':
        #     return '&'
        return str1

    def close(self):
        self.vmwriter.close()
