import os
import re
import bs4 as bs
import numpy as np
import pandas as pd
from string import punctuation


def assign_speech(speaker: str, speech: bs.BeautifulSoup) -> list:
    discourse = speech.find_all("discourse", {"speech":"true", "speaker":speaker})
    text = list(map(lambda x: x.text, discourse))
    return text


def calculate_univariant_metrics(x: pd.Series) -> tuple[float, float, float]:
    mean = np.mean(x)
    median = np.median(x)
    std = np.std(x)
    return mean, median, std


def count_tokens(text: str, unique: bool=False) -> int:
    tokens = text.split()
    if unique:
        tokens = set(tokens)
    return len(tokens)


def match_senator_name(senator: str, speakers: list) -> list:
    senator = set(preprocess_name(senator).split())
    speakers_prep = list(map(lambda x: set(x.split()), speakers))
    speaker = list(filter(lambda x: x.issubset(senator), speakers_prep))
    senator_idx = [speakers_prep.index(s) for s in speaker]
    senator = [speakers[i] for i in senator_idx]
    return senator


def preprocess_name(name: str) -> str:
    name = name.lower()
    name = name.translate(
        str.maketrans("áéíóúàèìòùäëïöü","aeiou"*3)
    )
    name = remove_punctuation(name)
    tokens = sorted(name.split())
    return " ".join(tokens)


def preprocess_text(text: str) -> str:
    text = text.lower()
    text = remove_punctuation(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def remove_punctuation(x: str) -> str:
    return re.sub(rf"[{punctuation}]", "", x)

def save_dataframe(
    dataframe: pd.DataFrame, folder: str, filename: str, latex: bool=True
) -> None:
    file_path = os.path.join(folder, filename)
    dataframe.to_csv(f"{file_path}.csv", index=False)
    if latex:
        dataframe.to_latex(f"{file_path}.tex", index=False)