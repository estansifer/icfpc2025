import sys
import random

import query
import tasks
import utils
import interface
import graph

def choose_k(task):
    N = task.N
    k = 4
    if N <= 72:
        k = 4
    if N <= 30:
        k = 3
    if N <= 12:
        k = 2
    return k

def interpret_parallel_queries(graph, qs, truncate = None):
    k = len(qs)
    code2node = graph.code2node

    label0 = qs[0].raw_response[0]
    code = tuple([label0] * k)
    cur_node = graph.new_node(label0, code)
    prev_node = None

    actions = qs[0].query
    if truncate:
        actions = actions[:truncate]

    for i, act in enumerate(actions):
        code = tuple([q.raw_response[i + 1] for q in qs])
        if act.is_door:
            prev_node = cur_node

            if code in graph.code2node:
                cur_node = code2node[code]
                if len(set(code)) == 1:
                    utils.print_red(f'Uh oh! Potential duplicate code {code}')
            else:
                assert len(set(code)) == 1
                cur_node = graph.new_node(code[0], code)

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

# Returns uniquely-determined prefix of path
def traverse_bfs(graph, q):
    # State consists of (index, labels, location, path)
    # index = index into q.query of next action
    valid_states = [(0, [n.label for n in graph.nodes], graph.nodes[0], [0])]

    valid_paths = []
    while len(valid_states) > 0:
        if len(valid_states) > 3000:
            print('Too many valid continuations!', len(valid_states))
            valid_paths = [path for index, labels, node, path in valid_states]
            break

        state = valid_states.pop(0)
        index, labels, node, path = state

        # print()
        # print('Popping:', index, node.index, path, utils.IntList(labels))

        if len(path) == q.n + 1:
            # print('Reached end of path')
            valid_paths.append(path)
            continue

        act = q.query[index]
        if act.is_door:
            label = q.raw_response[index + 1]
            # print(f'Passing through door {act.d} of node {node.index}, see label {label}')
            ns = graph.possible_adj(node, act.d)
            assert len(ns) > 0
            # print(f'Found {len(ns)} possible next nodes:', ' '.join([str(n.index) for n in ns]))
            if len(ns) == 1:
                n = ns[0]
                if labels[n.index] == label:
                    # print(f'Appending node at {n.index}')
                    valid_states.append((index + 1, labels, n, path + [n.index]))
            else:
                for n in ns:
                    if labels[n.index] == label:
                        # print(f'Appending node at {n.index}')
                        valid_states.append((index + 1, list(labels), n, path + [n.index]))
        else:
            # print(f'painting {act.m} on node {node.index}, server gave response {q.raw_response[index + 1]}')
            labels[node.index] = act.m
            valid_states.append((index + 1, labels, node, path))

    print(f'Found {len(valid_paths)} valid paths')
    assert len(valid_paths) > 0
    prefix = []
    for i, loc in enumerate(valid_paths[0]):
        inconsistent = False
        for path in valid_paths:
            if path[i] != loc:
                inconsistent = True
        if inconsistent:
            break
        prefix.append(loc)
    print(f'Longest certain prefix:', len(prefix))
    return prefix

def deduce_from_path(g, q):
    prefix = traverse_bfs(g, q)
    deductions = 0
    for i in range(len(prefix) - 1):
        n1 = g.nodes[prefix[i]]
        n2 = g.nodes[prefix[i + 1]]
        d = q.query_doors_only[i].d
        if n1.adj[d] is None:
            print(f'Inferring door {d} of {n1.index} goes to {n2.index}')
            deductions += 1
            n1.adj[d] = n2
        else:
            assert n1.adj[d] is n2

    print('Made', deductions, 'deductions from the path')
    return deductions

