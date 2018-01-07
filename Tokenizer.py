########################################################
# Tokenizer Class
# nand project 10
#
########################################################
import re

class Tokenizer:

    def __init__(self, filecontent):
        self.file = filecontent

    TokenType = \
        {
            'SPACE' : r'[ \t]+',    # space and tab
            'NL' : r'\n|\r',
            'COMMENT' : r'(?://.*)|(?:/\*(?:\n|\r|.)*?\*/)|(?:/\*\*(?:\n|\r|.)*?\*\*/)',
            'SYMBOL' : r'(?P<SYMBOL>[{}()[\].,;+\-*/&|<>=~])',
            'KEYWORD' : r'\b(?P<KEYWORD>class|constructor|function|method|field|static|var|int|char|boolean|void|'
                        r'true|false|null|this|let|do|if|else|while|return)\b',
            'IDENTIFIER' : r'(?P<IDENTIFIER>[a-z_A-Z][a-zA-Z_0-9]*)',
            'INT_CONST' : r'(?P<INT_CONST>[0-9]+)',
            'STR_CONST' : r'"(?P<STR_CONST>[^"\n]*)"'
        }
    TokenTypes = ['SPACE', 'NL', 'COMMENT', 'SYMBOL', 'KEYWORD', 'IDENTIFIER',
                  'INT_CONST', 'STR_CONST']
    XMLTokenType = \
        {
            'COMMENT' : 'comment',
            'SYMBOL' : 'symbol',
            'KEYWORD' : 'keyword',
            'IDENTIFIER' : 'identifier',
            'INT_CONST' : 'integerConstant',
            'STR_CONST' : 'stringConstant'
        }

    # an instance of this class represents a token (piece f language for the assembler)
    class Token:
        def __init__(self, typeOfToken, value):
            self.type = typeOfToken
            self.value = value

        def __str__(self):
            return '<' + Tokenizer.XMLTokenType[self.type] + '> ' + Tokenizer.symboltostring(self.value) + \
                        ' </' + Tokenizer.XMLTokenType[self.type] + '>\n'

        def isa(self, tokentype):
            return self.type == tokentype



    # creates a compiled pattern for regex use based on all tokentypes
    @staticmethod
    def makeMatcher():
        pattern = r''
        for ttype in Tokenizer.TokenTypes:
            pattern += r'|' + Tokenizer.TokenType[ttype]

        # we have "|" in the beginning of pattern that needs to be taken out
        return re.compile(pattern[1:])


    # breaks str of jack code into tokens
    @staticmethod
    def tokenize(str):
        tokens = []
        matcher = Tokenizer.makeMatcher()
        nextmatch = matcher.match(str)

        # while we have another match make an corresponding token and add it to tokens
        while nextmatch:
            if nextmatch.group('SYMBOL') != None:
                tokens.append(Tokenizer.Token('SYMBOL', Tokenizer.symboltostring(nextmatch.group('SYMBOL'))))
            for name in ['KEYWORD', 'IDENTIFIER', 'INT_CONST', 'STR_CONST']:
                if nextmatch.group(name) != None:
                    tokens.append(Tokenizer.Token(name, nextmatch.group(name)))
                    break

            # the next line takes out the part of the string that was matched
            str = str[nextmatch.group().__len__():]
            nextmatch = matcher.match(str)
        return tokens

    @staticmethod
    def symboltostring(symbol):
        #todo maybe get ride of entirly
        # if symbol == '>':
        #     return '&gt;'
        # if symbol == '<':
        #     return '&lt;'
        # if symbol == '&':
        #     return '&amp;'
        return symbol

    @staticmethod
    def filetoXML(file_data):
        tokens = Tokenizer.tokenize(file_data)
        output = '<tokens>\n'
        for token in tokens:
            for ttype in Tokenizer.XMLTokenType.keys():
                if token.isa(ttype):
                    output += '\t<' + Tokenizer.XMLTokenType[ttype] + '> ' + Tokenizer.symboltostring(token.value) + \
                        ' </' + Tokenizer.XMLTokenType[ttype] + '>\n'
        output += '</tokens>'
        return output



