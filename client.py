#!/Users/maz/venv/blogpostcorniceapp/bin/python


import simplejson as json
import requests

task = {
    'name': 'take_out_the_trash',
    'description': ("empty the trashcan and put the bag in the outside trashcan, "
        "don't forget to put a new bag in!"),
    }
 
response = requests.get('http://localhost:6543/tasks')
print(response.status_code, response.text)
response = requests.post('http://localhost:6543/tasks', json.dumps(task))
print(response.status_code, response.text)
response = requests.get('http://localhost:6543/tasks')
print(response.status_code, response.text)



