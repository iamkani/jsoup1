import os, time, requests


api_url = 'http://205.174.165.75:9380/api'
username = os.getenv('CYDARIEN_USERNAME')
password = os.getenv('CYDARIEN_PASSWORD')
host = os.getenv('REPOSITORY_HOST')
repo = os.getenv('REPOSITORY_PATH')
commit = os.getenv('COMMIT_SHA')
headers = {}
project_id = None
analysis_id = None

def authenticate():
    global headers
    response = requests.post(f'{api_url}/users/login/', data={
        'username': username, 'password': password
    })
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print('############  AUTHENTICATION FAILED!  ############')
        print(response.json()['detail'])
        print('##################################################')
        exit(1)
    headers = {'Authorization': f'Bearer {response.json()["access"]}'}

def get_project_id():
    global project_id
    response = requests.post(f'{api_url}/users/self/projects/by_path/',
        headers=headers,
        data={
            'host': host,
            'repo': repo,
        })
    if response.status_code != 200:
        print(response.json()['detail'])
        exit(1)
    project_id = response.json()['id']

def initiate_analysis():
    global analysis_id
    response = requests.post(f'{api_url}/users/self/git/',
        headers=headers,
        data={
            'project': project_id,
            'commit': commit
        })
    analysis_id = response.json()['analysis']

def start_polling():
    while True:
        response = requests.get(f'{api_url}/users/self/analyses/{analysis_id}', headers=headers)
        data = response.json()
        if data['total_crashes'] > 0:
            response = requests.get(f'{api_url}/analyses/{analysis_id}/crashes', headers=headers)
            for crash in response.json():
                print(crash['stackTrace'])
                print('Found crashes visit https://fuzzer.cydarien.com to download crashes.')
                exit(1)
        if data['status'] == 'T':
            exit(0)
        time.sleep(30)

if __name__ == "__main__":
    authenticate()
    get_project_id()
    initiate_analysis()
    start_polling()
