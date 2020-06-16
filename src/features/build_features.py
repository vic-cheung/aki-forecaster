#%%
import pandas as pd
from pathlib import Path
from src.features.featurizations import featurize
from concurrent.futures import as_completed, ProcessPoolExecutor
from tqdm.autonotebook import tqdm

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


#%%
# Paths to Each Patient's Lab Data
subj_id_labs = Path("/home/victoria/aki-forecaster/data/interim/subj_id_labs")
csv_files = [file for file in subj_id_labs.iterdir()]

#%%
# Make all labels unique by simplfying & then adding fluid & category info
data_dir = Path("/home/victoria/aki-forecaster/data/raw")

# %%
# Use Concurrent to featurize samples
executor = ProcessPoolExecutor()
jobs = [executor.submit(featurize, csv_file) for csv_file in tqdm(csv_files[:5])]

results = []
for job in tqdm(as_completed(jobs), total=len(jobs)):
    if job.result() is not None:
        results.append(job.result())

# Remove `None` Results
results = [x for x in results if pd.notnull(x)]

# Concatenate x's & y's derived from each patient into single `X` and `Y` matrix
X = pd.concat([item["x"] for item in results], axis=0)
Y = pd.concat([item["y"] for item in results], axis=0)

# %%
# Save Train Data
processed_dir = Path("/home/victoria/aki-forecaster/data/processed")
X.to_csv(processed_dir / "X.csv")
Y.to_csv(processed_dir / "Y.csv")
