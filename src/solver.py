import tasks
import query
import utils

class NodeInfo:
    def __init__(self, visits, max_forward = 5):
        self.visits = list(visits)
        assert len(visits) > 0
        self.label = visits[0].label
        for v in visits:
            assert v.label == self.label

        # [NodeInfo | None]
        self.neighbors = [None] * 6

        self.consistent = True
        # path -> labels | set[labels]
        # paths and labels are stored as IntLists
        signature = {}
        for v in visits:
            for path, labels in v.all_forward_path_and_labels(max_forward):
                if path in signature:
                    if type(signature[path]) is set:
                        signature[path].add(labels)
                    else:
                        # it is an IntList. Change to a set of IntLists
                        if signature[path] != labels:
                            self.consistent = False
                            signature[path] = {signature[path], labels}
                else:
                    signature[path] = labels
        self.signature = signature

class Knowledge:
    def __init__(self, task = None):
        if task is None:
            task = tasks.get_active_task()
        self.task = task
        self.N = task.N
        self.queries = []
        self.visits = []
        self.pl2visits = {}
        self.pl2node = {}

    def submit_query(self, q = None):
        if q is None:
            q = query.Query(self.task)
        query_count = q.submit()
        self.queries.append(q)
        self.visits.extend(q.visits)
        print('Query count:', query_count)
        self.compute_pl2node(max_length = 4)

    def compute_pl2node(self, max_length = 4):
        self.pl2visits = {}
        for v in self.visits:
            for path, labels in v.all_forward_path_and_labels(max_length):
                pl = utils.PathWithLabels(path, labels)
                if pl in self.pl2visits:
                    self.pl2visits[pl].append(v)
                else:
                    self.pl2visits[pl] = [v]

        self.pl2node = {}
        for pl, visits in self.pl2visits.items():
            self.pl2node[pl] = NodeInfo(visits, max_forward = 3)

    def common_pl(self, most = 20):
        xs = list(reversed(sorted(list(self.pl2node.items()), key = lambda x : len(x[1].visits))))
        for x in xs[:most]:
            pl, node_info = x
            print(pl, ':')
            print('    consistent', node_info.consistent)
            print('    signature:')
            print(node_info.signature)

k0 = Knowledge(tasks.task_list[0])
k = lambda : Knowledge()
