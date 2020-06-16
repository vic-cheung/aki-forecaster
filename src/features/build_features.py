#%%
import pandas as pd
from pathlib import Path
from src.features.featurizations import featurize, uniquify_label
from concurrent.futures import as_completed, ProcessPoolExecutor
from tqdm.autonotebook import tqdm

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


#%%
# Paths to Each Patient's Lab Data
subj_id_labs = Path("/home/victoria/aki-forecaster/data/interim/subj_id_labs_itemid")
csv_files = [file for file in subj_id_labs.iterdir()]

#%%
# Make all labels unique by simplfying & then adding fluid & category info
data_dir = Path("/home/victoria/aki-forecaster/data/raw")
lab_ids = pd.read_csv(data_dir / "lab_items_id.csv")
renamed_labels = lab_ids.apply(uniquify_label, axis=1)
lab_ids["renamed_label"] = renamed_labels
labs_to_include = lab_ids.itemid.to_list()

new_col_names = dict(
    zip([str(item) for item in lab_ids.itemid], lab_ids.renamed_label,)
)


# %%
# Use Concurrent to featurize samples
executor = ProcessPoolExecutor()
jobs = [
    executor.submit(featurize, csv_file, labs_to_include)
    for csv_file in tqdm(csv_files[:100])
]

results = []
for job in tqdm(as_completed(jobs), total=len(jobs)):
    if job.result() is not None:
        results.append(job.result())

# Remove `None` Results
results = [x for x in results if pd.notnull(x)]

# Concatenate x's & y's derived from each patient into single `X` and `Y` matrix
X = pd.concat([item["x"] for item in results], axis=0).rename(columns=new_col_names)
Y = pd.concat([item["y"] for item in results], axis=0)

# %%
# Save Train Data
processed_dir = Path("/home/victoria/aki-forecaster/data/processed")
X.to_csv(processed_dir / "X.csv")
Y.to_csv(processed_dir / "Y.csv")
