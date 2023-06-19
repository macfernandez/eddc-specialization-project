import os
import re
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_text


def convert_pdf2txt(path: str, out_file: str=None) -> str:
    out_file = out_file if out_file else path.replace('.pdf', '.txt')
    text = extract_text(path)
    with open(out_file, 'w') as f:
        _ = f.write(text)
    return out_file


def remove_header(text: str) -> str:
    header = re.compile(
        r'''(
            29\/30 de diciembre de 2020|                # date
            Sesión especial|                            # special session
            “2020 \- Año del General Manuel Belgrano”|  # commemoration
            Pág\. \d+                                   # page
            )''',
        re.X
    )
    return header.sub('', text)


def remove_footer(text: str) -> str:
    footer = re.compile(
        r'Dirección General de Taquígrafos'
    )
    return footer.sub('', text)


def split_attendees(text: str) -> str:
    attendees = re.compile(r'(.*?)(ÍNDICE.*)', re.DOTALL)
    _groups = attendees.search(text)
    return _groups.group(1), _groups.group(2)


def extract_attendees(text: str) -> str:
    attendees, text = split_attendees(text)
    return text
    

def remove_special_chars(text: str, *args) -> str:
    chars = re.compile(r'[]')
    return chars.sub('', text)


def preprocess(path: str, out_file: str=None) -> str:
    out_file = out_file if out_file else path.replace('.txt', '_prep.txt')
    with open(path, 'r') as f:
        text = f.read()
    text = remove_special_chars(text)
    text = remove_header(text)
    text = remove_footer(text)
    text = extract_attendees(text)
    with open(out_file, 'w') as f:
        _ = f.write(text)

