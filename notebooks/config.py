import os
import sys

import seaborn as sns


notebooks_dir = os.path.dirname(os.getcwd())
sys.path.append(notebooks_dir)

HERE = os.getcwd()
PROJECT_PATH = os.path.dirname(HERE)
DATA_PATH = os.path.join(PROJECT_PATH, "data")
VISUALIZATIONS_PATH = os.path.join(PROJECT_PATH, "visualizations")
MODELS_PATH = os.path.join(PROJECT_PATH, "models")

sns.set_style("whitegrid")