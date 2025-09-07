import query
import tasks
import utils
import interface

IL = utils.IntList

class Node:
    def __init__(self, index, label):
        self.index = index
        self.label = label
        self.code = None
        self.adj = [None] * 6
        self.adj_back = [None] * 6

class Graph:
    def __init__(self):
        self.nodes = []

    def new_node(self, label):
        node = Node(len(self.nodes), label)
        self.nodes.append(node)
        return node

    def number_missing_edges(self):
        count = 0
        for n in self.nodes:
            for a in n.adj:
                if a is None:
                    count += 1
        return count

    def compute_reverse_edges(self):
        reverse_edges_deduced = 0
        reverse_edges_guessed = 0
        for n in self.nodes:
            for i in range(6):
                n2 = n.adj[i]
                if n2 is None:
                    continue

                if n.adj_back[i] is None:
                    done = False
                    for j in range(6):
                        if (n2.adj[j] is n) and (n2.adj_back[j] is None):
                            n2.adj_back[j] = i
                            n.adj_back[i] = j
                            done = True
                            break

                    if not done:
                        count_none = sum([n3 is None for n3 in n2.adj])
                        if count_none == 0:
                            print(n.index, i, n2.index)
                            print([n3.index for n3 in n2.adj])
                        assert count_none > 0
                        if count_none == 1:
                            reverse_edges_deduced += 1
                        else:
                            print('Guessing which edge goes back...', n.index, i, n2.index)
                            reverse_edges_guessed += 1
                        for j in range(6):
                            if n2.adj[j] is None:
                                n2.adj[j] = n
                                n2.adj_back[j] = i
                                n.adj_back[i] = j
                                break

        if self.number_missing_edges() == 1:
            # Missing a self-loop, nothing else
            for n in self.nodes:
                for i in range(6):
                    if n.adj[i] is None:
                        n.adj[i] = n
                        n.adj_back[i] = i
                        reverse_edges_deduced += 1

        print('Reverse edges deduced:', reverse_edges_deduced)
        print('Reverse edges guessed:', reverse_edges_guessed)

    def submit_guess(self):
        assert self.number_missing_edges() == 0
        rooms = [n.label for n in self.nodes]
        connections = []
        for n in self.nodes:
            for i in range(6):
                if n.adj[i].index < n.index:
                    continue
                if n.adj[i].index == n.index and n.adj_back[i] < i:
                    continue
                connections.append({
                        'from' : {'room' : n.index, 'door' : i},
                        'to' : {'room' : n.adj[i].index, 'door' : n.adj_back[i]},
                    })

        map = {
                'rooms' : rooms,
                'startingRoom' : 0,
                'connections' : connections
            }

        result = interface.guess(map)
        print('Correct?', result)

def solve(task):
    N = task.N
    k = 5
    if N < 70:
        k = 4
    if N < 15:
        k = 3

    qs = query.parallel_queries(task, k)
    query.submit_batch(qs)

    # for q in qs:
        # print(q.query_string)
        # print(IL(q.raw_response))

    graph = Graph()
    code2node = {}
    prev_node = None
    cur_node = graph.new_node(qs[0].raw_response[0])
    cur_node.code = tuple([cur_node.label] * k)
    code2node[cur_node.code] = cur_node

    for i, act in enumerate(qs[0].query):
        if act.is_door:
            prev_node = cur_node
            code = tuple([q.raw_response[i + 1] for q in qs])

            if len(set(code)) == 1:
                # New node!
                if code in code2node:
                    print('Uh oh! Duplicate code', code, ' at position ', i)
                cur_node = graph.new_node(code[0])
                code2node[code] = cur_node
                cur_node.code = code
            else:
                # Previously seen node
                assert code in code2node
                cur_node = code2node[code]

            # Assign edge
            if prev_node.adj[act.d] is None:
                prev_node.adj[act.d] = cur_node
            else:
                # Previously seen edge
                assert prev_node.adj[act.d] is cur_node
        else:
            # Painting a node
            assert code2node[cur_node.code] is cur_node
            del code2node[cur_node.code]
            code = tuple([q.raw_response[i + 1] for q in qs])
            assert not (code in code2node)
            cur_node.code = code
            code2node[code] = cur_node

    print('Distinct nodes:', len(graph.nodes))
    def pr_node(n):
        if n is None:
            return 'N'
        else:
            return n.index
    for node in graph.nodes:
        print('    ', node.index, node.label, node.code, [pr_node(n) for n in node.adj])
    print('Missing edges:', graph.number_missing_edges())
    graph.compute_reverse_edges()
    for node in graph.nodes:
        print('    ', node.index, node.label, node.code, [pr_node(n) for n in node.adj])
    print('Missing edges:', graph.number_missing_edges())

    if graph.number_missing_edges() == 0:
        print('Submitting!')
        graph.submit_guess()

if __name__ == '__main__':
    t = tasks.task_list[5]
    interface.select(t.name)
    solve(t)
