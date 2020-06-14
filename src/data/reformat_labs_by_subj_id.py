# %% import libraries
import pandas as pd
from pathlib import Path
from concurrent.futures import as_completed, ProcessPoolExecutor
from tqdm.autonotebook import tqdm

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

#%% [markdown]
# Save Lab Files by Subject ID
# %% Load Labs Table
print("Loading labs table...")
lab_table = pd.read_csv(Path.cwd() / "labevents_of_patients.csv")
print("Loaded")


def pivot_labs_and_save(subj_id, subj_id_grp) -> pd.DataFrame:
    data_dir = Path("/home/victoria/aki-forecaster/data/interim")
    pivoted = pd.pivot_table(
        subj_id_grp,
        values=["labevents_value", "labevents_flag"],
        index="labevents_charttime",
        columns="labitems_label",
        aggfunc=list,
    ).applymap(lambda x: x[0] if isinstance(x, list) else x)
    save_filename = data_dir / "subj_id_labs" / f"{subj_id}.csv"
    pivoted.to_csv(save_filename)
    # print(f"Saved file: {save_filename}")


# Use Concurrent To Save Files in Paralle
executor = ProcessPoolExecutor()
jobs = [
    executor.submit(pivot_labs_and_save, subj_id, subj_id_grp)
    for subj_id, subj_id_grp in lab_table.groupby("subject_id")
]

results = []
for job in tqdm(as_completed(jobs), total=len(jobs)):
    results.append(job.result())


#%%
# Restore dataframe from CSV file
# dir = Path("/home/victoria/aki-forecaster/data/interim")
# res = pd.read_csv(dir / "subj_id_labs" / "3.csv", header=[0, 1], index_col=0)
# res
