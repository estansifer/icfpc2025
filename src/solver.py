import tasks
import query

class Key:
    def __init__(self, doors, labels):
        assert len(labels) == len(doors) + 1
        self.k = len(doors)
        self.doors = list(doors)
        self.labels = list(labels)
        x = 5 + labels[0]
        for i in range(self.k):
            x = x * 6
            x = x + doors[i]
            x = x * 4
            x = x + labels[i + 1]
        self.x = x

    def __hash__(self):
        return self.x

    def __eq__(self, other):
        return self.x == other.x

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        s = '(' + str(self.labels[0]) + ')'
        for i in range(self.k):
            s += ' ' + str(self.doors[i])
            s += ' (' + str(self.labels[i + 1]) + ')'
        return s

class Knowledge:
    def __init__(self, task = None):
        if task is None:
            task = tasks.get_active_task()
        self.task = task
        self.N = task.N
        self.queries = []
        self.len2key2pos = {}

    def submit_query(self):
        q = query.Query(self.task)
        query_count = q.submit()
        self.queries.append(q)
        print('Query count:', query_count)
        self.compute_key2pos(max_length = 3)

    def compute_key2pos(self, max_length = 1):
        self.len2key2pos = {}
        for l in range(1, max_length + 1):
            d = {}
            self.len2key2pos[l] = d
            for q in self.queries:
                n = q.query_length
                for i in range(n - l + 1):
                    k = Key(q.query[i : i + l], q.response[i : i + l + 1])
                    if not (k in d):
                        d[k] = []
                    d[k].append((q, i))

    def common_keys(self, l, most = 20):
        d = self.len2key2pos[l]
        xs = list(reversed(sorted(list(d.items()), key = lambda x : len(x[1]))))
        for x in xs[:most]:
            key, value = x
            print(key, ':', len(value))

k0 = Knowledge(tasks.task_list[0])
k = lambda : Knowledge()
