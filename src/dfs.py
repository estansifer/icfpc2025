import utils, interface, tasks

task_no = 1
DOORS = 6
N = tasks.task_list[task_no].N
PROBLEM_NAME = tasks.task_list[task_no].name

class Graph:
    # n -> num known vertices
    # edge -> n * 6 -> edges (-1 if unknown)
    # letter -> letter of vertex
    # mst -> list of mst sons for each vertex, for easy mst traversal
    # parent -> mst parent
    # edge_from_parent -> desc
    def __init__(self, max_n):
        self.n = 1
        self.edge = [[-1] * DOORS for _ in range(max_n + 2)]
        self.letter = [0] * (max_n + 2)
        self.letter[1] = utils.guess("")[0]
        self.mst = [[] for _ in range(max_n + 2)]
        self.parent = [-1] * (max_n + 2)
        self.edge_from_parent = [-1] * (max_n + 2)
        self.edge_to_parent = [-1] * (max_n + 2)

    def get_new_edge(self):
        for i in range(1, self.n + 1):
            for j in range(DOORS):
                if self.edge[i][j] == -1:
                    return i, j
        return -1, -1

    def path_to_edge(self, v):
        path = ""
        while v != 1:
            path += str(self.edge_from_parent[v])
            v = self.parent[v]
            # print(v)
        path = path[::-1]
        return path

    def find_backwards_edge(self, v):
        utils.print_green("Finding backwards edge")
        path = self.path_to_edge(v)
        for back_edge in range(DOORS):
            new_path = path + str(back_edge)
            res = utils.guess(new_path)
            self.letter[v] = res[-2]
            parent_letter = self.letter[self.parent[v]]
            if res[-1] != parent_letter and back_edge > 0:
                continue
            new_path2 = path[:-1] + "[" + str(utils.different(parent_letter)) + "]" + str(self.edge_from_parent[v]) + str(back_edge)
            res2 = utils.guess(new_path2)
            if res[-2] != res2[-2]:
                return -1
            if res[-1] == parent_letter and res2[-1] != parent_letter:
                return back_edge

    def traverse_for_repeats(self, v):
        utils.print_green("Traversing whole looking for a repeat")
        orgv = v
        path_te = self.path_to_edge(v)
        path_back = ""
        pocz_len = 0
        while v != 1:
            pocz_len += 1
            path_back += str(self.edge_to_parent[v])
            v = self.parent[v]

        order = []
        dfs_path = ""
        def dfs(v):
            nonlocal dfs_path
            order.append(v)
            for u, e in self.mst[v]:
                # print(v, u, e)
                # print(self.mst)
                dfs_path += str(e)
                dfs(u)
            if v != 1:
                order.append(self.parent[v])
                dfs_path += str(self.edge_to_parent[v])
        dfs(1)
        # print(path_te)
        # print(path_back)
        # print(dfs_path)
        path_sum = path_te + "[" + str(utils.different(self.letter[orgv])) + "]" + path_back + dfs_path
        res = utils.guess(path_sum)
        # print(path_sum)
        # print(dfs_path)
        # print(order)
        # print(res)
        # print(pocz_len)
        diff = 2 * pocz_len + 1
        for i in range(diff, len(res)):
            # print(order[i - diff])
            if self.letter[order[i - diff]] != res[i]:
                return order[i - diff]
        return -1
        

    def main_loop(self):
        while True:
            # Find a vertex and an edge
            v, e = self.get_new_edge()
            if v == -1:
                return
            utils.print_green("Looking at: " + str(v) + " " + str(e))
            # Add to mst
            self.parent[self.n + 1] = v
            self.edge_from_parent[self.n + 1] = e
            edge_back = self.find_backwards_edge(self.n + 1)
            self.edge_to_parent[self.n + 1] = edge_back

            if edge_back == -1:
                self.edge[v][e] = v
                continue

            # Traverse with modified value and try to union
            result = self.traverse_for_repeats(self.n + 1)
            if result == -1:
                utils.print_green("Adding new vertex")
                self.n += 1
                self.edge[v][e] = self.n
                self.edge[self.n][edge_back] = v
                self.mst[v].append((self.n, e))
            else:
                utils.print_green("Merging with: " + str(result))
                self.edge[v][e] = result
                self.edge[result][edge_back] = v
        # for v in range(self.n + 1):
        #     for e in range(6):
        #         print(v, e, self.edge[v][e])

    def answer(self):
        map = {
            "rooms": self.letter[1:-1],
            "startingRoom": 0,
            "connections": []
        }
        print(self.letter, map["rooms"])
        used = [[False] * 6 for _ in range(self.n + 1)]
        for v in range(1, self.n + 1):
            for e in range(6):
                to = self.edge[v][e]
                backdoor = 0
                for bd in range(6):
                    if self.edge[to][bd] == v and not used[to][bd]:
                        backdoor = bd
                        used[to][bd] = True
                        break
                map["connections"].append({
                    "from": {
                        "room": v-1,
                        "door": e
                    },
                    "to": {
                        "room": to-1,
                        "door": backdoor
                    }
                })
        return map


def main(n):
    if utils.prod:
        interface.select(PROBLEM_NAME)
    g = Graph(n)
    g.main_loop()
    # print(g.answer())
    if utils.prod:
        interface.guess(g.answer())

main(N)
