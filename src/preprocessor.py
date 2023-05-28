import os
import subprocess


def convert_pdf2txt(path: str, out_file: str=None) -> str:
    out_file = out_file if out_file else name.replace('.pdf', '.txt')
    subprocess.call(f'pdf2txt.py -o {out_file} {path}', shell=True)
    return out_file