import os

import math

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from notebooks.config import MODELS_PATH

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
        custom_stop_words: str = None,
        n_custom_stop_words: int = 100
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
        self.positive_values = positive_values
        self.custom_stop_words = custom_stop_words
        self.n_custom_stop_words = n_custom_stop_words
        self.split_value = 0
  
    def fit_transform(self, raw_documents:list[str], y:list[str]):
        negative_values = list(set(y).difference(set([self.positive_values])))[0]

        difference = self.calculate_metric(raw_documents, y, negative_values)

        vocabulary = self._select_vocabulary(difference, negative_values)
        self.vocabulary = vocabulary
        
        return super().fit_transform(raw_documents, y)
 
    def calculate_metric(self, raw_documents:list[str], y:list[str], negative_values: str):
        metric = self._calculate_absolute_frequencies(raw_documents, y)

        metric["diff"] = metric[self.positive_values] - metric[negative_values]

        return metric

    def _calculate_absolute_frequencies(self, raw_documents, y=None):
        X = super().fit_transform(raw_documents, y)
        total_frequencies = (
            pd.DataFrame(X.toarray(), columns=self.get_feature_names_out(), index=y)
            .groupby(level=0).sum()
            .T
            .reset_index(names="vocabulary")
        )
        if self.custom_stop_words == "zipf":
            total_frequencies = self._remove_zipf_stopwords(total_frequencies)
        return total_frequencies
    
    def _select_vocabulary(self, difference: pd.DataFrame, negative_values: str):
        if (len(difference)*2) <= (self.dimension):
            vocabulary = difference.vocabulary.to_list()
        else:
            n = math.ceil(int(self.dimension / 2))
            pos_voc = (
                difference[difference["diff"]>=self.split_value]
                .sort_values(
                    by=["diff", self.positive_values, negative_values],
                    ascending=[False, False, True]
                )
                .head(n)
                .vocabulary
                .to_list()
            )
            neg_voc = (
                difference[difference["diff"]<self.split_value]
                .sort_values(
                    by=["diff", negative_values, self.positive_values],
                    ascending=[True, False, True]
                )
                .head(n)
                .vocabulary
                .to_list()
            )
            vocabulary = pos_voc+neg_voc
        return vocabulary

    def _remove_zipf_stopwords(self, frequencies):
        stop_words = self._get_zipf_stop_words(frequencies)
        return frequencies[~frequencies.vocabulary.isin(stop_words)]
    
    def _get_zipf_stop_words(self, frequencies):
        ids = (
            frequencies
            .drop(columns="vocabulary")
            .sum(axis=1)
            .sort_values(ascending=False)
            .head(self.n_custom_stop_words)
            .index
        )
        stop_words = (
            frequencies.iloc[ids]
            .vocabulary
            .tolist()
        )
        file = f"{self.__class__.__name__}_{self.dimension}_{self.custom_stop_words}_{self.n_custom_stop_words}_{self.positive_values}.txt"
        file_path = os.path.join(STOPWORDS_PATH, file)
        os.makedirs(STOPWORDS_PATH, exist_ok=True)
        with open(file_path, "w") as f:
            _ = f.write("\n".join(stop_words))
        return stop_words


class CustomProportionsVectorizer(CustomFrequenciesVectorizer):
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
        n_custom_stop_words: int = 100
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
            dimension=dimension,
            positive_values=positive_values,
            custom_stop_words=custom_stop_words,
            n_custom_stop_words=n_custom_stop_words
        )
        self.split_value = 0
 
    def calculate_metric(self, raw_documents:list[str], y:list[str], negative_values: str):
        metric = self._calculate_proportions(raw_documents, y)

        metric["diff"] = metric[self.positive_values] - metric[negative_values]

        metric.reset_index(inplace=True, drop=True)
        return metric
    
    def _calculate_proportions(self, raw_documents:list[str], y:list[str]):
        total_frequencies = self._calculate_absolute_frequencies(raw_documents, y)
        proportions = (
            total_frequencies
            .drop(columns="vocabulary")
            .div(
                total_frequencies.drop(columns="vocabulary").sum()
            )
            .merge(
                total_frequencies.filter(items=["vocabulary"]),
                right_index=True,
                left_index=True,
                how="left"
            )
            [total_frequencies.columns.to_list()]
        )
        return proportions


