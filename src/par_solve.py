import sys

import query
import tasks
import utils
import interface

IL = utils.IntList

class Node:
    def __init__(self, index, label, code):
        self.index = index
        self.label = label
        self.code = code
        self.adj = [None] * 6
        self.adj_back = [None] * 6

    def bi_adjs(self):
        b = []
        for i in range(6):
            if self.adj[i] is None or self.adj_back[i] is None:
                continue
            b.append(i)
        return b

class Graph:
    def __init__(self):
        self.nodes = []
        self.code2node = {}

    def new_node(self, label, code):
        node = Node(len(self.nodes), label, code)
        if code in self.code2node:
            print('Uh oh! Duplicate code', code)
        self.code2node[code] = node
        self.nodes.append(node)
        return node

    def paint_node(self, node, code):
        assert self.code2node[node.code] is node
        del self.code2node[node.code]
        assert not (code in self.code2node)
        node.code = code
        self.code2node[code] = node

    def number_missing_edges(self):
        count = 0
        for n in self.nodes:
            for a in n.adj:
                if a is None:
                    count += 1
        return count

    def compute_reverse_edges(self, guessing = False):
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
                        assert count_none > 0
                        if count_none == 1:
                            reverse_edges_deduced += 1
                        else:
                            if guessing:
                                print('Guessing which edge goes back...', n.index, i, n2.index)
                                reverse_edges_guessed += 1
                        if count_none == 1 or guessing:
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

    def print_info(self):
        def pr_node(n):
            if n is None:
                return '  -'
            else:
                return f'{n.index:3d}'
        def pr_back(i):
            if i is None:
                return '-'
            else:
                return str(i)
        utils.print_green(f'Graph with {len(self.nodes)} nodes, missing {self.number_missing_edges()} edges')
        for node in self.nodes:
            adjs = ''.join([pr_node(n) for n in node.adj])
            adj_backs = ''.join([pr_back(i) for i in node.adj_back])
            print(f'   {node.index:2d}  {node.label}   {adjs}  {adj_backs}  {node.code}')

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

def choose_k(task):
    N = task.N
    k = 5
    if N < 70:
        k = 4
    if N < 15:
        k = 3
    if N <= 12:
        k = 2
    return k

def interpret_parallel_queries(graph, qs):
    k = len(qs)
    code2node = graph.code2node

    label0 = qs[0].raw_response[0]
    code = tuple([label0] * k)
    cur_node = graph.new_node(label0, code)
    prev_node = None

    for i, act in enumerate(qs[0].query):
        code = tuple([q.raw_response[i + 1] for q in qs])
        if act.is_door:
            prev_node = cur_node

            if len(set(code)) == 1:
                # New node!
                cur_node = graph.new_node(code[0], code)
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
            graph.paint_node(cur_node, code)

def interpret_parallel_queries_again(graph, qs):
    last_paint = -1
    for i, act in enumerate(qs[0].query):
        if not act.is_door:
            last_paint = i

    prev_node = None
    cur_node = None

    for i, act in enumerate(qs[0].query):
        code = tuple([q.raw_response[i + 1] for q in qs])
        if i < last_paint:
            continue

        if i == last_paint:
            assert not act.is_door
            cur_node = graph.code2node[code]
            continue

        assert act.is_door
        prev_node = cur_node
        cur_node = graph.code2node[code]

        # Assign edge
        if prev_node.adj[act.d] is None:
            prev_node.adj[act.d] = cur_node
        else:
            # Previously seen edge
            assert prev_node.adj[act.d] is cur_node

def build_dfs_tree(graph, N):
    path = []
    num_vis = 0
    vis = [False] * N
    def dfs(v, back):
        nonlocal num_vis
        num_vis += 1
        vis[v.index] = True
        path.append(query.MultiMark(v.code))
        for i in v.bi_adjs():
            u = v.adj[i]
            if vis[u.index]:
                continue
            path.append(query.doors[i])
            dfs(u, v.adj_back[i])
        if back != -1:
            path.append(query.doors[back])
    dfs(graph.nodes[0], -1)
    if num_vis != N:
        utils.print_red("WARNING: Not all vertices in the spanning tree!!!")
    return path

def solve(task):
    # k = choose_k(task)
    k = 5

    qs = query.parallel_queries(task, k)
    query.submit_batch(qs)

    graph = Graph()
    interpret_parallel_queries(graph, qs)

    graph.print_info()
    graph.compute_reverse_edges()
    graph.print_info()

    dfs_path = build_dfs_tree(graph, task.N)
    print(dfs_path)

    # while graph.number_missing_edges > 0:
        # utils.print_green("Edges left: " + str(graph.number_missing_edges) + ". Trying again")
        # queries = query.parallel_queries_custom(path, k=k)
        # server_resp = query.submit_batch(queries)

    if graph.number_missing_edges() == 0:
        utils.print_green('Submitting!')
        graph.submit_guess()

if __name__ == '__main__':
    task_no = 7
    if len(sys.argv) > 1:
        task_no = int(sys.argv[1])
    t = tasks.task_list[task_no]
    interface.select(t.name)
    solve(t)
