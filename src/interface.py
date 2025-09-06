import requests
import time

import secr
import tasks

url = 'https://31pwr5t6ij.execute-api.eu-west-2.amazonaws.com/'

headers =  {
        # 'User-Agent' : 'blah blah',
        "Content-Type":"application/json",
        # "Authorization": f"Bearer {secr.token}"
    }

def get(endpoint, **params):
    time.sleep(1)
    r = requests.get(url + endpoint, data = params, headers = headers)
    j = r.json()
    return j

def post(endpoint, j):
    time.sleep(1)
    print(f"Posting {j} to {endpoint}")
    r = requests.post(url + endpoint, json = j, headers = headers)
    j = r.json()
    print("Result:")
    print(j)
    return j

def register():
    return False
    params = {
            'name' : 'House of Lambdas',
            'pl' : 'python',
            'email' : 'eric.stansifer+icfpc@gmail.com'
        }
    j = post('register', params)
    print(j)

def select(problem_name):
    params = {
            'id' : secr.user_id,
            'problemName' : problem_name
        }
    j = post('select', params)
    with open('current_task_mutex', 'w') as f:
        f.write(problem_name + '\n')
    assert j['problemName'] == problem_name

# Returns:
# {results : [[int]], queryCount : int}
def explore(plans):
    params = {
            'id' : secr.user_id,
            'plans' : plans
        }
    j = post('explore', params)
    return j

def guess(map):
    params = {
            'id' : secr.user_id,
            'map' : map
        }
    j = post('guess', params)
    return j['correct']

if __name__ == '__main__':
    pass
    # register()
    # select(tasks.task_list[0][0])
    # explore(['0123423123021403240'])
