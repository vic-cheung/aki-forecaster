#!/home/victoria/miniconda3/envs/mimic3/bin python
# %% import libraries
import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import explained_variance_score, mean_squared_error, r2_score
from src.models.continuous_vars_only.model_comparisons_for_hyperparam_optimization import (
    unpickle,
)
import matplotlib

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

# %% load data
data_dir = Path("/home/victoria/aki-forecaster/data/processed/continuous_vars_only/")
X_test = pd.read_csv(data_dir / "X_test.csv", header=0, index_col=0)
Y_test = pd.read_csv(data_dir / "Y_test.csv", header=0, index_col=0)

X_valid = pd.read_csv(data_dir / "X_valid.csv", header=0, index_col=0)
Y_valid = pd.read_csv(data_dir / "Y_valid.csv", header=0, index_col=0)

#%%
model_dir = Path(
    "/home/victoria/aki-forecaster/src/models/continuous_vars_only/xgb_different_params"
)
pickles = [file for file in model_dir.iterdir()]
filenames = list(map(lambda x: x.name, pickles))

model1 = unpickle(pickles, 0)
model2 = unpickle(pickles, 1)
model3 = unpickle(pickles, 2)

# %%
model1.evals_result()
model1.evals_result()["validation_0"]
model1.evals_result()["validation_1"]

# %%
y1 = model1.predict(X_valid.values)
y2 = model2.predict(X_valid.values)
y3 = model3.predict(X_valid.values)
# %%
compare1 = pd.concat(
    [Y_valid.reset_index(drop=True), pd.Series(y1, name="Predicted Avg. Creatinine")],
    axis=1,
    ignore_index=True,
).rename(columns={0: "Creatinine_avg", 1: "Pred_Creatinine_value"})
plot1 = compare1.plot(kind="scatter", x="Creatinine_avg", y="Pred_Creatinine_value")
plot1.set_xlim(0, 25)
plot1.set(xlim=(0, 25), ylim=(0, 25))

# %%
compare2 = pd.concat(
    [Y_valid.reset_index(drop=True), pd.Series(2, name="Predicted Avg. Creatinine")],
    axis=1,
    ignore_index=True,
).rename(columns={0: "Creatinine_avg", 1: "Pred_Creatinine_value"})
compare2.plot(kind="scatter", x="Creatinine_avg", y="Pred_Creatinine_value")

# %%
compare3 = pd.concat(
    [Y_valid.reset_index(drop=True), pd.Series(y3, name="Predicted Avg. Creatinine")],
    axis=1,
    ignore_index=True,
).rename(columns={0: "Creatinine_avg", 1: "Pred_Creatinine_value"})
compare3.plot(kind="scatter", x="Creatinine_avg", y="Pred_Creatinine_value")

# %%
