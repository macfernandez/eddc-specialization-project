import os
import re
from typing import List
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_text

from src.utils import save_csv, save_xml


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

def postprocess_speaker(speaker: str) -> str:
    name_pattern = re.compile(r"\((.*)\)")
    name = name_pattern.search(speaker)
    if name:
        name = name.group(1)
    else:
        name = speaker
    speaker = re.sub(r"(Sra?\.|\.\-)", "", name)
    return speaker.strip()

def postprocess_attendees(text: str) -> str:
    attendees = list()
    lines = text.split('\n')
    roles_idx, roles = find_roles(lines)
    for line in lines[min(roles_idx):]:
        idx = lines.index(line)
        line = line.strip()
        if line != '':
            if ':' in line:
                rol, name = line.split(':')
                if name != '':
                    attendees.append([rol,postprocess_name(name)])
            else:
                next_roles = [i for i in roles_idx if i > idx]
                rol_id = min(next_roles) if next_roles else max(roles_idx)
                rol_pos = roles_idx.index(rol_id)
                rol = roles[rol_pos-1] if next_roles else roles[rol_pos]
                if re.search(r'\bY\b', line):
                    names = re.split(r'[Y,]', line)
                    for name in names:
                        if name.strip() != '':
                            attendees.append([rol,postprocess_name(name)])
                else:
                    attendees.append([rol,postprocess_name(line)])
    return attendees


def split_comments(text: str) -> list:
    comments = list()
    comment_pattern = re.compile(r"(–[A-Z].*[\d\.:])")
    comment_match = comment_pattern.findall(text)
    if comment_match:
        cm_pattern = list(map(re.escape,comment_match))
        cm_pattern = f"({'|'.join(cm_pattern)})"
        comment = re.split(rf"{cm_pattern}", text)
        for cm in comment:
            if cm in comment_match:
                comments.append((False, cm))
            else:
                comments.append((True, cm))
    else:
        comments.append((True, text))
    return comments

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

def split_speech(text):
    text = re.sub(r"(\n\s?)+", r"\n", text)
    speaker_pattern = re.compile(r"([^\n].*?\.\-)", re.I)
    discourse = speaker_pattern.split(text)
    discourse = list(filter(lambda x: re.search(r"^\s*$", x) is None, discourse))
    speaker_speech = list()
    for i in range(0, len(discourse)-1, 2):
        speaker, speech = discourse[i], split_comments(discourse[i+1])
        for s in speech:
            is_speech = s[0]
            content = s[1]
            data = {"speaker": None, "content": content.strip(),"speech": is_speech}
            if is_speech:
                data.update({"speaker": postprocess_speaker(speaker)})
            speaker_speech.append(data)
    return speaker_speech


def preprocess(path: str, out_csv: str=None, out_xml: str=None) -> str:
    out_csv = out_csv if out_csv else path.replace(".txt", "_attendees.csv")
    out_xml = out_xml if out_xml else path.replace(".txt", "_discourse.xml")
    with open(path, 'r') as f:
        text = f.read()
    text = remove_special_chars(text)
    text = remove_header(text)
    text = remove_footer(text)
    attendees, text = extract_attendees(text)
    attendees = postprocess_attendees(attendees)
    _ = save_csv(attendees, out_csv)
    text = select_section(text)
    discourse = split_speech(text)
    _ = save_xml(discourse, out_xml)
    return out_csv, out_xml
