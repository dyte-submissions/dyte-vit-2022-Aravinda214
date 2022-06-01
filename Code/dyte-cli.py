import argparse
import pandas as pd
import requests
import base64
import json


def github_read_file(username, repository_name, file_path):
    url = f'https://api.github.com/repos/{username}/{repository_name}/contents/{file_path}'
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    file_content = data['content']
    file_content_encoding = data.get('encoding')
    if file_content_encoding == 'base64':
        file_content = base64.b64decode(file_content).decode()

    return file_content

def version_check(gitLink,package,version):
    github_token = ""
    user_repo = gitLink.split('/')[3:]
    username = user_repo[0]
    repository_name = user_repo[1]
    file_path = 'package.json'

    file_content = github_read_file(username, repository_name, file_path)
    data = json.loads(file_content)
    #print(data)
    #print(type(data))

    PackVer = data['dependencies'][package][1:]

    if PackVer>=version:
        return True
    else:
        return False

def get_version(gitLink,package,version):
    user_repo = gitLink.split('/')[3:]
    username = user_repo[0]
    repository_name = user_repo[1]
    file_path = 'package.json'

    file_content = github_read_file(username, repository_name, file_path)
    data = json.loads(file_content)
    #print(data)
    #print(type(data))

    PackVer = data['dependencies'][package][1:]
    return PackVer


def repo_PR(gitLink,version_satisfied):
    if version_satisfied:
        return

    user_repo = gitLink.split('/')[3:]
    username = user_repo[0]
    repository_name = user_repo[1]
    file_path = 'package.json'

    token = "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"

    headers = {
    "Authorization" : "token "+token,
    "Accept" : "application/vnd.github.v3+json"
    }

    url = "https://api.github.com/repos/{}/{}/forks".format(username,repository_name)
    response = requests.post(url,headers=headers)

    newrepo = response.text['full_name']

    from github import Github

    token = "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"

    api = Github(token)
    site = api.get_repo('Aravinda214/'+repository_name)

    index_file = site.get_contents('package.json')
    index_content = base64.b64decode(index_file.content).decode("utf-8") 

    updated_content = index_content.replace('"axios": "^0.21.1"','"axios": "^0.23.0",')

    print(site.update_file(
        path='package.json',
        message='Updated Dependencies',
        content=updated_content,
        sha=index_file.sha
    ))



def main():
    parser = argparse.ArgumentParser(description='SDK Tooling Challenge - Node Packages Version Check')
    parser.add_argument('-i','--input', metavar='FILE', type=str, help="CSV of File Repos", required=True)
    parser.add_argument('PACKAGE', help="Package and Version in format P@V")
    #parser for PR [-U]

    args = parser.parse_args()
    package_ver = args.PACKAGE.split('@')

    df = pd.read_csv(args.input)
    df['version'] = df.apply(lambda row: get_version(row.repo,package_ver[0],package_ver[1]), axis=1)
    df['version_satisfied'] = df.apply(lambda row: version_check(row.repo,package_ver[0],package_ver[1]), axis=1)
    print(df)


    # df.apply(lambda row: repo_PR(row.repo,row.version_satisfied), axis=1)


    filename = 'output_' + args.input
    df.to_csv(filename,index=False)

    print("\n\nOutput saved as",filename)




if _name_ == '_main_':
    main()
