import pandas as pd

from notebooks.config import DATA_PATH
from notebooks.vectorizers import *


X_train_index = (
    pd.read_csv(
        os.path.join("models", "index", f"X_train_index.csv"),
        header=None, index_col=0
    )
    .index
)

data_path = os.path.join("data", "session_speech.csv")
data = pd.read_csv(data_path, converters={"speech_lemma_pos":eval})
data = (
    data[(data.speech.notna()) & (~data.vote.isin(["abstención", "ausente"]))]
    .reset_index(drop=True)
    .assign(
        speech_lemma_pos=lambda x: x.speech_lemma_pos.apply(
            lambda z: " ".join(["_".join(i) for i in z])
        )
    )
    .filter(regex=(r"\b(speech_lemma_pos|vote)\b"))
    .iloc[X_train_index]
)


# test frequencies
expected = pd.read_csv(
    "visualizations/stats/frecuencias.csv",
    header=0,
    names=["vocabulary","total","diff", "positivo", "negativo"],
    usecols=["vocabulary","diff", "positivo", "negativo"],
)

#vectorizer = CustomFrequenciesVectorizer(positive_values="positivo")
#predicted = (
#    vectorizer
#    .calculate_metric(data.speech_lemma_pos.to_list(), data.vote.to_list(), "negativo")
#    [expected.columns.tolist()]
#)
#pd.testing.assert_frame_equal(expected, predicted)
#
#X = vectorizer.fit_transform(data.speech_lemma_pos.to_list(), data.vote.to_list())
#
#vectors = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
#print("ABS FREQS", vectors.shape)

# test proportions
#expected = pd.read_csv(
#    #"visualizations/stats/proporciones.csv",
#    "visualizations/stats/proporciones_sin_stopwords_zipf.csv",
#    header=0,
#    names=["vocabulary","total","diff", "positivo", "negativo"],
#    usecols=["vocabulary","diff", "positivo", "negativo"],
#)
#
#vectorizer = CustomProportionsVectorizer(
#    positive_values="positivo",
#    custom_stop_words="zipf"
#)
#predicted = (
#    vectorizer
#    .calculate_metric(data.speech_lemma_pos.to_list(), data.vote.to_list(), "negativo")
#    [expected.columns.tolist()]
#)
#pd.testing.assert_frame_equal(expected, predicted, check_index_type=False)
#
#X = vectorizer.fit_transform(data.speech_lemma_pos.to_list(), data.vote.to_list())
#
#vectors = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
#print("PROP", vectors.shape)

# test odds
expected = pd.read_csv(
    #"visualizations/stats/proporciones.csv",
    "visualizations/stats/odds.csv",
    header=0,
    names=["vocabulary","total","diff", "positivo", "negativo"],
    usecols=["vocabulary","diff", "positivo", "negativo"],
)

vectorizer = CustomOddsRatioVectorizer(
    positive_values="positivo"
)
predicted = (
    vectorizer
    .calculate_metric(data.speech_lemma_pos.to_list(), data.vote.to_list(), "negativo")
    [expected.columns.tolist()]
)
pd.testing.assert_frame_equal(expected, predicted, check_index_type=False)

X = vectorizer.fit_transform(data.speech_lemma_pos.to_list(), data.vote.to_list())

vectors = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
print("ODDS", vectors.shape)