import random

import interface
import tasks
import utils

r = random.choices

class Door:
    def __init__(self, d):
        self.d = d
        self.is_door = True
    
    def __int__(self):
        return self.d

    def __str__(self):
        return str(self.d)
    
doors = [Door(d) for d in range(6)]

class Mark:
    def __init__(self, m):
        self.m = m
        self.is_door = False
    
    def __int__(self):
        return self.m

    def __str__(self):
        return f'[{self.m}]'

marks = [Mark(m) for m in range(4)]

# Represents a specific node visited at a specific time within a specific expedition
class Visit:
    # q: Query
    # index: number of doors previously traversed
    def __init__(self, q, index):
        self.query = q
        self.index = index
        assert (index >= 0) and (index <= q.n)

        self.label = q.response[index]
        self.prev = None # Visit
        self.next = None # Visit

        self.forwards = self.all_forward_path_and_labels(5)

    def ahead(self, k):
        if k == 0:
            return self
        if k > 0:
            return self.next.ahead(k - 1)
        if k < 0:
            return self.prev.ahead(k + 1)

    # Go forwards an additional l steps, returns (path, labels)
    def forward_path_and_labels(self, l):
        i = self.index
        if i + l > self.query.n:
            return None
        path = utils.IntList(self.query.query_doors_only[i : i + l])
        labels = utils.IntList(self.query.response[i : i + l + 1])
        return (path, labels)

    def all_forward_path_and_labels(self, max_length):
        result = []
        for l in range(1, max_length + 1):
            if self.index + l > self.query.n:
                break
            result.append(self.forward_path_and_labels(l))
        return result

class Query:
    def __init__(self, task = None):
        if task is None:
            task  = tasks.get_active_task()
        self.task = task
        self.N = task.N
        self.query_length = task.query_length

        # number of door transitions in the query
        self.n = None                                
        # sequence of actions
        self.query = None
        # sequence of actions, excluding markings
        self.query_doors_only = None
        # converted to string for sending to server
        self.query_string = None
        # sequence of ints returned by server
        self.raw_response = None
        # sequence of ints returned by server, excluding markings
        self.response = None
        # sequence of Visit
        self.visits = None

        self.random_query1()

    def custom_query(self, actions, trim_if_too_long = True, error_if_too_short = True):
        self.query = list(actions)
        if trim_if_too_long:
            self.query = []
            num_doors = 0
            for act in actions:
                if act.is_door:
                    num_doors += 1
                if num_doors > self.query_length:
                    break

                self.query.append(act)
        else:
            self.query = list(actions)

        self.query_doors_only = [act for act in self.query if act.is_door]
        self.n = len(self.query_doors_only)
        if error_if_too_short:
            assert self.n == self.query_length
        else:
            assert self.n <= self.query_length

        self.query_string = ''.join([str(act) for act in self.query])

        return self

    def random_query0(self):
        q = []
        while len(q) < self.query_length:
            d = r(doors)[0]
            q.append(d)

        return self.custom_query(q)

    def random_query1(self):
        q = []
        while len(q) < self.query_length:
            d = r(doors, [5, 5, 2, 2, 2, 2])[0]
            q.append(d)

        return self.custom_query(q)

    def random_query2(self):
        q = []
        while len(q) < self.query_length:
            if random.random() < 0.2:
                q.append(r(doors)[0])
                while random.random() < 0.1:
                    q.append(r(doors)[0])

            if random.random() < 0.5:
                q.append(doors[0])
                q.append(doors[1])
            else:
                q.append(doors[1])
                q.append(doors[0])

        return self.custom_query(q)

    def parse_response(self, response):
        self.raw_response = response
        assert len(self.query) + 1 == len(self.raw_response)

        # Only keep responses to movements, not markings
        self.response = [response[0]]
        for i in range(len(self.query)):
            if self.query[i].is_door:
                self.response.append(response[i + 1])

        assert self.n + 1 == len(self.response)

        self.visits = [Visit(self, i) for i in range(self.n + 1)]
        for i in range(self.n):
            self.visits[i].next = self.visits[i + 1]
            self.visits[i + 1].prev = self.visits[i]

    def submit(self):
        j = interface.explore([self.query_string])
        results = j['results'][0]
        query_count = j['queryCount']

        self.parse_response(results)

        return query_count

def base4(x, ndigits):
    digits = [0] * ndigits
    for i in range(ndigits):
        digits[i] = x % 4
        x = (x // 4)
    if x > 0:
        return None
    return digits

def parallel_queries(task = None, k = 4):
    if task is None:
        task = tasks.get_active_task()
    cur_id = 1
    actions = [[] for i in range(k)]
    path = r(doors, k = task.query_length)
    for d in path:
        code = base4(cur_id, k)
        cur_id += 1
        if (not (code is None)) and len(set(code)) == 1:
            code = base4(cur_id, k)
            cur_id += 1

        for i in range(k):
            actions[i].append(d)
            if not (code is None):
                actions[i].append(marks[code[i]])

    queries = [Query(task).custom_query(a) for a in actions]
    return queries

def submit_batch(queries):
    if len(queries) == 0:
        return

    j = interface.explore([q.query_string for q in queries])
    results = j['results']
    query_count = j['queryCount']
    for i, q in enumerate(queries):
        q.parse_response(results[i])

    return query_count

if __name__ == '__main__':
    qs = parallel_queries(k = 3)
    for q in qs:
        print(q.query_string)

    # q = Query()
    # print(q.query_string)
    # q.custom_query([Door(0), Mark(3), Door(1)], error_if_too_short = False)
    # print(q.query_string)
    # q.random_query2()
    # print(q.query_string)
