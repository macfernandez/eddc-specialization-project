import re
import requests
from typing import List, Tuple


def download_pdf(url: str, output: str) -> None:
    response = requests.get(url)
    with open(output, 'wb') as f:
        f.write(response.content)


def get_bibliography_list(file: str) -> Tuple[List[str], List[str]]:
    with open(file, 'r') as f:
        data = f.read()
    names = list(re.findall(r'\[([\W\w]+)\]', data))
    urls = list(re.findall(r'\((.*)\)', data))
    return zip(names, urls)


def preprocess_name(name: str) -> str:
    pattern = re.compile(r'.*?\d+\.([\W\w]+?\s){2}')
    name = pattern.search(name)
    if name:
        author, date, title = re.split(r'(\d+)', name.group())
        out = f'{date}_{preprocess_author(author)}_{preprocess_title(title)}.pdf'
        return out
    else:
        raise Exception(f'No match found for name {name}.')


def preprocess_author(author: str) -> str:
    author = re.sub(r'\,\s', '-', author)
    author = re.sub(r'[\.\,\s]', '', author)
    return author


def preprocess_title(title: str) -> str:
    title = re.sub(r'\W', ' ', title).title().replace(' ','')
    return title


if __name__ == '__main__':

    import os

    BIBLIOGRAPHY_FOLDER = 'bibliography'
    BIBLIOGRAPHY_FILE = os.path.join(BIBLIOGRAPHY_FOLDER, 'README.md')

    
    bibliography = get_bibliography_list(BIBLIOGRAPHY_FILE)

    for name, url in bibliography:
        name = preprocess_name(name)
        output = os.path.join(BIBLIOGRAPHY_FOLDER, name)
        download_pdf(url, output)
