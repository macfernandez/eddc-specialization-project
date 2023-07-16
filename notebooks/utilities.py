import os
import pandas as pd


def save_dataframe(dataframe: pd.DataFrame, folder: str, filename: str, latex: bool=True):
    file_path = os.path.join(folder, filename)
    dataframe.to_csv(f"{file_path}.csv", index=False)
    if latex:
        dataframe.to_latex(f"{file_path}.tex", index=False)