def build_dfs_tree(graph, N, k):
    path = []
    num_vis = 0
    vis = [False] * N

    def check_for_unique_unused_labels():
        label2node = {}
        for i in range(N):
            if vis[i]:
                continue
            label = graph.nodes[i].label
            if label in label2node:
                label2node[label].append(graph.nodes[i])
            else:
                label2node[label] = [graph.nodes[i]]

        for label in label2node:
            nodes = label2node[label]
            if len(nodes) == 1:
                graph.code2node[tuple([label] * k)] = nodes[0]
                vis[nodes[0].index] = True


    def dfs(v):
        nonlocal num_vis
        num_vis += 1
        vis[v.index] = True
        path.append(query.MultiMark(v.code))
        check_for_unique_unused_labels()
        if all(vis):
            return

        for i in v.bi_adjs():
            u = v.adj[i]
            if vis[u.index]:
                continue
            path.append(query.doors[i])
            dfs(u)
            if all(vis):
                return
            path.append(query.doors[v.adj_back[i]])

    dfs(graph.nodes[0])

    if num_vis != N:
        utils.print_green("Not all vertices in the spanning tree. Found: " + str(num_vis))
    else:
        utils.print_green("Marked all nodes!")

    used_labels = [False] * 4
    for v in range(N):
        if vis[v]:
            continue
        v = graph.nodes[v]
        if used_labels[v.label]:
            utils.print_red("ERROR: Cannot uniquely mark nodes!!! Found: " + str(num_vis) + "\nRepreated label: " + str(v.label))
            exit(1)
        used_labels[v.label] = True
        graph.code2node[tuple([v.label] * k)] = v
        
    return path

def print_path(graph, path):
    for x in path:
        if x.is_door:
            print(x, end=" ")
        else:
            print("[" + str(graph.code2node[x.m].index) + "]", end=" ")
    print()

def solve(task, num_tries = 6):
    k = choose_k(task)
    # truncate = int (task.N * 7.2 + random.random() * 50)
    truncate = int (task.N * 15)
    utils.print_green(f'Solving task {task.name} with {task.N} nodes and k = {k}')

    qs = query.parallel_queries(task, k, truncate)
    query_count = query.submit_batch(qs)
    # q = query.Query(task).random_query3()
    # query_count = query.submit_batch(qs + [q])

    g = graph.Graph()
    interpret_parallel_queries(g, qs, truncate)
    g.print_info(True)
    if len(g.nodes) + 1 == task.N:
        print('Missing one node...')
        g.add_missing_node()

    if len(g.nodes) < task.N:
        utils.print_red(f'Only found {len(g.nodes)} of {task.N} nodes')
        exit(1)
    if len(g.nodes) > task.N:
        utils.print_red(f'Found {len(g.nodes)} of {task.N} nodes!!')
        exit(1)

    g.compute_node_groups(task.mirrors)
    for i in range(6):
        count = 0
        # count += g.deduce_from_node_groups()
        count += g.compute_reverse_edges()
        # count += deduce_from_path(g, q)
        for q in qs:
            count += deduce_from_path(g, q)
        if count == 0:
            break
    g.print_info(True)

    if g.number_missing_edges() <= 20:
        g.compute_reverse_edges(guessing = True, full_guessing = True)
        utils.print_green(f"Current query count: {query_count}")
        utils.print_green('Submitting!')
        g.submit_guess()
        return

    return

    k = g.repaint_all_nodes()

    dfs_path = build_dfs_tree(g, task.N, k)
    print_path(g, dfs_path)

    all_queries = []
    for _ in range(num_tries):
        all_queries += query.parallel_queries_custom(dfs_path, k)
    query_count = query.submit_batch(all_queries)

    for i in range(num_tries):
        utils.print_green("Edges left: " + str(g.number_missing_edges()) + ". Trying again")

        qs = all_queries[i*k:(i+1)*k]

        interpret_parallel_queries_again(g, qs)
        g.print_info()
        g.deduce_from_node_groups()
        g.compute_reverse_edges()
        g.deduce_from_node_groups()
        g.compute_reverse_edges()
        g.print_info()

    utils.print_green("Guessing finished. Edges left: " + str(g.number_missing_edges()))
    g.compute_reverse_edges(guessing = True, full_guessing = True)
    utils.print_green(f"Current query count: {query_count}")
    utils.print_green('Submitting!')
    g.submit_guess()

if __name__ == '__main__':
    task_no = 6
    num_tries = 1
    if len(sys.argv) > 1:
        task_no = int(sys.argv[1])
        if len(sys.argv) > 2:
            num_tries = int(sys.argv[2])
    t = tasks.task_list[task_no]
    interface.select(t.name)
    solve(t, num_tries)
