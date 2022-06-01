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

def main():
    parser = argparse.ArgumentParser(description='SDK Tooling Challenge - Node Packages Version Check')
    parser.add_argument('-i','--input', metavar='FILE', type=str, help="CSV of File Repos", required=True)
    parser.add_argument('PACKAGE', help="Package and Version in format P@V")
    #parser for PR [-U]

    args = parser.parse_args()
    package_ver = args.PACKAGE.split('@')

    df = pd.read_csv(args.input)
    df['version_satisfied'] = df.apply(lambda row: version_check(row.repo,package_ver[0],package_ver[1]), axis=1)
    print(df)

    filename = 'output_' + args.input
    df.to_csv(filename,index=False)

    print("\n\nOutput saved as",filename)


if __name__ == '__main__':
    main()
