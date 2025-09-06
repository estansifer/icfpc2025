import interface

prod = True

def guess(path):
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