import random

import interface
import tasks

doors = [0, 1, 2, 3, 4, 5]

r = random.choices

class Query:
    def __init__(self, task = None):
        if task is None:
            task  = tasks.get_active_task()
        self.task = task
        self.N = task.N
        self.query_length = task.query_length
        self.query = None
        self.query_string = None
        self.response = None

        self.make_query()

    def make_query(self):
        q = []
        while len(q) < self.query_length:
            d = r(doors, [5, 5, 2, 2, 2, 2])[0]
            q.append(d)

        self.query = q
        self.query_string = ''.join([str(d) for d in q])
        assert len(self.query_string) == self.query_length

    def submit(self):
        assert len(self.query_string) == self.query_length

        j = interface.explore([self.query_string])
        results = j['results'][0]
        query_count = j['queryCount']

        self.response = results

        return query_count

def submit_batch(queries):
    if len(queries) == 0:
        return

    N = queries[0].N
    for q in queries:
        assert len(q.query_string) == q.query_length
        assert q.N == N

    j = interface.explore([q.query_string for q in queries])
    results = j['results']
    query_count = j['queryCount']
    for i, q in enumerate(queries):
        q.response = results[i]

    return query_count

if __name__ == '__main__':
    q = Query()
    print(q.query_string)
