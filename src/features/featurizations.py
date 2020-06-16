# %%
import pandas as pd
import numpy as np
from pathlib import Path

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

#%%
subj_id_labs = Path("/home/victoria/aki-forecaster/data/interim/subj_id_labs")
csv_files = [file for file in subj_id_labs.iterdir()]
csv_file = csv_files[1]
pt_data = pd.read_csv(csv_file, header=0, index_col=0)
res = pt_data.loc[:, ~pt_data.columns.str.contains(pat="_cat")]
#%%
# pt_data = pt_data.fillna("None")
#%%
# series = pt_data["Nitrite[U-H]"]


# def categorical_to_one_hot(series: pd.Series) -> pd.DataFrame:
#     "Transforms all categorical columns into multiple one-hot columns."
#     categories = series.unique()
#     encoder = OneHotEncoder()
#     # Generate OneHotEncoder
#     encoder.fit(categories.reshape(-1, 1))
#     # Transform all values in series to One-Hot Encoding
#     one_hot = encoder.transform(series.values.reshape(-1, 1)).toarray()
#     # Return pd.DataFrame that is original Series in One-Hot Encoding
#     one_hot_column_names = [series.name + ">" + cat for cat in encoder.categories_]
#     return pd.DataFrame(one_hot, columns=one_hot_column_names).as


# res = categorical_to_one_hot(series)

#%%

#%%


def create_samples(data: pd.DataFrame, window: int = 3):
    """Transforms raw labs data for 1 patient into multiple samples
    by sliding a window across time to define `X` and `Y`.

    `X` is all lab values in days specified in `window`
    `Y` is all lab values in day following `X`
    """

    # Make index datetime
    data.index = pd.to_datetime(data.index)

    # # Identify Categorical & Continuous Features
    # categorical = [
    #     "Anti-Neutrophil Cytoplasmic Antibody[B-C]",
    #     "Blood[U-H]",
    #     "Nitrite[U-H]",
    #     "Platelet Smear[B-H]",
    #     "Urine Appearance[U-H]",
    #     "Urine Color[U-H]",
    #     "Yeast[U-H]",
    # ]
    # continuous = list(np.setdiff1d(data.columns, categorical))
    # # Interpolate NaN values of numerical features
    data = data.apply(pd.to_numeric, errors="coerce").interpolate(
        limit_direction="both"
    )
    # )
    # #
    # try:
    #     cat_mode = data.loc[:, categorical].mode().to_dict("r")[0]  # Create Dataset
    #     data = data.fillna(value=cat_mode)
    # except Exception:
    #     print("No values in cat_mode")

    X_raw = []
    Y_raw = []

    # get midnight (start of first day)
    last_date = data.index[-1]
    start_date = pd.Timestamp(data.index[0].date())
    while start_date < (last_date - pd.Timedelta(days=window + 1)):
        # Define X Date Interval
        X_start = start_date
        X_end = start_date + pd.Timedelta(days=window)
        # Define Y Date Interval
        Y_start = X_end
        Y_end = X_end + pd.Timedelta(days=1)

        # Get X Data
        x = data.loc[(data.index >= X_start) & (data.index < X_end)]
        y = data.loc[(data.index >= Y_start) & (data.index < Y_end)]

        # Only add x & y if both are not empty dataframes
        # and if there is a `y` label
        if (not x.empty) and (not y.empty):
            if not y["Creatinine[B-C]"].empty:
                # Add X to Dataset
                X_raw += [x]
                # Add Y to Dataset
                Y_raw += [y]

        # Move Start Interval
        start_date = start_date + pd.Timedelta(days=1)
    return X_raw, Y_raw


def featurize_X(X_raw: pd.DataFrame):
    "Returns pd.DataFrame of Labs"
    X = []
    means_raw = []
    for x in X_raw:
        means = x.mean()
        means_raw += [means]
    X = pd.DataFrame(means_raw)
    return X


def featurize_Y(Y_raw: pd.DataFrame):
    "Returns pd.Series of Creatinine for day after X"
    Y_cr_only = [Y["Creatinine[B-C]"] for Y in Y_raw]
    Y = pd.Series([item.mean() for item in Y_cr_only], name="Creatinine_avg")
    return Y


def featurize(csv_file):
    """Generate final `X` & `Y` dataframes used for modeling.
    Splits raw lab data into samples based on sliding window in `create_samples`.
    Featurize `X`, then Featurize `Y.  Returns `X` & `Y`.
    """
    pt_data = pd.read_csv(csv_file, header=0, index_col=0)
    pt_data = pt_data.loc[:, ~pt_data.columns.str.contains(pat="_cat")]
    pt = int(csv_files[1].name.split(".")[0])
    demographics = pd.read_csv(
        Path(
            "/home/victoria/aki-forecaster/data/processed/patients_ht_wt_demographics.csv"
        ),
        header=0,
        index_col=0,
    )
    pt_demographics = demographics[demographics["subject_id"] == pt].loc[
        :, ["gender", "ethnicity", "weight", "height", "age"]
    ]
    demographics_dict = pt_demographics.to_dict("records")[0]
    # Only create training example if patient has Creatinine Value (corresponding to itemid: 50912)
    if "Creatinine[B-C]" in pt_data.columns:
        # Try to Preprocess Data
        try:
            X_raw, Y_raw = create_samples(pt_data)
            x = featurize_X(X_raw)
            y = featurize_Y(Y_raw)
            for col in pt_demographics.columns:
                x[col] = np.nan
            x = x.fillna(demographics_dict)
            return x, y
            if x.empty or y.empty:
                return None
            else:
                return {"x": x, "y": y}
        # If Error occurs, skip patient
        except Exception as e:
            print(f"Error occurred in file: {csv_file}.  Error: {e}")
            return None


# %%
