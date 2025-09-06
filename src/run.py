import sys
import os

import interface
import query
import tasks

def run():
    t = tasks.task_list[0]
    q = query.Query(t)
    print(q.query_string)

if __name__ == '__main__':
    run()
