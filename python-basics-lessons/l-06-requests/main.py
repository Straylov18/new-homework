import requests
import json

url = 'https://api.data.gov/ed/collegescorecard/v1/schools?api_key=DEMO_KEY&fields=id%2Cname%2Clocation%2Cstudent.size'

response = requests.get(url)

print(response.status_code)
print(json.dumps(response.json(), indent=4))
# print(response.json())
