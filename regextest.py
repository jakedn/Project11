import re



if __name__ == '__main__':
    s = "+{}()[].,;-*&<>=~"
    iss = [s[i] for i in range(len(s))]
    pattern = re.compile(r'(?P<SYMBOL>/\*.*\*/)')
    for i in iss:
        a = pattern.match(i)
        print(a.group())
