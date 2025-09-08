import utils
import query
import interface

verbose_graph_info = False

all_node_groups = []

class Node:
    def __init__(self, index, label, code):
        self.index = index
        self.label = label
        self.code = code
        self.adj = [None] * 6
        self.adj_back = [None] * 6
        self.node_group = None

    def bi_adjs(self):
        b = []
        for i in range(6):
            if self.adj[i] is None or self.adj_back[i] is None:
                continue
            b.append(i)
        return b

    def similarity(self, other):
        if self.label != other.label:
            return 0
        count = 1
        for i in range(6):
            if None in [self.adj[i], other.adj[i]]:
                continue
            if self.adj[i].label == other.adj[i].label:
                count += 1
            else:
                return 0
        return count

    def siblings(self):
        nodes = []
        for node in self.node_group.nodes:
            if not (node is self):
                nodes.append(node)
        return nodes

class NodeGroup:
    def __init__(self, nodes):
        all_node_groups.append(self)
        assert len(nodes) >= 2
        self.nodes = list(nodes)
        self.adj = [None] * 6

        for node in nodes:
            node.node_group = self

        self.floodfill()

    def __str__(self):
        ns = sorted([n.index for n in self.nodes])
        return ' '.join([f'{n:2d}' for n in ns])

    def __repr__(self):
        return str(self)

    def floodfill(self):
        for i in range(6):
            nodes = []
            for n in self.nodes:
                if n.adj[i] is None:
                    continue
                nodes.append(n.adj[i])
            ng = self.adj[i]
            for n in nodes:
                if not (n.node_group is None):
                    ng = n.node_group
            if ng is None:
                if len(nodes) >= 2:
                    ng = NodeGroup(nodes)
                else:
                    continue
            self.adj[i] = ng
            for n in nodes:
                if n.node_group is None:
                    n.node_group = ng
                    ng.nodes.append(n)
                    ng.floodfill()

