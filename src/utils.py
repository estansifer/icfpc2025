import interface

prod = True

def guess(path):
    if prod:
        return interface.explore(path)['results']
    else:
        print(path)
        res = input()
        return [int(c) for c in res]

def guess_unbatched(path):
    if prod:
        return interface.explore([path])['results'][0]
    else:
        print(path)
        res = input()
        return [int(c) for c in res]

def compare(arr1, arr2):
    res = []
    for i in range(len(arr1)):
        if arr1[i] != arr2[i]:
            res.append(i)
    return res

def different(i):
    if i == 0:
        return 1
    return 0

def print_green(strr):
    print("\033[32m" + strr + "\033[0m")

M = 1442968193 # prime number

class IntList:
    def __init__(self, values):
        self.n = len(values)
        assert self.n > 0
        self.values = [int(v) for v in values]
        x = 0
        for v in self.values:
            x = (x * 6 + v) % M
        self.x = x

    def drop_last(self):
        assert self.n > 1
        return IntList(self.values[:-1])

    def __hash__(self):
        return self.x

    def __eq__(self, other):
        return self.n == other.n and self.x == other.x

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        # return str(self.values)
        return ''.join([str(v) for v in self.values])

    def __repr__(self):
        return str(self)

class PathWithLabels:
    def __init__(self, path, labels):
        self.path = path
        self.labels = labels
        self.n = path.n
        assert path.n + 1 == labels.n

    def __hash__(self):
        return hash((self.path, self.labels))

    def __eq__(self, other):
        return self.path == other.path and self.labels == other.labels

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        s = '(' + str(self.labels.values[0]) + ')'
        for i in range(self.path.n):
            s += ' ' + str(self.path.values[i])
            s += ' (' + str(self.labels.values[i + 1]) + ')'
        return s
