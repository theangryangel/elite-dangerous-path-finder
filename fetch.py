import requests
import json

print 'Fetching EDSC systems...'

data = {
        'data': {
            'ver':2, 'test': True, 'outputmode': 2,
                'filter':{
                    'knownstatus':0,
                    'date':"2013-09-01 12:34:56"
                }
            }
        }

r = requests.post('http://edstarcoordinator.com/api.asmx/GetSystems',json=data)

print 'Saving...'

with open('response.json', 'w') as outfile:
    json.dump(r.json(), outfile)

print 'Job\'s done!'