class Graph:
    def __init__(self):
        self.nodes = []
        self.node_groups = []
        self.code2node = {}

    def new_node(self, label, code):
        node = Node(len(self.nodes), label, code)
        self.code2node[code] = node
        self.nodes.append(node)
        return node

    def paint_node(self, node, code):
        assert self.code2node[node.code] is node
        del self.code2node[node.code]
        assert not (code in self.code2node)
        node.code = code
        self.code2node[code] = node

    def repaint_all_nodes(self):
        k = 4
        if len(self.nodes) <= 60:
            k = 3
        if len(self.nodes) <= 12:
            k = 2

        for n in self.nodes:
            self.paint_node(n, n.code + (7,))

        x = 1
        for n in self.nodes:
            code = query.base4(x, k)
            x += 1
            if len(set(code)) == 1:
                code = query.base4(x, k)
                x += 1

            self.paint_node(n, tuple(code))

        return k

    def add_missing_node(self):
        label_counts = [0] * 4
        for node in self.nodes:
            label_counts[node.label] += 1
        label = label_counts.index(min(label_counts))

        self.new_node(label, tuple([label] * len(self.nodes[0].code)))


    def possible_adj(self, node, i):
        if node.adj[i] is None:
            if node.node_group is None:
                ns = self.nodes
            else:
                if node.node_group.adj[i] is None:
                    ns = self.nodes
                else:
                    ns = node.node_group.adj[i].nodes
            ns_ = []
            for n in ns:
                if (None in n.adj) or (node in n.adj):
                    ns_.append(n)
            return ns_
        else:
            return [node.adj[i]]

    def number_missing_edges(self):
        count = 0
        for n in self.nodes:
            for a in n.adj:
                if a is None:
                    count += 1
        return count

    def compute_node_groups(self, mirrors):
        if mirrors == 1:
            return

        N = len(self.nodes)
        similarity = []
        for i in range(N):
            for j in range(i + 1, N):
                s = self.nodes[i].similarity(self.nodes[j])
                similarity.append((s, i, j, self.nodes[i], self.nodes[j]))
        similarity.sort(reverse = True)

        while True:
            nones = 0
            for node in self.nodes:
                if node.node_group is None:
                    nones += 1
            print('Number of nodes with None for node group:', nones)
            if nones == 0:
                break

            for s, i, j, ni, nj in similarity:
                if not (None in [ni.node_group, nj.node_group]):
                    continue

                if not (ni.node_group is None):
                    if len(ni.node_group.nodes) == mirrors:
                        continue
                if not (nj.node_group is None):
                    if len(nj.node_group.nodes) == mirrors:
                        continue

                print(f'Next most similar pair are nodes {i} and {j} with similarity of {s}')
                if not (ni.node_group is None):
                    ni.node_group.nodes.append(nj)
                    nj.node_group = ni.node_group
                    ni.node_group.floodfill()
                elif not (nj.node_group is None):
                    nj.node_group.nodes.append(ni)
                    ni.node_group = nj.node_group
                    nj.node_group.floodfill()
                else:
                    NodeGroup([ni, nj])
                break

        for ng in all_node_groups:
            ng.floodfill()

        # Check consistency...
        assert len(all_node_groups) * mirrors == N
        # for ng in all_node_groups:
            # print('   ', ng, '  ->  ', ng.adj)
            # assert not (None in ng.adj)
        for node in self.nodes:
            assert len(node.node_group.nodes) == mirrors
            for i in range(6):
                assert (None in [node.adj[i], node.node_group.adj[i]]) or (node.adj[i].node_group is node.node_group.adj[i])

    def deduce_from_node_groups(self):
        for ng in all_node_groups:
            ng.floodfill()

        forward_edges_deduced = 0
        reverse_edges_deduced = 0

        for n in self.nodes:
            ng = n.node_group
            siblings = n.siblings()
            for i in range(6):
                if n.adj[i] is None:
                    # Check if other nodes in group are resolved...
                    any_missing = False
                    for n2 in siblings:
                        if n2.adj[i] is None:
                            any_missing = True
                    if any_missing:
                        continue

                    # All siblings are resolved, so we can deduce the target
                    targets = list(siblings[0].adj[i].node_group.nodes)
                    for n2 in siblings:
                        targets.remove(n2.adj[i])
                    assert len(targets) == 1
                    n.adj[i] = targets[0]
                    forward_edges_deduced += 1

                if not (n.adj_back[i] is None):
                    continue
                # Deduce reverse edges
                n2 = n.adj[i]
                done = False
                for j in range(6):
                    if (n2.adj[j] is n) and (n2.adj_back[j] is None):
                        n2.adj_back[j] = i
                        n.adj_back[i] = j
                        done = True
                        reverse_edges_deduced += 1
                        break

                if done:
                    continue

                valid = [None] * 6
                for j in range(6):
                    if n2.adj[j] is None:
                        valid[j] = (n2.node_group.adj[j] in [ng, None])
                    else:
                        valid[j] = False

                if sum(valid) == 1:
                    for j in range(6):
                        if valid[j]:
                            assert n2.adj_back[j] is None
                            n2.adj[j] = n
                            n2.adj_back[j] = i
                            n.adj_back[i] = j
                            reverse_edges_deduced += 1
                            break

        print('Forward edges deduced:', forward_edges_deduced)
        print('Reverse edges deduced:', reverse_edges_deduced)

        return forward_edges_deduced + reverse_edges_deduced

    def compute_reverse_edges(self, guessing = False, full_guessing = False):
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
                        if count_none == 1 or guessing:
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

        missing_edges = self.number_missing_edges()
        if missing_edges == 1 or full_guessing:
            # Missing a self-loop, nothing else
            for n in self.nodes:
                for i in range(6):
                    if n.adj[i] is None:
                        n.adj[i] = n
                        n.adj_back[i] = i
                        if missing_edges == 1:
                            reverse_edges_deduced += 1
                        else:
                            reverse_edges_guessed += 1

        print('Reverse edges deduced:', reverse_edges_deduced)
        print('Reverse edges guessed:', reverse_edges_guessed)

        return reverse_edges_deduced + reverse_edges_guessed

    def print_info(self, verbose = verbose_graph_info):
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
        if verbose:
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
        if not result:
            exit(1)
