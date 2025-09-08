import interface
import query
import tasks
import utils

relabel = {0 : '01', 1 : '23', 2 : '4', 3 : '5'}

class Sig:
    def __init__(self):
        self.sig = [set() for i in range(6)]

    def add(self, door, label):
        self.sig[door].add(label)

    def __str__(self):
        xs = []
        for i in range(6):
            if len(self.sig[i]) == 0:
                xs.append(' -')
            else:
                # xs.append(str(utils.IntList(sorted(list(self.sig[i])))))
                xs.append(''.join([relabel[x] for x in sorted(list(self.sig[i]))]))
        return '  '.join(xs)

    def __repr__(self):
        return str(self)

def run():
    return
    interface.select(tasks.task_list[1].name)
    q = query.Query()
    q.random_query0()
    q.submit()
    print('# ', q.query_string)
    print('# ', ''.join([relabel[x][:1] for x in q.response]))
    counts = [0] * 4
    for l in q.response:
        counts[l] += 1
    print('# ', counts)

    labels = q.response

    n = len(q.query)
    doors = [int(d) for d in q.query_string]

    s4 = [Sig() for i in range(4)]

    for l in [0, 1, 2, 3]:
        for i in range(n):
            if labels[i] == l:
                s4[l].add(doors[i], labels[i + 1])
        print(f'# Adjacency for {relabel[l]}:', s4[l])

    for l2 in [0, 1]:
        print(f'# {relabel[l2]}:', s4[l2])
        for l1 in [2, 3]:
            for d in range(6):
                if (l2 in s4[l1].sig[d]):
                    s = Sig()
                    for i in range(n - 1):
                        if labels[i] == l1 and doors[i] == d:
                            s.add(doors[i + 1], labels[i + 2])
                    l2 = list(s4[l1].sig[d])[0]
                    # print(f'Signature after room {relabel[l1]} through door {d} and label {relabel[l2]}:', s)
                    print(f'# {relabel[l1]}-{d}-{relabel[l2]}:', s)

def verify(adj):
    query = '213003334155002552544132541120051354123153422431122021325452552245234543115010402555541124121001050544143512'
    response = '0500000000002055020244255050050500005055002420550055024220502020244224442222424420202050052224200005052242222'

    result = [0]
    loc = 0
    for q in query:
        q = int(q)
        loc = adj[loc][q]
        result.append(loc)
    result = ''.join([['0', '0', '2', '2', '4', '5'][l] for l in result])
    print(result)
    print(response)
    print(result == response)

def read_and_submit_adj_matrix(fn = 'primus_matrix'):
    adj = []
    with open(fn, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue

            xs = line.split()
            assert len(xs) == 6
            adj.append([int(x) for x in xs])

    assert len(adj) == 6

    verify(adj)

    back = [[None] * 6 for i in range(6)]
    for n1 in range(6):
        for i in range(6):
            n2 = adj[n1][i]
            for k in range(6):
                if adj[n2][k] == n1 and back[n2][k] is None:
                    back[n1][i] = k
                    back[n2][k] = i
                    break

    print(adj)
    print(back)

    rooms = [0, 0, 1, 1, 2, 3]
    connections = []
    for n in range(6):
        for i in range(6):
            if adj[n][i] < n:
                continue
            if adj[n][i] == n and back[n][i] < i:
                continue
            connections.append({
                    'from' : {'room' : n, 'door' : i},
                    'to' : {'room' : adj[n][i], 'door' : back[n][i]}
                })

    map = {
            'rooms' : rooms,
            'startingRoom' : 0,
            'connections' : connections
        }

    print(map)

    result = interface.guess(map)
    print('Correct?', result)

if __name__ == '__main__':
    # run()
    read_and_submit_adj_matrix()