class CustomOddsRatioVectorizer(CustomProportionsVectorizer):
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
        n_custom_stop_words: int = 100,
        smooth: float = None
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
            dimension=dimension,
            custom_stop_words=custom_stop_words,
            n_custom_stop_words=n_custom_stop_words,
            positive_values=positive_values
        )
        self.split_value = 1
        self.smooth = smooth

    def calculate_metric(self, raw_documents:list[str], y:list[str], negative_values: str):
        metric = self._calculate_odds(raw_documents, y, negative_values)
        
        metric["diff"] = metric[self.positive_values]/metric[negative_values]

        metric.reset_index(inplace=True, drop=True)
        return metric

    def _calculate_odds(self, raw_documents:list[str], y:list[str], negative_values: str) -> pd.DataFrame:
        metric = self._calculate_proportions(raw_documents, y)

        if self.smooth:
            metric[[self.positive_values, negative_values]] = (
                metric[[self.positive_values, negative_values]]
                .applymap(lambda x: x+self.smooth if x == 0 else x)
            )

        metric[[self.positive_values, negative_values]] = (
            metric[[self.positive_values, negative_values]]
            .applymap(
                lambda x: x/(1-x)
            )
        )
        return metric


class CustomLogOddsRatioVectorizer(CustomOddsRatioVectorizer):
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
        smooth: float = None
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
            dimension=dimension,
            custom_stop_words=custom_stop_words,
            n_custom_stop_words=n_custom_stop_words,
            positive_values=positive_values,
            smooth=smooth
        )
        self.split_value = 0
 
    def calculate_metric(self, raw_documents:list[str], y:list[str], negative_values: str):
        count_difference = super().calculate_metric(raw_documents, y, negative_values)
        count_difference["diff"] = np.log(count_difference["diff"])

        return count_difference


class CustomTfidfVectorizer(CustomProportionsVectorizer):
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
            dtype=dtype,
            dimension=dimension,
            custom_stop_words=custom_stop_words,
            n_custom_stop_words=n_custom_stop_words,
            positive_values=positive_values
        )
        self.log_idf = log_idf
        self.split_value = 0
 
    def calculate_metric(self, raw_documents:list[str], y:list[str], negative_values: str):
        proportions = self._calculate_proportions(raw_documents, y)

        vectorizer = CountVectorizer(lowercase=True)
        X = vectorizer.fit_transform(raw_documents)
        X = X.toarray()
        tf_idf = (
            pd.DataFrame(X, columns=vectorizer.get_feature_names_out())
            .sum(axis=0)
            .to_frame("df")
            .reset_index(names="vocabulary")
            .merge(proportions, on="vocabulary", how="right")
            [proportions.columns.to_list()+["df"]]
        )
        
        if self.log_idf:
            tf_idf["log_idf"] = tf_idf.df.apply(lambda x: math.log(1/x))
            tf_idf = (
                tf_idf
                .assign(
                    **{
                        self.positive_values: (
                            tf_idf.apply(lambda x: x[self.positive_values]*x.log_idf, axis=1)
                        ),
                        negative_values: (
                            tf_idf.apply(lambda x: x[negative_values]*x.log_idf, axis=1)
                        ) 
                    }
                )
                .assign(diff=lambda x: x[self.positive_values] - x[negative_values])
            )
        else:
            tf_idf = (
                tf_idf
                .assign(
                    **{
                        self.positive_values: (
                            tf_idf.apply(lambda x: x[self.positive_values]/x.df, axis=1)
                        ),
                        negative_values: (
                            tf_idf.apply(lambda x: x[negative_values]/x.df, axis=1)
                        ) 
                    }
                )
                .assign(diff=lambda x: x[self.positive_values] - x[negative_values])
            )

        return tf_idf[proportions.columns.to_list()+["diff"]]
    
        return super().transform(raw_documents)

class CustomWordScoresVectorizer(CustomProportionsVectorizer):
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

    def calculate_metric(self, raw_documents:list[str], y:list[str], negative_values: str):
        frequencies = self._calculate_absolute_frequencies(raw_documents, y)

        proportions = self._calculate_proportions(raw_documents, y)
        
        wkw = (
            (proportions[self.positive_values]-proportions[negative_values])/
            (proportions[self.positive_values]+proportions[negative_values])
        )
        nkw = frequencies[[self.positive_values,negative_values]].sum(axis=1)

        metric = (
            pd
            .DataFrame({
                "vocabulary": frequencies.vocabulary,
                self.positive_values: wkw*nkw,
                negative_values: wkw*nkw,
                "diff": wkw*nkw,
            })
        )
        return metric
