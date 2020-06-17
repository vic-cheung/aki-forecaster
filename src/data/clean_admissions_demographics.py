# %% import libraries
import pandas as pd
import numpy as np

# import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import as_completed, ProcessPoolExecutor
from tqdm.autonotebook import tqdm
from typing import Union

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

#%% [markdown]
# Load, clean, extract demographic & height-weight information
# %% Load Height, Weight, Date of Birth Table
raw_data_dir = Path("/home/victoria/aki-forecaster/data/raw_hadmid")
print("Loading heights table...")
heights = pd.read_csv(raw_data_dir / "heights.csv").rename(
    columns={"valueuom": "height_units"}
)

print("Loading weights table...")
weights = pd.read_csv(raw_data_dir / "weights.csv").rename(
    columns={"patientweight": "weight"}
)

print("Loading admissions table...")
admissions = (
    pd.read_csv(raw_data_dir / "admissions.csv")
    .drop_duplicates(subset="hadm_id", keep="first", inplace=False)
    .reset_index(drop=True)
)
print("Finished loading data.")


# %%
def normalize_value(row: pd.Series):
    "Normalizes units of `height` to `inches` based on `height_units`."
    if isinstance(row.height_units, str):
        units = row.height_units.lower()
        height = row.height
        if units in ("inches", "inch", "in"):
            return height
        elif units in ("cm"):
            return height / 2.54
        elif np.isnan(units):
            return np.nan
        else:
            return "Unknown"
    else:
        return np.nan


def remove_invalid_height(height: float):
    "Remove invalid heights"
    if height <= 24.0:  # Shorter than shortest person in world in inches
        return np.nan
    elif height >= 107.0:  # Taller than tallest person in world in inches
        return np.nan
    else:
        return height


def get_last_non_nan_value(series: pd.Series):
    "For each series, get only last non-NaN value.  If none exist, return `NaN`."
    count = 1
    value = np.nan
    while pd.isnull(value) and (count <= len(series)):
        value = series.iloc[-1 * count]
        count += 1
    return value


def process_htwt(hadm_id, grp_df):
    df = grp_df.sort_values(by="charttime")
    return df.apply(get_last_non_nan_value, axis=0).to_dict()


# %%
htwt = heights.append(weights)

# Get only columns we need
htwt = htwt.loc[:, ["hadm_id", "charttime", "weight", "height", "height_units"]]
# Converts height based on units
htwt.height = htwt.apply(normalize_value, axis=1)
# Gets rid of invalid height values
htwt.height = htwt.height.apply(remove_invalid_height)


# Use Concurrent pkg to parallelize featurization
executor = ProcessPoolExecutor()
jobs = [
    executor.submit(process_htwt, hadm_id, grp_df)
    for hadm_id, grp_df in htwt.groupby("hadm_id")
]

results = []
for job in tqdm(as_completed(jobs), total=len(jobs)):
    results.append(job.result())


height_weight = pd.DataFrame(results)
height_weight = height_weight.loc[:, ["hadm_id", "charttime", "weight", "height"]]
# Uncomment to save
# height_weight.to_csv(
#     Path(
#         "/home/victoria/aki-forecaster/data/interim/hadmid_height_weight_processed.csv"
#     )
# )
#%% [markdown]
# Now we have cleaned demographics, which we will join with hospital admissions table
#%%

height_weight = pd.read_csv(
    Path(
        "/home/victoria/aki-forecaster/data/interim/hadmid_height_weight_processed.csv"
    ),
    header=0,
    index_col=0,
)


#%% Merge Admissions data & Convert Dates

pt_info = pd.merge(
    admissions.loc[:, ["hadm_id", "admittime", "gender", "ethnicity", "dob"]],
    height_weight,
    how="left",
    on=["hadm_id"],
)


def str_to_datetime(
    string: Union[str, float], format: str = "%Y-%m-%d %H:%M:%S"
) -> datetime:
    "Converts datetime string to `datetime.datetime` object."
    if pd.isnull(string):
        return np.nan
    elif isinstance(string, str):
        return datetime.strptime(string, format)
    else:
        return "Unknown Type"


pt_info.charttime = pt_info.charttime.apply(str_to_datetime)
pt_info.admittime = pt_info.admittime.apply(str_to_datetime)
pt_info.dob = pt_info.dob.apply(lambda s: s.split(" ")[0]).apply(
    str_to_datetime, format="%Y-%m-%d"
)


def estimate_age(admittime: datetime, birthdate: datetime):
    if pd.notnull(admittime) and pd.notnull(birthdate):
        age = admittime - birthdate
    else:
        age = np.nan
    return age


pt_info["age"] = pt_info.apply(
    lambda row: estimate_age(row.admittime.year, row.dob.year), axis=1
).apply(lambda age: 89 if (age == 300) else age)

#%% Save Merged & Processed Demographics & Hospital Admission Dataferame
save_dir = Path("/home/victoria/aki-forecaster/data/processed")
save_filename = save_dir / "hadmid_ht_wt_demographics.csv"
pt_info.to_csv(save_filename)
print(f"Saved file: {save_filename}")


# %%
