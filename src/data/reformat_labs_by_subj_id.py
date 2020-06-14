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
data_dir = Path("/home/victoria/aki-forecaster/data/raw")
lab_table = pd.read_csv(data_dir / "lab_events.csv")
lab_ids = pd.read_csv(data_dir / "lab_items_id.csv")

print("Loaded")


# %%
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


def pivot_labs_and_save(subj_id, subj_id_grp) -> pd.DataFrame:
    data_dir = Path("/home/victoria/aki-forecaster/data/interim")
    pivoted = pd.pivot_table(
        subj_id_grp,
        values=["labevents_value", "flag"],
        index="charttime",
        columns="label",
        aggfunc=list,
    ).applymap(lambda x: x[0] if isinstance(x, list) else x)
    save_filename = data_dir / "subj_id_labs" / f"{subj_id}.csv"
    pivoted.to_csv(save_filename)
    # print(f"Saved file: {save_filename}")


# %%
# Make all labels unique by simplfying & then adding fluid & category info
renamed_labels = lab_ids.apply(uniquify_label, axis=1)
lab_ids["renamed_label"] = renamed_labels
labs_to_include = lab_ids.itemid.to_list()
labs_to_exclude = lab_ids[
    lab_ids["label"].isin(
        [
            "Platelet Smear",
            "Sodium, Whole Blood",
            "Potassium, Whole Blood",
            "Chloride, Whole Blood",
            "Hematocrit, Calculated",
            "WBCP",
            "Calculated Bicarbonate, Whole Blood",
            "Anti-Neutrophil Cytoplasmic Antibody",
        ]
    )
].itemid

# %%
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
