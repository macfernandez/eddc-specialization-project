import os

import math

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from config import MODELS_PATH

STOPWORDS_PATH = os.path.join(MODELS_PATH, "stopwords")


class CustomFrequenciesVectorizer(CountVectorizer):
    def __init__(
        self,
        *,
        input="content",
        encoding="utf-8",
        decode_error="strict",
        strip_accents=None,
        lowercase=True,
        preprocessor=None,
        tokenizer=None,
        stop_words=None,
        token_pattern=r"(?u)\b\w\w+\b",
        ngram_range=(1, 1),
        analyzer="word",
        max_df=1.0,
        min_df=1,
        max_features=None,
        vocabulary=None,
        binary=False,
        dtype=np.int64,
        dimension: int = 300,
        positive_values: str = "",
        custom_stop_words: str = "",
        n_custom_stop_words: int = 1
        ) -> None:
        super().__init__(
            input=input,
            encoding=encoding,
            decode_error=decode_error,
            strip_accents=strip_accents,
            lowercase=lowercase,
            preprocessor=preprocessor,
            tokenizer=tokenizer,
            stop_words=stop_words,
            token_pattern=token_pattern,
            ngram_range=ngram_range,
            analyzer=analyzer,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features,
            vocabulary=vocabulary,
            binary=binary,
            dtype=dtype
        )
        self.dimension = dimension
        self.custom_stop_words = custom_stop_words
        self.n_custom_stop_words = n_custom_stop_words
        self.positive_values = positive_values

    def fit(self, raw_documents, y=None):
        super().fit(raw_documents)
        return self
    
    def fit_transform(self, raw_documents:list[str], y:list[str]):
        difference = self.calculate_metric(raw_documents, y)

        if (len(difference)*2) <= (self.dimension):
            vocabulary = difference.vocabulary.to_list()
        else:
            n = math.ceil(int(self.dimension / 2))
            pos_voc = (
                difference[difference["diff"]>=0]
                .sort_values(by=["diff", "pos", "neg"], ascending=[False, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            neg_voc = (
                difference[difference["diff"]<0]
                .sort_values(by=["diff", "neg", "pos"], ascending=[True, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            vocabulary = pos_voc+neg_voc
        self.vocabulary = vocabulary
        return super().fit_transform(raw_documents, y)
        
    def calculate_metric(self, raw_documents:list[str], y:list[str]):
        total_frequencies = self._count_total_frequencies(raw_documents, y)
        
        negative_values = list(set(y).difference(set([self.positive_values])))[0]
        
        count_difference = (
            pd.DataFrame({
                "diff": total_frequencies.loc[self.positive_values]-total_frequencies.loc[negative_values],
                "pos": total_frequencies.loc[self.positive_values],
                "neg": total_frequencies.loc[negative_values]
            })
            .rename_axis("vocabulary", axis=0)
            .reset_index()
        )
        return count_difference

    def _count_total_frequencies(self, raw_documents, y=None):
        X = super().fit_transform(raw_documents, y)
        total_frequencies = (
            pd.DataFrame(X.toarray(), columns=self.get_feature_names_out(), index=y)
            .rename_axis("LABEL", axis=0)
            .reset_index()
            .groupby("LABEL")
            .sum()
        )
        if (self.custom_stop_words == "zipf"):
            total_frequencies = self._remove_zipf_stopwords(total_frequencies)
        return total_frequencies
    
    def _set_stopwords(self, raw_documents) -> list:
        if isinstance(self.custom_stop_words, str) and (self.custom_stop_words == "zipf"):
            self.stop_words = self.get_zipf_stopwords(raw_documents)
        elif isinstance(self.custom_stop_words, list):
            self.stop_words = self.custom_stop_words
        elif self.custom_stop_words == None:
            self.stop_words = self.custom_stop_words
        else:
            raise ValueError("stop_words must be either string ('zipf'), a list of strings or None.")

    def _remove_zipf_stopwords(self, frequencies):
        stop_words = self.get_zipf_stop_words(frequencies)
        return frequencies.drop(columns=stop_words)
    
    def get_zipf_stop_words(self, frequencies):
        stop_words = (
            frequencies
            .sum(axis=0)
            .sort_values(ascending=False)
            .head(100)
            .index
            .tolist()
        )
        file = f"{self.__class__.__name__}_{self.dimension}_{self.custom_stop_words}_{self.n_custom_stop_words}_{self.positive_values}.txt"
        file_path = os.path.join(STOPWORDS_PATH, file)
        os.makedirs(STOPWORDS_PATH, exist_ok=True)
        with open(file_path, "w") as f:
            _ = f.write("\n".join(stop_words))
        return stop_words
    
    def transform(self, raw_documents):
        return super().transform(raw_documents)


class CustomProportionsVectorizer(CountVectorizer):
    def __init__(
        self,
        *,
        input="content",
        encoding="utf-8",
        decode_error="strict",
        strip_accents=None,
        lowercase=True,
        preprocessor=None,
        tokenizer=None,
        stop_words=None,
        token_pattern=r"(?u)\b\w\w+\b",
        ngram_range=(1, 1),
        analyzer="word",
        max_df=1.0,
        min_df=1,
        max_features=None,
        vocabulary=None,
        binary=False,
        dtype=np.int64,
        dimension: int = 300,
        positive_values: str = "",
        custom_stop_words: str = "",
        n_custom_stop_words: int = 1
        ) -> None:
        super().__init__(
            input=input,
            encoding=encoding,
            decode_error=decode_error,
            strip_accents=strip_accents,
            lowercase=lowercase,
            preprocessor=preprocessor,
            tokenizer=tokenizer,
            stop_words=stop_words,
            token_pattern=token_pattern,
            ngram_range=ngram_range,
            analyzer=analyzer,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features,
            vocabulary=vocabulary,
            binary=binary,
            dtype=dtype,
        )
        self.dimension = dimension
        self.custom_stop_words = custom_stop_words
        self.n_custom_stop_words = n_custom_stop_words
        self.positive_values = positive_values
 
    def fit(self, raw_documents, y=None):
        super().fit(raw_documents)
        return self

    def fit_transform(self, raw_documents:list[str], y:list[str]):
        difference = self.calculate_metric(raw_documents, y)

        if (len(difference)*2) <= (self.dimension):
            vocabulary = difference.vocabulary.to_list()
        else:
            n = math.ceil(int(self.dimension / 2))
            pos_voc = (
                difference[difference["diff"]>=0]
                .sort_values(by=["diff", "pos", "neg"], ascending=[False, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            neg_voc = (
                difference[difference["diff"]<0]
                .sort_values(by=["diff", "neg", "pos"], ascending=[True, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            vocabulary = pos_voc+neg_voc
        self.vocabulary = vocabulary
        return super().fit_transform(raw_documents, y)
 
    def calculate_metric(self, raw_documents:list[str], y:list[str]):
        proportions = self._calculate_proportions(raw_documents, y)
        
        negative_values = list(set(y).difference(set([self.positive_values])))[0]

        count_difference = (
            pd.DataFrame({
                "diff": proportions.loc[self.positive_values]-proportions.loc[negative_values],
                "pos": proportions.loc[self.positive_values],
                "neg": proportions.loc[negative_values]
            })
            .rename_axis("vocabulary", axis=0)
            .reset_index()
        )
        return count_difference
    
    def _calculate_proportions(self, raw_documents:list[str], y:list[str]):
        total_frequencies = self._count_total_frequencies(raw_documents, y)
        proportions = total_frequencies.div(total_frequencies.sum(axis=1), axis=0)
        return proportions

    def _count_total_frequencies(self, raw_documents, y=None):
        X = super().fit_transform(raw_documents, y)
        total_frequencies = (
            pd.DataFrame(X.toarray(), columns=self.get_feature_names_out(), index=y)
            .rename_axis("LABEL", axis=0)
            .reset_index()
            .groupby("LABEL")
            .sum()
        )
        if (self.custom_stop_words == "zipf"):
            total_frequencies = self._remove_zipf_stopwords(total_frequencies)
        return total_frequencies
    
    def _set_stopwords(self, raw_documents) -> list:
        if isinstance(self.custom_stop_words, str) and (self.custom_stop_words == "zipf"):
            self.stop_words = self.get_zipf_stopwords(raw_documents)
        elif isinstance(self.custom_stop_words, list):
            self.stop_words = self.custom_stop_words
        elif self.custom_stop_words == None:
            self.stop_words = self.custom_stop_words
        else:
            raise ValueError("stop_words must be either string ('zipf'), a list of strings or None.")

    def _remove_zipf_stopwords(self, frequencies):
        stop_words = self.get_zipf_stop_words(frequencies)
        return frequencies.drop(columns=stop_words)
    
    def get_zipf_stop_words(self, frequencies):
        stop_words = (
            frequencies
            .sum(axis=0)
            .sort_values(ascending=False)
            .head(100)
            .index
            .tolist()
        )
        file = f"{self.__class__.__name__}_{self.dimension}_{self.custom_stop_words}_{self.n_custom_stop_words}_{self.positive_values}.txt"
        file_path = os.path.join(STOPWORDS_PATH, file)
        os.makedirs(STOPWORDS_PATH, exist_ok=True)
        with open(file_path, "w") as f:
            _ = f.write("\n".join(stop_words))
        return stop_words
    
    def transform(self, raw_documents):
        return super().transform(raw_documents)


class CustomOddsRatioVectorizer(CountVectorizer):
    def __init__(
        self,
        *,
        input="content",
        encoding="utf-8",
        decode_error="strict",
        strip_accents=None,
        lowercase=True,
        preprocessor=None,
        tokenizer=None,
        stop_words=None,
        token_pattern=r"(?u)\b\w\w+\b",
        ngram_range=(1, 1),
        analyzer="word",
        max_df=1.0,
        min_df=1,
        max_features=None,
        vocabulary=None,
        binary=False,
        dtype=np.int64,
        dimension: int = 300,
        positive_values: str = "",
        custom_stop_words: str = "",
        n_custom_stop_words: int = 1
        ) -> None:
        super().__init__(
            input=input,
            encoding=encoding,
            decode_error=decode_error,
            strip_accents=strip_accents,
            lowercase=lowercase,
            preprocessor=preprocessor,
            tokenizer=tokenizer,
            stop_words=stop_words,
            token_pattern=token_pattern,
            ngram_range=ngram_range,
            analyzer=analyzer,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features,
            vocabulary=vocabulary,
            binary=binary,
            dtype=dtype,
        )
        self.dimension = dimension
        self.custom_stop_words = custom_stop_words
        self.n_custom_stop_words = n_custom_stop_words
        self.positive_values = positive_values

    def fit(self, raw_documents, y=None):
        super().fit(raw_documents)
        return self

    def fit_transform(self, raw_documents:list[str], y:list[str]):
        difference = self.calculate_metric(raw_documents, y)

        if (len(difference)*2) <= (self.dimension):
            vocabulary = difference.vocabulary.to_list()
        else:
            n = math.ceil(int(self.dimension / 2))
            pos_voc = (
                difference[difference["diff"]>=1]
                .sort_values(by=["diff", "pos", "neg"], ascending=[False, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            neg_voc = (
                difference[difference["diff"]<1]
                .sort_values(by=["diff", "neg", "pos"], ascending=[True, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            vocabulary = pos_voc+neg_voc
        self.vocabulary = vocabulary
        return super().fit_transform(raw_documents, y)

    def calculate_metric(self, raw_documents:list[str], y:list[str]):
        proportions = self._calculate_proportions(raw_documents, y)

        negative_values = list(set(y).difference(set([self.positive_values])))[0]
        
        count_difference = (
            pd.DataFrame({
                "pos": proportions.loc[self.positive_values]/(1-proportions.loc[self.positive_values]),
                "neg": proportions.loc[negative_values]/(1-proportions.loc[negative_values])
            })
            .assign(diff=lambda x: x["pos"]/x["neg"])
            .rename_axis("vocabulary", axis=0)
            .reset_index()
        )

        return count_difference
    
    def _calculate_proportions(self, raw_documents:list[str], y:list[str]):
        total_frequencies = self._count_total_frequencies(raw_documents, y)
        proportions = total_frequencies.div(total_frequencies.sum(axis=1), axis=0)
        return proportions

    def _count_total_frequencies(self, raw_documents, y=None):
        X = super().fit_transform(raw_documents, y)
        total_frequencies = (
            pd.DataFrame(X.toarray(), columns=self.get_feature_names_out(), index=y)
            .rename_axis("LABEL", axis=0)
            .reset_index()
            .groupby("LABEL")
            .sum()
        )
        if (self.custom_stop_words == "zipf"):
            total_frequencies = self._remove_zipf_stopwords(total_frequencies)
        return total_frequencies
    
    def _set_stopwords(self, raw_documents) -> list:
        if isinstance(self.custom_stop_words, str) and (self.custom_stop_words == "zipf"):
            self.stop_words = self.get_zipf_stopwords(raw_documents)
        elif isinstance(self.custom_stop_words, list):
            self.stop_words = self.custom_stop_words
        elif self.custom_stop_words == None:
            self.stop_words = self.custom_stop_words
        else:
            raise ValueError("stop_words must be either string ('zipf'), a list of strings or None.")

    def _remove_zipf_stopwords(self, frequencies):
        stop_words = self.get_zipf_stop_words(frequencies)
        return frequencies.drop(columns=stop_words)
    
    def get_zipf_stop_words(self, frequencies):
        stop_words = (
            frequencies
            .sum(axis=0)
            .sort_values(ascending=False)
            .head(100)
            .index
            .tolist()
        )
        file = f"{self.__class__.__name__}_{self.dimension}_{self.custom_stop_words}_{self.n_custom_stop_words}_{self.positive_values}.txt"
        file_path = os.path.join(STOPWORDS_PATH, file)
        os.makedirs(STOPWORDS_PATH, exist_ok=True)
        with open(file_path, "w") as f:
            _ = f.write("\n".join(stop_words))
        return stop_words
    
    def transform(self, raw_documents):
        return super().transform(raw_documents)


class CustomLogOddsRatioVectorizer(CountVectorizer):
    def __init__(
        self,
        *,
        input="content",
        encoding="utf-8",
        decode_error="strict",
        strip_accents=None,
        lowercase=True,
        preprocessor=None,
        tokenizer=None,
        stop_words=None,
        token_pattern=r"(?u)\b\w\w+\b",
        ngram_range=(1, 1),
        analyzer="word",
        max_df=1.0,
        min_df=1,
        max_features=None,
        vocabulary=None,
        binary=False,
        dtype=np.int64,
        dimension: int = 300,
        positive_values: str = "",
        custom_stop_words: str = "",
        n_custom_stop_words: int = 1
        ) -> None:
        super().__init__(
            input=input,
            encoding=encoding,
            decode_error=decode_error,
            strip_accents=strip_accents,
            lowercase=lowercase,
            preprocessor=preprocessor,
            tokenizer=tokenizer,
            stop_words=stop_words,
            token_pattern=token_pattern,
            ngram_range=ngram_range,
            analyzer=analyzer,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features,
            vocabulary=vocabulary,
            binary=binary,
            dtype=dtype,
        )
        self.dimension = dimension
        self.custom_stop_words = custom_stop_words
        self.n_custom_stop_words = n_custom_stop_words
        self.positive_values = positive_values
 
    def fit(self, raw_documents, y=None):
        super().fit(raw_documents)
        return self

    def fit_transform(self, raw_documents:list[str], y:list[str]):
        difference = self.calculate_metric(raw_documents, y)

        if (len(difference)*2) <= (self.dimension):
            vocabulary = difference.vocabulary.to_list()
        else:
            n = math.ceil(int(self.dimension / 2))
            pos_voc = (
                difference[difference["diff"]>=0]
                .sort_values(by=["diff", "pos", "neg"], ascending=[False, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            neg_voc = (
                difference[difference["diff"]<0]
                .sort_values(by=["diff", "neg", "pos"], ascending=[True, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            vocabulary = pos_voc+neg_voc
        self.vocabulary = vocabulary
        return super().fit_transform(raw_documents, y)

    def calculate_metric(self, raw_documents:list[str], y:list[str]):
        count_difference = self._calculate_odds(raw_documents, y)
        count_difference["diff"] = np.log(count_difference["diff"])

        return count_difference
    
    def _calculate_proportions(self, raw_documents:list[str], y:list[str]):
        total_frequencies = self._count_total_frequencies(raw_documents, y)
        proportions = total_frequencies.div(total_frequencies.sum(axis=1), axis=0)
        return proportions
    
    def _calculate_odds(self, raw_documents:list[str], y:list[str]):
        proportions = self._calculate_proportions(raw_documents, y)

        negative_values = list(set(y).difference(set([self.positive_values])))[0]
        
        count_difference = (
            pd.DataFrame({
                "pos": proportions.loc[self.positive_values]/(1-proportions.loc[self.positive_values]),
                "neg": proportions.loc[negative_values]/(1-proportions.loc[negative_values])
            })
            .assign(diff=lambda x: x["pos"]/x["neg"])
            .rename_axis("vocabulary", axis=0)
            .reset_index()
        )

        return count_difference

    def _count_total_frequencies(self, raw_documents, y=None):
        X = super().fit_transform(raw_documents, y)
        total_frequencies = (
            pd.DataFrame(X.toarray(), columns=self.get_feature_names_out(), index=y)
            .rename_axis("LABEL", axis=0)
            .reset_index()
            .groupby("LABEL")
            .sum()
        )
        if (self.custom_stop_words == "zipf"):
            total_frequencies = self._remove_zipf_stopwords(total_frequencies)
        return total_frequencies
    
    def _set_stopwords(self, raw_documents) -> list:
        if isinstance(self.custom_stop_words, str) and (self.custom_stop_words == "zipf"):
            self.stop_words = self.get_zipf_stopwords(raw_documents)
        elif isinstance(self.custom_stop_words, list):
            self.stop_words = self.custom_stop_words
        elif self.custom_stop_words == None:
            self.stop_words = self.custom_stop_words
        else:
            raise ValueError("stop_words must be either string ('zipf'), a list of strings or None.")

    def _remove_zipf_stopwords(self, frequencies):
        stop_words = self.get_zipf_stop_words(frequencies)
        return frequencies.drop(columns=stop_words)
    
    def get_zipf_stop_words(self, frequencies):
        stop_words = (
            frequencies
            .sum(axis=0)
            .sort_values(ascending=False)
            .head(100)
            .index
            .tolist()
        )
        file = f"{self.__class__.__name__}_{self.dimension}_{self.custom_stop_words}_{self.n_custom_stop_words}_{self.positive_values}.txt"
        file_path = os.path.join(STOPWORDS_PATH, file)
        os.makedirs(STOPWORDS_PATH, exist_ok=True)
        with open(file_path, "w") as f:
            _ = f.write("\n".join(stop_words))
        return stop_words
    
    def transform(self, raw_documents):
        return super().transform(raw_documents)


class CustomSmoothLogOddsRatioVectorizer(CountVectorizer):
    def __init__(
        self,
        *,
        input="content",
        encoding="utf-8",
        decode_error="strict",
        strip_accents=None,
        lowercase=True,
        preprocessor=None,
        tokenizer=None,
        stop_words=None,
        token_pattern=r"(?u)\b\w\w+\b",
        ngram_range=(1, 1),
        analyzer="word",
        max_df=1.0,
        min_df=1,
        max_features=None,
        vocabulary=None,
        binary=False,
        dtype=np.int64,
        dimension: int = 300,
        positive_values: str = "",
        custom_stop_words: str = "",
        n_custom_stop_words: int = 1
        ) -> None:
        super().__init__(
            input=input,
            encoding=encoding,
            decode_error=decode_error,
            strip_accents=strip_accents,
            lowercase=lowercase,
            preprocessor=preprocessor,
            tokenizer=tokenizer,
            stop_words=stop_words,
            token_pattern=token_pattern,
            ngram_range=ngram_range,
            analyzer=analyzer,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features,
            vocabulary=vocabulary,
            binary=binary,
            dtype=dtype
        )
        self.dimension = dimension
        self.custom_stop_words = custom_stop_words
        self.n_custom_stop_words = n_custom_stop_words
        self.positive_values = positive_values

    def fit(self, raw_documents, y=None):
        super().fit(raw_documents)
        return self
    
    def fit_transform(self, raw_documents:list[str], y:list[str]):
        difference = self.calculate_metric(raw_documents, y)

        if (len(difference)*2) <= (self.dimension):
            vocabulary = difference.vocabulary.to_list()
        else:
            n = math.ceil(int(self.dimension / 2))
            pos_voc = (
                difference[difference["diff"]>=0]
                .sort_values(by=["diff", "pos", "neg"], ascending=[False, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            neg_voc = (
                difference[difference["diff"]<0]
                .sort_values(by=["diff", "neg", "pos"], ascending=[True, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            vocabulary = pos_voc+neg_voc
        self.vocabulary = vocabulary
        return super().fit_transform(raw_documents, y)
    
    def calculate_metric(self, raw_documents:list[str], y:list[str]):
        negative_values = list(set(y).difference(set([self.positive_values])))[0]

        proportions = self._calculate_proportions(raw_documents, y)

        proportions.loc[["positivo", "negativo"]] = (
            proportions.loc[["positivo", "negativo"]]
            .applymap(lambda x: x+0.5 if x == 0 else x)
        )

        f_smooth_log_odds_diff = (
            pd
            .DataFrame({
                "pos": proportions.loc[self.positive_values]/(1-proportions.loc[self.positive_values]),
                "neg": proportions.loc[negative_values]/(1-proportions.loc[negative_values])
            })
            .assign(
                diff=lambda x: np.log(x["pos"]/x["neg"])
            )
            .rename_axis("vocabulary", axis=0)
            .reset_index()
        )

        return f_smooth_log_odds_diff

    
    def _calculate_proportions(self, raw_documents:list[str], y:list[str]):
        total_frequencies = self._count_total_frequencies(raw_documents, y)
        proportions = total_frequencies.div(total_frequencies.sum(axis=1), axis=0)
        return proportions

    def _count_total_frequencies(self, raw_documents, y=None):
        X = super().fit_transform(raw_documents, y)
        total_frequencies = (
            pd.DataFrame(X.toarray(), columns=self.get_feature_names_out(), index=y)
            .rename_axis("LABEL", axis=0)
            .reset_index()
            .groupby("LABEL")
            .sum()
        )
        if (self.custom_stop_words == "zipf"):
            total_frequencies = self._remove_zipf_stopwords(total_frequencies)
        return total_frequencies
    
    def _set_stopwords(self, raw_documents) -> list:
        if isinstance(self.custom_stop_words, str) and (self.custom_stop_words == "zipf"):
            self.stop_words = self.get_zipf_stopwords(raw_documents)
        elif isinstance(self.custom_stop_words, list):
            self.stop_words = self.custom_stop_words
        elif self.custom_stop_words == None:
            self.stop_words = self.custom_stop_words
        else:
            raise ValueError("stop_words must be either string ('zipf'), a list of strings or None.")

    def _remove_zipf_stopwords(self, frequencies):
        stop_words = self.get_zipf_stop_words(frequencies)
        return frequencies.drop(columns=stop_words)
    
    def get_zipf_stop_words(self, frequencies):
        stop_words = (
            frequencies
            .sum(axis=0)
            .sort_values(ascending=False)
            .head(100)
            .index
            .tolist()
        )
        file = f"{self.__class__.__name__}_{self.dimension}_{self.custom_stop_words}_{self.n_custom_stop_words}_{self.positive_values}.txt"
        file_path = os.path.join(STOPWORDS_PATH, file)
        os.makedirs(STOPWORDS_PATH, exist_ok=True)
        with open(file_path, "w") as f:
            _ = f.write("\n".join(stop_words))
        return stop_words
    
    def transform(self, raw_documents):
        return super().transform(raw_documents)


class CustomTfidfVectorizer(CountVectorizer):
    def __init__(
        self,
        *,
        input="content",
        encoding="utf-8",
        decode_error="strict",
        strip_accents=None,
        lowercase=True,
        preprocessor=None,
        tokenizer=None,
        stop_words=None,
        token_pattern=r"(?u)\b\w\w+\b",
        ngram_range=(1, 1),
        analyzer="word",
        max_df=1.0,
        min_df=1,
        max_features=None,
        vocabulary=None,
        binary=False,
        dtype=np.int64,
        dimension: int = 300,
        positive_values: str = "",
        custom_stop_words: str = "",
        n_custom_stop_words: int = 1,
        log_idf: bool = False
        ) -> None:
        super().__init__(
            input=input,
            encoding=encoding,
            decode_error=decode_error,
            strip_accents=strip_accents,
            lowercase=lowercase,
            preprocessor=preprocessor,
            tokenizer=tokenizer,
            stop_words=stop_words,
            token_pattern=token_pattern,
            ngram_range=ngram_range,
            analyzer=analyzer,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features,
            vocabulary=vocabulary,
            binary=binary,
            dtype=dtype
        )
        self.log_idf = log_idf
        self.dimension = dimension
        self.custom_stop_words = custom_stop_words
        self.n_custom_stop_words = n_custom_stop_words
        self.positive_values = positive_values

    def fit(self, raw_documents, y=None):
        super().fit(raw_documents)
        return self
    
    def fit_transform(self, raw_documents:list[str], y:list[str]):
        difference = self.calculate_metric(raw_documents, y)

        if (len(difference)*2) <= (self.dimension):
            vocabulary = difference.vocabulary.to_list()
        else:
            n = math.ceil(int(self.dimension / 2))
            pos_voc = (
                difference[difference["diff"]>=0]
                .sort_values(by=["diff", "pos", "neg"], ascending=[False, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            neg_voc = (
                difference[difference["diff"]<0]
                .sort_values(by=["diff", "neg", "pos"], ascending=[True, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            vocabulary = pos_voc+neg_voc
        self.vocabulary = vocabulary
        return super().fit_transform(raw_documents, y)
 
    def calculate_metric(self, raw_documents:list[str], y:list[str]):
        total_frequencies = self._calculate_proportions(raw_documents, y)

        vectorizer = CountVectorizer(lowercase=True)
        X = vectorizer.fit_transform(raw_documents)
        X = X.toarray()
        tf_idf = (
            pd.DataFrame(X, columns=vectorizer.get_feature_names_out())
            .sum(axis=0)
            .to_frame("df")
            .reset_index(names="vocabulary")
            .merge(total_frequencies, on="vocabulary", how="right")
            [["vocabulary", "pos", "neg", "df"]]
        )
        
        if self.log_idf:
            tf_idf["log_idf"] = tf_idf.df.apply(lambda x: math.log(1/x))
            tf_idf = (
                tf_idf
                .assign(
                    pos=tf_idf.apply(lambda x: x.pos*x.log_idf, axis=1),
                    neg=tf_idf.apply(lambda x: x.neg*x.log_idf, axis=1)
                )
                .assign(diff=lambda x: x.pos - x.neg)
            )
        else:
            tf_idf = (
                tf_idf
                .assign(
                    pos=tf_idf.apply(lambda x: x.pos/x.df, axis=1),
                    neg=tf_idf.apply(lambda x: x.neg/x.df, axis=1)
                )
                .assign(diff=lambda x: x.pos - x.neg)
            )

        return tf_idf[["vocabulary", "diff", "pos", "neg"]]

    def calculate_metric(self, raw_documents:list[str], y:list[str]):
        proportions = self._calculate_proportions(raw_documents, y)
        
        negative_values = list(set(y).difference(set([self.positive_values])))[0]

        count_difference = (
            pd.DataFrame({
                "diff": proportions.loc[self.positive_values]-proportions.loc[negative_values],
                "pos": proportions.loc[self.positive_values],
                "neg": proportions.loc[negative_values]
            })
            .rename_axis("vocabulary", axis=0)
            .reset_index()
        )
        return count_difference
    
    def _calculate_proportions(self, raw_documents:list[str], y:list[str]):
        total_frequencies = self._count_total_frequencies(raw_documents, y)
        proportions = total_frequencies.div(total_frequencies.sum(axis=1), axis=0)
        return proportions

    def _count_total_frequencies(self, raw_documents, y=None):
        X = super().fit_transform(raw_documents, y)
        total_frequencies = (
            pd.DataFrame(X.toarray(), columns=self.get_feature_names_out(), index=y)
            .rename_axis("LABEL", axis=0)
            .reset_index()
            .groupby("LABEL")
            .sum()
        )
        if (self.custom_stop_words == "zipf"):
            total_frequencies = self._remove_zipf_stopwords(total_frequencies)
        return total_frequencies
    
    def _set_stopwords(self, raw_documents) -> list:
        if isinstance(self.custom_stop_words, str) and (self.custom_stop_words == "zipf"):
            self.stop_words = self.get_zipf_stopwords(raw_documents)
        elif isinstance(self.custom_stop_words, list):
            self.stop_words = self.custom_stop_words
        elif self.custom_stop_words == None:
            self.stop_words = self.custom_stop_words
        else:
            raise ValueError("stop_words must be either string ('zipf'), a list of strings or None.")

    def _remove_zipf_stopwords(self, frequencies):
        stop_words = self.get_zipf_stop_words(frequencies)
        return frequencies.drop(columns=stop_words)
    
    def get_zipf_stop_words(self, frequencies):
        stop_words = (
            frequencies
            .sum(axis=0)
            .sort_values(ascending=False)
            .head(100)
            .index
            .tolist()
        )
        file = f"{self.__class__.__name__}_{self.dimension}_{self.custom_stop_words}_{self.n_custom_stop_words}_{self.positive_values}.txt"
        file_path = os.path.join(STOPWORDS_PATH, file)
        os.makedirs(STOPWORDS_PATH, exist_ok=True)
        with open(file_path, "w") as f:
            _ = f.write("\n".join(stop_words))
        return stop_words
    
    def transform(self, raw_documents):
        return super().transform(raw_documents)


class CustomWordScoresVectorizer(CountVectorizer):
    def __init__(
        self,
        *,
        input="content",
        encoding="utf-8",
        decode_error="strict",
        strip_accents=None,
        lowercase=True,
        preprocessor=None,
        tokenizer=None,
        stop_words=None,
        token_pattern=r"(?u)\b\w\w+\b",
        ngram_range=(1, 1),
        analyzer="word",
        max_df=1.0,
        min_df=1,
        max_features=None,
        vocabulary=None,
        binary=False,
        dtype=np.int64,
        dimension: int = 300,
        positive_values: str = "",
        custom_stop_words: str = "",
        n_custom_stop_words: int = 1
        ) -> None:
        super().__init__(
            input=input,
            encoding=encoding,
            decode_error=decode_error,
            strip_accents=strip_accents,
            lowercase=lowercase,
            preprocessor=preprocessor,
            tokenizer=tokenizer,
            stop_words=stop_words,
            token_pattern=token_pattern,
            ngram_range=ngram_range,
            analyzer=analyzer,
            max_df=max_df,
            min_df=min_df,
            max_features=max_features,
            vocabulary=vocabulary,
            binary=binary,
            dtype=dtype,
        )
        self.dimension = dimension
        self.custom_stop_words = custom_stop_words
        self.n_custom_stop_words = n_custom_stop_words
        self.positive_values = positive_values

    def fit(self, raw_documents, y=None):
        super().fit(raw_documents)
        return self

    def fit_transform(self, raw_documents:list[str], y:list[str]):
        difference = self.calculate_metric(raw_documents, y)

        if (len(difference)*2) <= (self.dimension):
            vocabulary = difference.vocabulary.to_list()
        else:
            n = math.ceil(int(self.dimension / 2))
            pos_voc = (
                difference[difference["diff"]>=0]
                .sort_values(by=["diff", "pos", "neg"], ascending=[False, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            neg_voc = (
                difference[difference["diff"]<0]
                .sort_values(by=["diff", "neg", "pos"], ascending=[True, False, True])
                .head(n)
                .vocabulary
                .to_list()
            )
            vocabulary = pos_voc+neg_voc
        self.vocabulary = vocabulary
        return super().fit_transform(raw_documents, y)

    def calculate_metric(self, raw_documents:list[str], y:list[str]):
        total_frequencies = self._count_total_frequencies(raw_documents, y)

        proportions = total_frequencies.div(total_frequencies.sum(axis=1), axis=0)
        
        negative_values = list(set(y).difference(set([self.positive_values])))[0]
        
        wkw = (
            (proportions.loc[self.positive_values]-proportions.loc[negative_values])/
            (proportions.loc[self.positive_values]+proportions.loc[negative_values])
        )
        nkw = total_frequencies.sum(axis=0)

        wkw_diff = (
            pd
            .DataFrame({
                "diff": wkw*nkw,
                "pos": wkw*nkw,
                "neg": wkw*nkw,
            })
            .rename_axis("vocabulary", axis=0)
            .reset_index()
        )
        return wkw_diff

    def _count_total_frequencies(self, raw_documents, y=None):
        X = super().fit_transform(raw_documents, y)
        total_frequencies = (
            pd.DataFrame(X.toarray(), columns=self.get_feature_names_out(), index=y)
            .rename_axis("LABEL", axis=0)
            .reset_index()
            .groupby("LABEL")
            .sum()
        )
        if (self.custom_stop_words == "zipf"):
            total_frequencies = self._remove_zipf_stopwords(total_frequencies)
        return total_frequencies
    
    def _set_stopwords(self, raw_documents) -> list:
        if isinstance(self.custom_stop_words, str) and (self.custom_stop_words == "zipf"):
            self.stop_words = self.get_zipf_stopwords(raw_documents)
        elif isinstance(self.custom_stop_words, list):
            self.stop_words = self.custom_stop_words
        elif self.custom_stop_words == None:
            self.stop_words = self.custom_stop_words
        else:
            raise ValueError("stop_words must be either string ('zipf'), a list of strings or None.")

    def _remove_zipf_stopwords(self, frequencies):
        stop_words = self.get_zipf_stop_words(frequencies)
        return frequencies.drop(columns=stop_words)
    
    def get_zipf_stop_words(self, frequencies):
        stop_words = (
            frequencies
            .sum(axis=0)
            .sort_values(ascending=False)
            .head(100)
            .index
            .tolist()
        )
        file = f"{self.__class__.__name__}_{self.dimension}_{self.custom_stop_words}_{self.n_custom_stop_words}_{self.positive_values}.txt"
        file_path = os.path.join(STOPWORDS_PATH, file)
        os.makedirs(STOPWORDS_PATH, exist_ok=True)
        with open(file_path, "w") as f:
            _ = f.write("\n".join(stop_words))
        return stop_words
    
    def transform(self, raw_documents):
        return super().transform(raw_documents)
