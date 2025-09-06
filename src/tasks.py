class Task:
    def __init__(self, name, N, k, mirrors):
        self.name = name
        self.N = N
        self.query_length = N * k
        self.mirrors = mirrors

task_list = [
        Task('probatio', 3, 18, 1),
        Task('primus', 6, 18, 1),
        Task('secundus', 12, 18, 1),
        Task('tertius', 18, 18, 1),
        Task('quartus', 24, 18, 1),
        Task('quintus', 30, 18, 1),
        Task('aleph', 12, 6, 2),
        Task('beth', 24, 6, 2),
        Task('gimel', 36, 6, 2),
        Task('daleth', 48, 6, 2),
        Task('he', 60, 6, 2),
        Task('vau', 18, 6, 3),
        Task('zain', 36, 6, 3),
        Task('hhet', 54, 6, 3),
        Task('teth', 72, 6, 3),
        Task('iod', 90, 6, 3)
    ]

def get_task_by_name(name):
    for t in task_list:
        if t.name == name:
            return t
    print('No such task found:', name)

def get_active_task():
    with open('current_task_mutex', 'r') as f:
        name = f.read().strip()
        return get_task_by_name(name)
