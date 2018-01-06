

class MyClass:

    def __init__(self, func):
        self.func = func
    def inner(self, b):
        return b-1


def outer(a):
    return a+1
if __name__ == '__main__':
    # first = MyClass(outer)
    # second = MyClass(MyClass.inner)
    # s = 0
    # # print(first.func(s))
    #
    #
    # print(second.func(second, s))
    s = "ffn    nfmmm"
    print('\t' in s)
    for i in s:
        if '\t' in i:
            print('\\')
            print('s')
        else:
            print(ord(i))
            print(ord('T'))