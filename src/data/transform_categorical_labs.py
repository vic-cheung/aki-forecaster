#%%
import pandas as pd
import numpy as np
from pathlib import Path
import collections
import pickle
from concurrent.futures import as_completed, ProcessPoolExecutor
from tqdm.autonotebook import tqdm
from sklearn.preprocessing import OneHotEncoder

data_dir = Path("/home/victoria/aki-forecaster/data/interim/subj_id_labs")
csv_files = [file for file in data_dir.iterdir()]

categorical = [
    "Anti-Neutrophil Cytoplasmic Antibody[B-C]",
    "Blood[U-H]",
    "Nitrite[U-H]",
    "Platelet Smear[B-H]",
    "Urine Appearance[U-H]",
    "Urine Color[U-H]",
    "Yeast[U-H]",
]
res = pt_data.loc[:, ~pt_data.columns.str.contains(pat="_cat")]
#%%
# pt_data = pt_data.fillna("None")
# series = pt_data["Nitrite[U-H]"]


def get_unique_categorical_values(csv_file):
    "Return dictionary of all unique categorical values"
    # Load Data
    data = pd.read_csv(csv_file, header=0, index_col=0)
    # Get Only categorical columns
    data_categorical = (
        data.loc[:, categorical]
        .fillna("zz")
        .applymap(str)
        .applymap(lambda x: x.lower())
    )
    # continuous = [col for col in data.columns if col not in categorical]
    # Get Unique values for Categorical Columns
    categorical_values = data_categorical.apply(lambda x: x.unique().tolist(), axis=0)
    return {k: v for k, v in categorical_values.items()}


# Use Concurrent To Get All Unique Categorical Values for labs across all Subj_ID in Parallel
# Submit parallel jobs
executor = ProcessPoolExecutor()
jobs = [
    executor.submit(get_unique_categorical_values, csv_file) for csv_file in csv_files
]

results = []
for job in tqdm(as_completed(jobs), total=len(jobs)):
    results.append(job.result())

# Uniquify results across all jobs
all_unique_cat_values = collections.defaultdict(set)
for d in results:
    for k, v in d.items():
        all_unique_cat_values[k].update(set(v))


#%% [markdown]
# TODO:
# 1. for each patient, lower case all your categorical data columns
# 2. --skrun `transform_categorical_labs` up until now
# 3. use values in `all_unique_cat_values` for each lab type (e.g. `Blood[U-H]`) ...
#     ... and transform each categorical column (series) into one-hot dataframe equivalent
# 4. delete orig. categorical columns from each patient's data, and concat one-hot dataframe equivalent


#%%
# Save Unique Categorical Values
# save_path = Path("/home/victoria/aki-forecaster/data/interim/categorical_values.pkl")
# with open(save_path, "wb") as f:
#     pickle.dump(all_unique_cat_values, f, pickle.HIGHEST_PROTOCOL)

#%%
# with open(save_path, "rb") as f:
#     res = pickle.load(f)
#%%
# data_categorical.apply(lambda x: x.unique().tolist(), axis=0)

# #%%
# subj_id_labs = Path("/home/victoria/aki-forecaster/data/interim/subj_id_labs")
# csv_files = [file for file in subj_id_labs.iterdir()]
# csv_file = csv_files[1]
# pt_data = pd.read_csv(csv_file, header=0, index_col=0)

#%%
# Generate All Possible Categorical Column Names in a One-Hot Encoding Scenario
categorical_column_names = []
for k, v in all_unique_cat_values.items():
    categorical_column_names += [k + ">" + v for v in all_unique_cat_values[k]]
#%%


def categorical_to_one_hot(series: pd.Series) -> pd.DataFrame:
    "Transforms all categorical columns into multiple one-hot columns."
    categories = series.unique()
    encoder = OneHotEncoder()
    # Generate OneHotEncoder
    encoder.fit(categories.reshape(-1, 1))
    # Transform all values in series to One-Hot Encoding
    one_hot = encoder.transform(series.values.reshape(-1, 1)).toarray()
    # Return pd.DataFrame that is original Series in One-Hot Encoding
    one_hot_column_names = [series.name + ">" + cat for cat in encoder.categories_]
    return pd.DataFrame(one_hot, columns=one_hot_column_names)


def transform_categorical_columns(csv_file):
    # Load Data
    data = pd.read_csv(csv_file, header=0, index_col=0)
    # Get Only categorical columns
    data_categorical = data.loc[:, categorical].fillna("zz").applymap(str)
    # Transform to One-Hot
    one_hotified = []
    for col in data_categorical.columns:
        one_hotified.append(categorical_to_one_hot(data_categorical.loc[:, col]))
    one_hot_categorical = pd.concat(one_hotified)
    # Add all Categorical Column Names that don't appear in data for this SubjID
    for col in categorical_column_names:
        one_hot_categorical[col] = np.nan
    # Remove Old categorical Columns
    continuous = [col for col in data.columns if col not in categorical_column_names]
    data_continuous = data.loc[:, continuous]
    # Add One-Hot Categorical Columns
    data2 = pd.concat([data_categorical, data_continuous], axis=1)
    return data2


# Use Concurrent To Get All Unique Categorical Values for labs across all Subj_ID in Parallel
# Submit parallel jobs
executor = ProcessPoolExecutor()
jobs = [
    executor.submit(transform_categorical_columns, csv_file)
    for csv_file in csv_files[:3]
]

results = []
for job in tqdm(as_completed(jobs), total=len(jobs)):
    results.append(job.result())


# pt_data = pt_data.fillna("None")
#%%
# Transform Categorical Columns into One-hot


res = categorical_to_one_hot(series)
