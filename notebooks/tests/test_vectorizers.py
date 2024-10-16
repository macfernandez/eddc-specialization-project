import pandas as pd
import pytest

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

def load_expected_df(expected_file):
    source = ["word","diff", "pos", "neg"]
    target = ["vocabulary","diff", "positivo", "negativo"]
    df = (
        pd.read_csv(expected_file,header=0)
        .filter(items=source)
        .rename(columns=dict(zip(source, target)))
    )
    return df


@pytest.mark.parametrize("vectorizer, kwargs, expected_file", [
    (CustomFrequenciesVectorizer, {}, "visualizations/stats/frecuencias.csv"),
    (CustomProportionsVectorizer, {}, "visualizations/stats/proporciones.csv"),
    # los datos en este archivo se guardaron mal
    #(CustomProportionsVectorizer, {"custom_stop_words": "zipf"}, "visualizations/stats/proporciones_sin_stopwords_zipf.csv"),
    (CustomOddsRatioVectorizer, {}, "visualizations/stats/odds.csv"),
    (CustomLogOddsRatioVectorizer, {}, "visualizations/stats/log_odds.csv"),
    # los datos en este archivo se guardaron mal
    #(CustomLogOddsRatioVectorizer, {"smooth": .5}, "visualizations/stats/log_odds_suavizado.csv"),
    (CustomTfidfVectorizer, {}, "visualizations/stats/tfidf_dfnatural.csv"),
    (CustomTfidfVectorizer, {"log_idf": True}, "visualizations/stats/tfidf_dflogged.csv"),
    (CustomWordScoresVectorizer, {}, "visualizations/stats/wordscores.csv")
])
def test_calculate_metric_returns_same_df(vectorizer, kwargs, expected_file):
    expected = load_expected_df(expected_file)
    vectorizer = vectorizer(positive_values="positivo", **kwargs)
    predicted = (
        vectorizer
        .calculate_metric(data.speech_lemma_pos.to_list(), data.vote.to_list(), "negativo")
        [expected.columns.tolist()]
    )
    pd.testing.assert_frame_equal(expected, predicted, check_index_type=False)

    X = vectorizer.fit_transform(data.speech_lemma_pos.to_list(), data.vote.to_list())
    vectors = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
    assert vectors.shape == (len(data), vectorizer.dimension)