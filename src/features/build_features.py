import pandas as pd
from pathlib import Path
from src.features.featurizations import featurize
from concurrent.futures import as_completed, ProcessPoolExecutor
from tqdm.autonotebook import tqdm

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


#%% Paths to Each Patient's Lab Data
hadm_id_labs = Path("/home/victoria/aki-forecaster/data/interim/hadm_id_labs")
csv_files = [file for file in hadm_id_labs.iterdir()]

#%% Make all labels unique by simplfying & then adding fluid & category info
data_dir = Path("/home/victoria/aki-forecaster/data/raw")

# %% Use Concurrent to featurize samples
executor = ProcessPoolExecutor()
jobs = [executor.submit(featurize, csv_file) for csv_file in csv_files]

X, Y = [], []
for job in tqdm(as_completed(jobs), total=len(jobs)):
    result = job.result()
    if result:
        x, y = result
        X.append(x)
        Y.append(y)

# Remove `None` Results
X = [item for item in X if not item.empty]
Y = [item for item in Y if not item.empty]

# Join all featurized samples
X = pd.concat(X, axis=0)
Y = pd.concat(Y, axis=0)

# %% Save Train Data
processed_dir = Path(
    "/home/victoria/aki-forecaster/data/processed/continuous_vars_only/hadm_id_window1"
)
X.to_csv(processed_dir / "X.csv")
Y.to_csv(processed_dir / "Y.csv")
