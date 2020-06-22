#!/home/victoria/miniconda3/envs/mimic3/bin python
# %% import libraries
import pandas as pd

# import numpy as np
from pathlib import Path
import itertools
import collections
import pickle
from tqdm.autonotebook import tqdm
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score

# from sklearn.linear_model import LogisticRegression, LinearRegression
# from sklearn.metrics import explained_variance_score, mean_squared_error, r2_score
import xgboost as xgb

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


def named_product(**items):
    "Cartesian product with result in named tuple.  Pass in `**dict` as arg."
    Product = collections.namedtuple("Product", items.keys())
    return itertools.starmap(Product, itertools.product(*items.values()))


def create_regressors(params: dict) -> xgb.XGBRegressor:
    model = xgb.XGBRegressor(
        objective="reg:squarederror",
        learning_rate=params.learning_rate,
        max_depth=params.max_depth,
        # reg_alpha=10,
        reg_lambda=params.reg_lambda,
        n_estimators=params.n_estimators,
        subsample=params.subsample,
        colsample_bytree=params.colsample_bytree,
        random_state=123,
        # missing=-999,
    )
    return model


#%% Train Models
def train_model(model: xgb.XGBRegressor):
    print(f"Training model with parameters: \n{model.get_xgb_params()}")
    return model.fit(
        X_train.values,
        Y_train.values,
        eval_set=[(X_train.values, Y_train.values), (X_valid.values, Y_valid.values)],
        eval_metric=["rmse", "rmsle", "mae"],
    )


def train_model_and_save(
    model: xgb.XGBRegressor,
    save_folder=Path(
        "/home/victoria/aki-forecaster/models/prelim/hadm_id_hyperparam_opt3"
    ),
):
    result = train_model(model)
    # Get params for filename
    params = model.get_xgb_params()
    lr = params["learning_rate"]
    md = params["max_depth"]
    lam = params["reg_lambda"]
    n = model.n_estimators
    ss = params["subsample"]
    csbt = params["colsample_bytree"]
    # Save model file
    filename = save_folder / f"xgb_lr{lr}_n{n}_md{md}_ss{ss}_csbt{csbt}_lam{lam}.pkl"
    # pickle.dump(result, open(filename, "wb"))
    with open(filename, "wb") as f:
        pickle.dump(result, f)
    return result


# %% load data
data_dir = Path(
    "/home/victoria/aki-forecaster/data/processed/continuous_vars_only/hadm_id_window1"
)
X = pd.read_csv(data_dir / "X.csv", header=0, index_col=0,)
Y = pd.read_csv(data_dir / "Y.csv", header=0, index_col=0,)
# %% integer encode ethnicity and gender
ethnicity_id = dict(enumerate(X.ethnicity.unique().tolist()))
pd.Series(ethnicity_id).to_csv(
    Path(
        "/home/victoria/aki-forecaster/data/processed/continuous_vars_only/hadm_id_window1"
    )
    / "ethnicity_id.csv"
)
# invert keys and values so categorical becomes a number, map it onto
ethnicity_id_inverse = dict(zip(ethnicity_id.values(), ethnicity_id.keys()))
X.ethnicity = X.ethnicity.map(ethnicity_id_inverse)

gender_dict = {"M": 0, "F": 1}
X.gender = X.gender.map(gender_dict)
# %% fill NaNs with median value for XGBoost


# def median_value(series: pd.Series):
#     s = series.dropna()
#     return s.median()


# X.apply(median_value, axis=0)

#%%
X_filled = X.fillna(X.median(axis=0))
Y_filled = Y.fillna(Y.median())
# %% split training and test data
X_train, X_test, Y_train, Y_test = train_test_split(
    X_filled.reset_index(drop=True),
    Y_filled.reset_index(drop=True),
    test_size=0.2,
    random_state=123,
)
X_test, X_valid, Y_test, Y_valid = train_test_split(
    X_test, Y_test, test_size=0.5, random_state=123
)
# join test set back to train set
X_train = X_train.append(X_test)
Y_train = Y_train.append(Y_test)

# sanity check dimensions of the sets
print(
    f"""
X_train: {X_train.shape}
Y_train: {Y_train.shape}

X_valid: {X_valid.shape}
Y_valid: {Y_valid.shape}

X_test: {X_test.shape}
Y_test: {Y_test.shape}
"""
)
# Save Train Data
processed_dir = Path(
    "/home/victoria/aki-forecaster/data/processed/continuous_vars_only/hadm_id_window1"
)
X_train.to_csv(processed_dir / "X_train.csv")
Y_train.to_csv(processed_dir / "Y_train.csv")
X_valid.to_csv(processed_dir / "X_valid.csv")
Y_valid.to_csv(processed_dir / "Y_valid.csv")
X_test.to_csv(processed_dir / "X_test.csv")
Y_test.to_csv(processed_dir / "Y_test.csv")

print("Train/Validate/Test sets saved")

#%%
# Create Models with different Hyperparameters
# params = {
#     "learning_rate": [0.1, 0.3, 1.0],
#     "max_depth": [5, 10],
#     "reg_lambda": [0.1, 0.3, 1.0],
#     "n_estimators": [1000, 5000, 10000, 30000],
#     "subsample": [0.3, 0.5, 1.0],
#     "colsample_bytree": [0.3, 0.5, 1.0],
# }

# params = {
#     "learning_rate": [0.01, 0.1],
#     "max_depth": [3, 6],
#     "reg_lambda": [0.3, 1],
#     "n_estimators": [10000, 30000, 50000],
#     "subsample": [0.8],
#     "colsample_bytree": [0.8, 1.0],
# }

params = {
    "learning_rate": [0.01],
    "max_depth": [12],
    "reg_lambda": [1],
    "n_estimators": [30000],
    "subsample": [0.8],
    "colsample_bytree": [0.8],
}
# Create all models (total # is unique combination of all parameters)
models = [create_regressors(x) for x in named_product(**params)]
# Train all models
trained_models = [train_model_and_save(x) for x in tqdm(models)]

print("All models trained!")

# %%
# kfold = StratifiedKFold(n_splits=10, random_state=7)
# results = cross_val_score(trained_models, X, Y, cv=kfold)
# print("Accuracy: %.2f%% (%.2f%%)" % (results.mean() * 100, results.std() * 100))
