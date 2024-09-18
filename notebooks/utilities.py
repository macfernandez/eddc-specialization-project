from copy import deepcopy
import math
import os
import re
from string import punctuation

import bs4 as bs
import matplotlib.pyplot as plt
from nltk import stem
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import BaseEstimator
from sklearn.preprocessing import MinMaxScaler
import spacy


STEMMER = stem.SnowballStemmer("spanish")
SPACY_MODEL = spacy.load("es_core_news_md")


def assign_speech(speaker: str, speech: bs.BeautifulSoup) -> list:
    discourse = speech.find_all("discourse", {"speech":"true", "speaker":speaker})
    text = list(map(lambda x: x.text, discourse))
    return text


def calculate_univariant_metrics(x: pd.Series, round_: float=None) -> tuple[float, float, float]:
    mean = np.mean(x)
    median = np.median(x)
    std = np.std(x)
    if round:
        mean, median, std = (
            round(mean, round_), round(median, round_), round(std, round_)
        )
    return mean, median, std


def count_tokens(text: str, unique: bool=False) -> int:
    tokens = text.split()
    if unique:
        tokens = set(tokens)
    return len(tokens)


def map_inf(x: float, min_value: float, max_value: float) -> float:
    if x == -math.inf:
        return math.ceil(min_value)
    elif x == math.inf:
        return math.floor(max_value)
    else:
        return x


def match_senator_name(senator: str, speakers: list) -> list:
    senator = set(preprocess_name(senator).split())
    speakers_prep = list(map(lambda x: set(x.split()), speakers))
    speaker = list(filter(lambda x: x.issubset(senator), speakers_prep))
    senator_idx = [speakers_prep.index(s) for s in speaker]
    senator = [speakers[i] for i in senator_idx]
    return senator

    
def plot_stats(
    df: pd.DataFrame, title: str, ylabel: str, filename: str = None, nwords: int = 25
    ):
    # df copy
    df_copy = deepcopy(df)
    df_copy["word"] = df_copy["word"].apply(postprocess_word)
    df_copy["group"] = df_copy["diff"].apply(lambda x: "pos" if x>=0 else "neg")
    
    # calculate dots sizes
    _min, _max = df_copy["diff"].min(), df_copy["diff"].max()
    df_copy["size"] = df_copy["diff"].apply(lambda x: map_inf(x, _min, _max))
    
    dot_size = scale(df_copy["size"], MinMaxScaler, (0.001,1.0))

    # calculate words texts
    neg, pos = df_copy[df_copy["size"]<0], df_copy[0<=df_copy["size"]]
    word_texts = list()
    
    for df, method, inv in zip([pos, neg],["nlargest", "nsmallest"], [False, True]):
        if not df.empty:
            word_texts.append(scale_text(df, method, nwords, inv))
    word_texts = pd.concat(word_texts)

    # plot
    fig, ax = plt.subplots(figsize=(9,9))

    color_map = {"pos":"#1f77b4", "neg":"#d62728"}
    sns.scatterplot(df_copy, x="total", y="diff",
                    size=dot_size, ax=ax, alpha=.7,
                    hue="group", palette=color_map
    )

    # add words to the right
    ylim_min, ylim_max = ax.get_ylim()
    ylim_div = (ylim_max-ylim_min)/(nwords*2)

    xlim_min, xlim_max = ax.get_xlim()
    
    for e, (i, row) in enumerate(word_texts.iterrows(), start=1):

        # add words to scatter
        ax.text(
            row["total"], row["size"], row["word"],
            horizontalalignment='left', color='black', fontsize=row["text_size"]
        )
        
        ax.text(
            xlim_max+2, ylim_max-(e*ylim_div), row["word"],
            horizontalalignment='left', color=color_map.get(row["group"]),
            fontsize=row["text_size"],
            alpha=.9
        )

    ax.set_title(title)
    ax.set_xlabel("Frecuencia absoluta (log)")
    ax.set_ylabel(ylabel)
    ax.get_legend().set_visible(False)
    plt.tight_layout()

    if filename:
        plt.savefig(filename)
    else:
        plt.show()
    

def postprocess_word(word: str):
    return re.sub(
        r"(?P<word>[a-z]+_)(?P<tag>[a-z]+)",
        lambda x: f"{x.group('word')}{x.group('tag').upper()}",
        word
    )


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

    
def scale(
    x: pd.Series,
    scaler: BaseEstimator,
    feature_range: tuple[float,float],
) -> pd.Series:
    y = deepcopy(x)
    _scaler = scaler(feature_range=feature_range)
    y = (
        _scaler
        .fit_transform(np.array(y).reshape(-1,1))
        .reshape(len(y))
    )
    return y


def scale_text(df: pd.DataFrame, func: callable, n: int = 30, inverse: bool = False) -> pd.DataFrame:
    words_scaler = MinMaxScaler(feature_range=(8.0,16.0))
    method = getattr(df, func)
    inv = -1 if inverse else 1
    df = (
        method(n=n, columns=["size"], keep="all")
        .assign(
            text_size=lambda x: words_scaler.fit_transform(np.array(x["size"]*inv).reshape(-1,1))
        )
        .sort_values(by=["size"], ascending=False)
    )
    return df


def stem_and_lemmatize(
    text: str,
    stemmer: stem.StemmerI = STEMMER,
    model: spacy.Language = SPACY_MODEL
) -> dict[str, str]:
    tokens = model(text)
    output = list()
    for t in tokens:
        token = preprocess_text(t.text)
        if token:
            output.append(
                {
                    "raw": token,
                    "stem": stemmer.stem(token),
                    "lemma": preprocess_text(t.lemma_),
                    "pos": t.pos_
                }
            )
    return output
