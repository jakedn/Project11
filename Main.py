from os import getcwd, listdir
from os.path import exists, join, isdir, isfile
import sys
from Tokenizer import *
from CompilationEngine import *

# This function takes a directory and returns all files in or of that directory
def getfiles(directory):
    cwd = getcwd()
    if not exists(directory):
        if exists(join(cwd, directory)):
            directory = join(cwd, directory)
        else:
            return []
    if isdir(directory):
        return [join(directory, f) for f in listdir(directory)
                if (isfile(join(directory, f)) and '.jack' == f[-5:])]
    if isfile(directory):
        return [directory]

    # if we get here we are not on a file or a directory
    return []

if __name__ == '__main__':
    directory = sys.argv[1]
    files = getfiles(directory)
    for file in files:
        f = open(file, "r")
        file_content = f.read()
        tokenizer = Tokenizer(file_content)
        f.close()
        # testing :
        # wT = open(file[:-5] + 'Tm.xml', "w")
        # wT.write(Tokenizer.filetoXML(file_content))
        # wT.close()
        w = open(file[:-5] + '.xml', "w")
        tokens = tokenizer.tokenize(tokenizer.file)
        engine = CompilationEngine(tokens)
        XML, tokens = engine.compileclass(engine.tokens, 0)
        w.write(XML)
        w.close()
