import re
from typing import List, Dict, Tuple

from pdfminer.high_level import extract_text

from src.utils import save_csv, save_xml
from src.preprocessor.patterns import HEADER, FOOTER, CHARS


def convert_pdf2txt(path: str, out_file: str=None) -> str:
    out_file = out_file if out_file else path.replace('.pdf', '.txt')
    text = extract_text(path)
    with open(out_file, 'w') as f:
        _ = f.write(text)
    return out_file


def find_roles(texts: List[str]) -> Tuple[List[int],List[str]]:
    idx, roles = list(), list()
    for i, line in enumerate(texts):
        if ':' in line:
            rol = re.search(r'(.*?)\:', line).group(1)
            roles.append(rol)
            idx.append(i)
    return idx, roles


def split_attendees(text: str) -> Tuple[str,str]:
    attendees = re.compile(r'(.*?)(ÍNDICE.*)', re.DOTALL)
    _groups = attendees.search(text)
    return _groups.group(1), _groups.group(2)


def split_comments(text: str) -> List[Tuple[bool,str]]:
    comments = list()
    comment_pattern = re.compile(r"(–[A-Z].*[\d\.:])")
    comment_match = comment_pattern.findall(text)
    if comment_match:
        cm_pattern = list(map(re.escape,comment_match))
        cm_pattern = f"({'|'.join(cm_pattern)})"
        comment = re.split(rf"{cm_pattern}", text)
        for cm in comment:
            if cm in comment_match:
                comments.append((True, cm))
            else:
                comments.append((False, cm))
    else:
        comments.append((False, text))
    return comments


def split_speech(text: str) -> List[Dict[str,str]]:
    text = re.sub(r"(\n\s?)+", r"\n", text)
    speaker_pattern = re.compile(r"([^\n].*?\.\-)", re.I)
    discourse = speaker_pattern.split(text)
    discourse = list(filter(lambda x: re.search(r"^\s*$", x) is None, discourse))
    speaker_speech = list()
    for i in range(0, len(discourse)-1, 2):
        speaker, speech = discourse[i], split_comments(discourse[i+1])
        for s in speech:
            is_comment = s[0]
            content = s[1].strip()
            if content == "":
                continue
            data = {
                "speaker": "none",
                "content": postprocess_content(content),
                "speech": str(not(is_comment)).lower()
            }
            if not is_comment:
                data.update({"speaker": postprocess_speaker(speaker)})
            speaker_speech.append(data)
    return speaker_speech


def postprocess_attendees(text: str) -> List[List[str]]:
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
                last_rol_line = max([i for i in roles_idx if i < idx])
                rol_pos = roles_idx.index(last_rol_line)
                rol = roles[rol_pos]
                if re.search(r'\bY\b', line):
                    names = re.split(r'[Y,]', line)
                    for name in names:
                        if name.strip() != '':
                            attendees.append([rol,postprocess_name(name)])
                else:
                    attendees.append([rol,postprocess_name(line)])
    return attendees


def postprocess_content(text: str) -> str:
    text = re.sub(r"[\n\s\t]+", " ", text)
    text = re.sub(r"–", "-", text)
    return text


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
    speaker = re.sub(r"\s+", " ", speaker).strip()
    return speaker


def remove_pattern(pattern: str, text: str) -> str:
    pattern = re.compile(pattern)
    return pattern.sub('', text)


def select_section(text: str) -> str:
    section = re.compile(
        r"6\.\s+ Regulación del acceso a la interrupción voluntaria del embarazo y a la \n+atención postaborto \(O\.D\. N\° 716\/20\.\)(.*)8\.\s+Apéndice",
        re.DOTALL
    )
    section_text = section.search(text)
    if section_text:
        return section_text.group(1).strip()
    else:
        return None


def preprocess(path: str, out_csv: str=None, out_xml: str=None) -> str:
    out_csv = out_csv if out_csv else path.replace(".txt", "_attendees.csv")
    out_xml = out_xml if out_xml else path.replace(".txt", "_discourse.xml")
    with open(path, 'r') as f:
        text = f.read()
    for pattern in [HEADER, FOOTER, CHARS]:
        text = remove_pattern(pattern, text)
    attendees, text = split_attendees(text)
    attendees = postprocess_attendees(attendees)
    _ = save_csv(attendees, out_csv)
    text = select_section(text)
    discourse = split_speech(text)
    _ = save_xml(discourse, out_xml)
    return out_csv, out_xml
