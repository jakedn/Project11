import Tokenizer as T
import sys

if __name__ == '__main__':
    print(sys.argv)
    file = sys.argv[1]

    f = open(file, "r")
    str = f.read()
    print(str)
    print(T.Tokenizer.filetoXML(str))