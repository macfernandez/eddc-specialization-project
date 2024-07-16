import os

import seaborn as sns


HERE = os.getcwd()
PROJECT_PATH = os.path.dirname(HERE)
DATA_PATH = os.path.join(PROJECT_PATH, "data")
VISUALIZATIONS_PATH = os.path.join(PROJECT_PATH, "visualizations")

sns.set_style("whitegrid")