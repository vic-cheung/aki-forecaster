import pandas as pd
from pathlib import Path
from concurrent.futures import as_completed, ProcessPoolExecutor
from tqdm.autonotebook import tqdm

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


#%%
# Paths to Each Patient's Lab Data
subj_id_labs = Path("/home/victoria/aki-forecaster/data/interim/subj_id_labs")
csv_files = [file for file in subj_id_labs.iterdir()]


def create_samples(data: pd.DataFrame, window: int = 3):
    """Transforms raw labs data for 1 patient into multiple samples
    by sliding a window across time to define `X` and `Y`.

    `X` is all lab values in days specified in `window`
    `Y` is all lab values in day following `X`
    """
    # col_to_drop = [
    #     "Platelet Smear",
    #     "Sodium, Whole Blood",
    #     "Potassium, Whole Blood",
    #     "Chloride, Whole Blood",
    #     "Hematocrit, Calculated",
    #     "WBCP",
    #     "Calculated Bicarbonate, Whole Blood",
    #     "Anti-Neutrophil Cytoplasmic Antibody",
    # ]
    # for col in col_to_drop:
    #     if col in data.columns:
    #         data = data.drop(columns=col)

    # Make index datetime
    data.index = pd.to_datetime(data.index)
    # Interpolate NaN values
    data = data.interpolate(limit_direction="both")

    # Create Dataset
    X_data_raw = []
    Y_data_raw = []

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
            if not y.Creatinine.empty:
                # Add X to Dataset
                X_data_raw += [x]
                # Add Y to Dataset
                Y_data_raw += [y]

        # Move Start Interval
        start_date = start_date + pd.Timedelta(days=1)
    return X_data_raw, Y_data_raw


def featurize_X(X_data_raw: pd.DataFrame):
    "Returns pd.DataFrame of Labs"
    X = []
    for x in X_data_raw:
        mean = x.mean()
        mean.index = [item + "_avg" for item in mean.index]
    X = pd.DataFrame(X)
    return X


def featurize_Y(Y_data_raw: pd.DataFrame):
    "Returns pd.Series of Creatinine for day after X"
    Y_cr_only = [Y.Creatinine for Y in Y_data_raw]
    Y = pd.Series([item.mean() for item in Y_cr_only], name="Creatinine_avg")
    return Y


def featurize(csv_file):
    """Generate final `X` & `Y` dataframes used for modeling.
    Splits raw lab data into samples based on sliding window in `create_samples`.
    Featurize `X`, then Featurize `Y.  Returns `X` & `Y`.
    """
    pt_data = pd.read_csv(csv_file, header=[0, 1], index_col=0).labevents_value

    # Only create training example if patient has Creatinine Value
    if "Creatinine" in pt_data.columns:
        # Try to Preprocess Data
        try:
            X_train_raw, Y_train_raw = create_samples(pt_data)
            x = featurize_X(X_train_raw)
            y = featurize_Y(Y_train_raw)
            return (x, y)
        # If Error occurs, skip patient
        except Exception as e:
            print(f"Error occurred in file: {csv_file}.  Error: {e}")


# Use Concurrent to featurize samples
executor = ProcessPoolExecutor()
jobs = [executor.submit(featurize, csv_file) for csv_file in tqdm(csv_files)]

X, Y = [], []
for job in tqdm(as_completed(jobs), total=len(jobs)):
    x, y = job.result()
    X.append(x)
    Y.append(y)

# Join all featurized samples
X = pd.concat(X, axis=0)
Y = pd.concat(Y, axis=0)

# Save Train Data
processed_dir = Path("/home/victoria/aki-forecaster/data/processed")
X.to_csv(processed_dir / "X.csv")
Y.to_csv(processed_dir / "Y.csv")
