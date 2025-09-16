import requests
import sys
from datetime import datetime

def return_response(arg, runtime = False):
    url = 'http://69.197.139.26:5000/generate'
    data = {'prompt': arg}
    headers = {
        "Authorization": f"Bearer @#$#234RAIN##SHINE$$INTHE$$CLUB"
    }
    
    if runtime:
        start_time = datetime.now()
        response = requests.post(url, json=data, headers=headers)
        end_time = datetime.now()
        duration = end_time - start_time
        return (response.json()["text"], duration)
    else:
        response = requests.post(url, json=data, headers=headers)
        return response.json()["text"]

if __name__ == "__main__":
    arg = sys.argv[1]

    response = return_response(arg, runtime = True)
    print(response[0])
    print(f"Runtime: {response[1].total_seconds()} seconds")