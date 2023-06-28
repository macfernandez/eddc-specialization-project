import os
import re
from typing import List
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
        r'''(29\/30 de diciembre de 2020|Sesión especial|\“2020 \- Año del General Manuel Belgrano\”|Pág\. \d+)'''
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
    return attendees, text
    

def remove_special_chars(text: str, *args) -> str:
    chars = re.compile(r'[]')
    return chars.sub('', text)


def find_roles(texts: List[str]):
    idx, roles = list(), list()
    for i, line in enumerate(texts):
        if ':' in line:
            rol = re.search(r'(.*?)\:', line).group(1)
            roles.append(rol)
            idx.append(i)
    return idx, roles

def postprocess_name(text: str) -> str:
    title_pattern = re.compile(r'(DOCTOR|SENADOR|SEÑOR)A?')
    name = title_pattern.sub('', text)
    if ',' in name:
        lastname, firstname = re.split(r'\,', name)
        name = re.sub(r'\s+', ' ', f'{firstname} {lastname}')
    return name.strip().title()

def postprocess_attendees(text: str) -> str:
    lines = text.split('\n')
    roles_idx, roles = find_roles(lines)
    output_file = os.path.join('data', 'attendees.csv')
    f = open(output_file, 'w')
    for line in lines[min(roles_idx):]:
        idx = lines.index(line)
        line = line.strip()
        if line != '':
            if ':' in line:
                rol, name = line.split(':')
                if name != '':
                    _ = f.write(f'{rol}|{postprocess_name(name)}\n')
            else:
                next_roles = [i for i in roles_idx if i > idx]
                rol_id = min(next_roles) if next_roles else max(roles_idx)
                rol_pos = roles_idx.index(rol_id)
                rol = roles[rol_pos-1] if next_roles else roles[rol_pos]
                if re.search(r'\bY\b', line):
                    names = re.split(r'[Y,]', line)
                    for name in names:
                        if name.strip() != '':
                            _ = f.write(f'{rol}|{postprocess_name(name)}\n')
                else:
                    _ = f.write(f'{rol}|{postprocess_name(line)}\n')
    return output_file


def select_section(text: str):
    section = re.compile(
        r"6\.\s+ Regulación del acceso a la interrupción voluntaria del embarazo y a la \n+atención postaborto \(O\.D\. N\° 716\/20\.\)(.*)8\.\s+Apéndice",
        re.DOTALL
    )
    section_text = section.search(text)
    if section_text:
        return section_text.group(1).strip()
    else:
        return None

def speaker(text):
    #speaker = re.compile(r"((Sra?\.)?.*?\.\-)", re.I)
    text = re.sub(r"(\n\s?)+", r"\n", text)
    speaker = re.compile(r"([^\n].*?\.\-)", re.I)
    speakers = speaker.split(text)
    with open("data/speakers.txt","w") as f:
        _ = f.write(f"\n{'-'*80}\n".join(speakers))


def preprocess(path: str, out_file: str=None) -> str:
    out_file = out_file if out_file else path.replace('.txt', '_prep.txt')
    with open(path, 'r') as f:
        text = f.read()
    text = remove_special_chars(text)
    text = remove_header(text)
    text = remove_footer(text)
    attendees, text = extract_attendees(text)
    _ = postprocess_attendees(attendees)
    text = select_section(text)
    speaker(text)
    with open(out_file, 'w') as f:
        _ = f.write(text)
    

preprocess('data/session_29-12-2020.txt')
#<?xml version="1.0" encoding="UTF-8"?>
