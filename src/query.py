import random

import interface
import tasks

r = random.choices

class Door:
    def __init__(self, d):
        self.d = d
        self.is_door = True

    def __str__(self):
        return str(self.d)

doors = [Door(d) for d in range(6)]

class Mark:
    def __init__(self, m):
        self.m = m
        self.is_door = False

    def __str__(self):
        return f'[{self.m}]'

class Query:
    def __init__(self, task = None):
        if task is None:
            task  = tasks.get_active_task()
        self.task = task
        self.N = task.N
        self.query_length = task.query_length

        self.query = None
        self.query_doors_only = None
        self.query_string = None
        self.response = None

        self.random_query1()

    def custom_query(self, actions, trim_if_too_long = True, error_if_too_short = True):
        self.query = list(actions)
        if trim_if_too_long:
            self.query = self.query[:self.query_length]
        if error_if_too_short:
            assert len(self.query) == self.query_length

        self.query_doors_only = [q for q in self.query if q.is_door]

        self.query_string = ''.join([str(act) for act in self.query])

    def random_query1(self):
        q = []
        while len(q) < self.query_length:
            d = r(doors, [5, 5, 2, 2, 2, 2])[0]
            q.append(d)

        self.custom_query(q)

    def parse_response(self, response):
        self.raw_response = response
        assert len(self.query) + 1 == len(self.raw_response)

        # Only keep responses to movements, not markings
        self.response = [response[0]]
        for i in range(len(self.query)):
            if self.query[i].is_door:
                self.response.append(response[i + 1])

        assert len(self.query_doors_only) + 1 == len(self.response)

    def submit(self):
        j = interface.explore([self.query_string])
        results = j['results'][0]
        query_count = j['queryCount']

        self.parse_response(results)

        return query_count

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
    q = Query()
    print(q.query_string)
    q.custom_query([Door(0), Mark(3), Door(1)], error_if_too_short = False)
    print(q.query_string)
