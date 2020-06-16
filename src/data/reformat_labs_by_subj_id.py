# %% import libraries
import pandas as pd
import numpy as np
from pathlib import Path
from concurrent.futures import as_completed, ProcessPoolExecutor
from tqdm.autonotebook import tqdm


#%% [markdown]
# Save Lab Files by Subject ID
# %% Load Labs Table
print("Loading labs table...")
data_dir = Path("/home/victoria/aki-forecaster/data/raw")
lab_table = pd.read_csv(data_dir / "lab_events.csv").rename(
    columns={"labevents_itemid": "itemid"}
)
print("Loaded")

#%% Load Lab Items ID Table
lab_ids = pd.read_csv(data_dir / "lab_items_id.csv")


def simplify_label(label: str) -> str:
    "Simplifies `label` with comma in it by dropping after comma."
    split_label = label.split(", ")
    if len(split_label) == 1:
        return label
    elif split_label[1] in ("Whole Blood", "Blood", "Urine", "Calculated"):
        return split_label[0]
    else:
        return label


def uniquify_label(row: pd.Series):
    "Uniquifies `label` by appending abbreviated `fluid` and `category`"

    label = simplify_label(row.label)

    if row.fluid.lower() == "blood":
        fluid_str = "B"
    elif row.fluid.lower() == "urine":
        fluid_str = "U"
    else:
        fluid_str = "X"
    if row.category.lower() == "hematology":
        cat_str = "H"
    elif row.category.lower() == "chemistry":
        cat_str = "C"
    elif row.category.lower() == "blood gas":
        cat_str = "G"
    else:
        cat_str = "X"

    new_label = label + f"[{fluid_str}-{cat_str}]"
    return new_label


# Create mapping from lab ID to name
lab_ids["name"] = lab_ids.apply(uniquify_label, axis=1)
# Save Updated Lab ID Table with Names
lab_ids.to_csv(data_dir / "lab_items_id_with_names.csv")
# Create Dict mapping lab IDs to names
lab_id_to_name = {k: v for k, v in lab_ids.loc[:, ["itemid", "name"]].values}
#%% [markdown]
# Generate Dataframe of Labs for each SubjectID
#%%


def pivot_labs_and_save(subj_id, subj_id_grp) -> pd.DataFrame:
    "Pivotes Long Table of Lab IDs for each SubjectID to unique LabID per col, saves file."
    # Pivot Labs for each Subject ID
    pivoted = pd.pivot_table(
        subj_id_grp,
        values="labevents_value",
        index="charttime",
        columns="itemid",
        aggfunc=list,
    ).applymap(lambda x: x[0] if isinstance(x, list) else x)
    # Not all Subjects have every lab.  Normalize cols in all subjects by adding np.nan columns
    cols_to_add = [col for col in lab_id_to_name.keys() if col not in pivoted.columns]
    for col in cols_to_add:
        pivoted[col] = np.nan
    # Rename columns using `name` instead of `lab id`
    pivoted = pivoted.rename(columns=lab_id_to_name)
    # Save File
    data_dir = Path("/home/victoria/aki-forecaster/data/interim")
    save_filename = data_dir / "subj_id_labs" / f"{subj_id}.csv"
    pivoted.to_csv(save_filename)
    # print(f"Saved file: {save_filename}")


# Use Concurrent To Save Files in Parallel
executor = ProcessPoolExecutor()
jobs = [
    executor.submit(pivot_labs_and_save, subj_id, subj_id_grp)
    for subj_id, subj_id_grp in lab_table.groupby("subject_id")
]

results = []
for job in tqdm(as_completed(jobs), total=len(jobs)):
    results.append(job.result())

print("All patient tables are pivoted and saved!")
#%%
# Restore dataframe from CSV file
# dir = Path("/home/victoria/aki-forecaster/data/interim")
# res = pd.read_csv(dir / "subj_id_labs" / "3.csv", header=[0, 1], index_col=0)
# res
