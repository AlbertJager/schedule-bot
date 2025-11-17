import requests
import base64
import json

GITHUB_TOKEN = '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'
REPO_OWNER = 'AlbertJager'
REPO_NAME = 'schedule-bot'
FILE_PATH = 'users.json'
BRANCH = 'main'

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_file_sha():
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['sha']
    return None

def update_file(content_str, sha=None):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
    content_encoded = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
    data = {
        'message': 'Автоматическое обновление данных JSON',
        'content': content_encoded,
        'branch': BRANCH,
    }
    if sha:
        data['sha'] = sha
    response = requests.put(url, headers=headers, json=data)
    return response.json()

if __name__ == '__main__':
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        file_content = f.read()

    sha = get_file_sha()
    result = update_file(file_content, sha)
    print(result)
