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
raw_data_dir = Path("/home/victoria/aki-forecaster/data/raw")
print("Loading height-weight-dob table...")
hwd = pd.read_csv(raw_data_dir / "height_weight.csv").rename(
    columns={"value": "height", "valueuom": "height_units", "patientweight": "weight"}
)
print("Loading admissions table...")
admissions = (
    pd.read_csv(raw_data_dir / "admissions.csv")
    .drop_duplicates(subset="subject_id", keep="first", inplace=False)
    .reset_index(drop=True)
)
print("Finished loading data.")


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


def process_demographics(subj_id, grp_df):
    df = grp_df.sort_values(by="chart_charttime")
    return df.apply(get_last_non_nan_value, axis=0).to_dict()


# Get only columns we need
hwd = hwd.loc[:, ["subject_id", "chart_charttime", "gender", "dob", "height", "weight"]]
# Converts height based on units
hwd.height = hwd.apply(normalize_value, axis=1)
# Gets rid of invalid height values
hwd.height = hwd.height.apply(remove_invalid_height)


# Use Concurrent pkg to parallelize featurization
executor = ProcessPoolExecutor()
jobs = [
    executor.submit(process_demographics, subj_id, grp_df)
    for subj_id, grp_df in hwd.groupby("subject_id")
]

results = []
for job in tqdm(as_completed(jobs), total=len(jobs)):
    results.append(job.result())


demographics = pd.DataFrame(results)

# Uncomment to save
# demographics.to_csv(
#     Path(
#         "/home/victoria/predicting-insulin-regimen/patients_demographics_processed.csv"
#     )
# )
#%% [markdown]
# Now we have cleaned demographics, which we will join with hospital admissions table
#%%

demographics = pd.read_csv(
    Path.cwd() / "patients_demographics_processed.csv", header=0, index_col=0
)


#%% Merge Admissions data & Convert Dates

pt_info = pd.merge(
    admissions.loc[:, ["subject_id", "admittime", "ethnicity"]],
    demographics,
    how="inner",
    on=["subject_id"],
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


pt_info.chart_charttime = pt_info.chart_charttime.apply(str_to_datetime)
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
save_filename = Path.cwd() / "patients_hwd_adm.csv"
pt_info.to_csv(save_filename)
print(f"Saved file: {save_filename}")
