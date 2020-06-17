#!/home/victoria/miniconda3/envs/mimic3/bin python
# %% import libraries
import pandas as pd
from pathlib import Path
import re
import pickle
import altair as alt
import xgboost as xgb

# from tqdm.autonotebook import tqdm

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


# %%
def select_params(fnames: list, param: str) -> list:
    items = [name for name in fnames if re.search(param, name)]
    return items


# %%
def to_path(fnames: list) -> Path:
    add_path = [cd / name for name in fnames]
    return add_path


# %%
def get_metrics(fnames: list) -> pd.DataFrame:
    # param_eval = dict.fromkeys(["lr", "md", "lam", "n", "ss", "csbt"])
    metrics = pd.DataFrame(columns=["error"])
    for p in fnames:
        model = pickle.load(open(p, "rb"))
        train_val_rmse = pd.DataFrame(
            model.evals_result_["validation_0"]["rmse"], columns=["train_rmse"]
        )
        test_val_rmse = pd.DataFrame(
            model.evals_result_["validation_1"]["rmse"], columns=["test_rmse"]
        )

        train_val_rmsle = pd.DataFrame(
            model.evals_result_["validation_0"]["rmsle"], columns=["train_rmsle"]
        )
        test_val_rmsle = pd.DataFrame(
            model.evals_result_["validation_1"]["rmsle"], columns=["test_rmsle"]
        )

        train_val_mae = pd.DataFrame(
            model.evals_result_["validation_0"]["mae"], columns=["train_mae"]
        )
        test_val_mae = pd.DataFrame(
            model.evals_result_["validation_1"]["mae"], columns=["test_mae"]
        )

        eval_metrics = pd.concat(
            [
                train_val_rmse,
                train_val_rmsle,
                train_val_mae,
                test_val_rmse,
                test_val_rmsle,
                test_val_mae,
            ],
            axis=1,
        )
        metrics = metrics.append(
            pd.DataFrame([eval_metrics], columns=["error"]), ignore_index=True
        )
    return metrics


# %%
def plot_metrics(
    data: pd.DataFrame,
    features: list = [
        "test_rmse",
        "test_rmsle",
        "test_mae",
        "train_rmse",
        "train_rmsle",
        "train_mae",
    ],
    x_title: str = "index",
    x_inputs: str = "index",
    y_title: str = "error_value",
    y_inputs: str = "max(value)",
    color_by: str = "variable",
    style: str = "line",
) -> alt.Chart:
    # Altair codes for data types
    # DATA TYPE        CODE	        DESCRIPTION
    # quantitative	    Q	        Number
    # nominal	        N	        Unordered Categorical
    # ordinal	        O	        Ordered Categorical
    # temporal	        T	        Date/Time
    data = data.reset_index()

    if style == "line":
        CHART = (
            alt.Chart(data)
            .mark_line()
            .transform_fold(fold=features, as_=["variable", "value"])
            .encode(
                alt.X(f"{x_inputs}:Q", axis=alt.Axis(title=f"{x_title}")),
                alt.Y(f"{y_inputs}:Q", axis=alt.Axis(title=f"{y_title}")),
                color=f"{color_by}:N",
            )
        )
    elif style == "scatter":
        CHART = (
            alt.Chart(data)
            .mark_point()
            .transform_fold(fold=features, as_=["variable", "value"])
            .encode(
                alt.X(f"{x_inputs}:Q", axis=alt.Axis(title=f"{x_title}")),
                alt.Y(f"{y_inputs}:Q", axis=alt.Axis(title=f"{y_title}")),
                color=f"{color_by}:N",
            )
        )
    return CHART


# %%
# find min error values in each test
def aggr_min_error(metrics: pd.DataFrame) -> pd.DataFrame:
    aggr = []
    for i in range(len(metrics)):
        data = metrics.error[i]
        data = data.min(axis=0)
        aggr += [data]
    aggr = pd.DataFrame(aggr)
    mask = (
        (aggr == aggr.min(axis=0))
        .loc[:, ["test_rmse", "test_rmsle", "test_mae"]]
        .sum(axis=1)
    )
    mask = (mask == mask.max()).astype(bool)
    selected_min = aggr.loc[mask, :]
    print(f"min_idx: {selected_min.index.values[0]}")
    return selected_min


# %%
def unpickle(PosixPath: list, idx: int):
    model = pickle.load(open(PosixPath[idx], "rb"))
    print(f"model loaded: {PosixPath[idx].name}")
    return model


# %%
def get_model_params(model: xgb.XGBRegressor) -> dict:
    params = model.get_xgb_params()
    params_dict = {
        "lr": params["learning_rate"],
        "md": params["max_depth"],
        "lam": params["reg_lambda"],
        "n": model.n_estimators,
        "ss": params["subsample"],
        "csbt": params["colsample_bytree"],
    }
    return params_dict


# def append_errors_on_params():


# %% load data
cd = Path(
    "/home/victoria/aki-forecaster/src/models/continuous_vars_only/xgb_different_params"
)
pickles = [file for file in cd.iterdir()]
filenames = list(map(lambda x: x.name, pickles))

# %% n estimators
n30000 = to_path(select_params(filenames, "n30000_"))
min_error_values30000 = aggr_min_error(get_metrics(n30000))
model30000 = unpickle(n30000, min_error_values30000.index.values[0])
params30000 = get_model_params(model30000)

n50000 = to_path(select_params(filenames, "n50000_"))
min_error_values50000 = aggr_min_error(get_metrics(n50000))
model50000 = unpickle(n50000, min_error_values50000.index.values[0])
params50000 = get_model_params(model50000)

n100000 = to_path(select_params(filenames, "n100000_"))
min_error_values100000 = aggr_min_error(get_metrics(n100000))
model100000 = unpickle(n100000, min_error_values100000.index.values[0])
params100000 = get_model_params(model100000)

error_cat_n = pd.concat(
    [min_error_values30000, min_error_values50000, min_error_values100000],
    ignore_index=True,
)

plot_metrics(error_cat_n, style="scatter")

# %% learning rate
lr1 = to_path(select_params(filenames, "_lr0.1_"))
min_error_valueslr1 = aggr_min_error(get_metrics(lr1))
modellr1 = unpickle(lr1, min_error_valueslr1.index.values[0])
paramslr1 = get_model_params(modellr1)

lr3 = to_path(select_params(filenames, "_lr0.3_"))
min_error_valueslr3 = aggr_min_error(get_metrics(lr3))
modellr3 = unpickle(lr3, min_error_valueslr3.index.values[0])
paramslr3 = get_model_params(modellr3)

lr10 = to_path(select_params(filenames, "_lr1.0_"))
min_error_valueslr10 = aggr_min_error(get_metrics(lr10))
modellr10 = unpickle(lr10, min_error_valueslr10.index.values[0])
paramslr10 = get_model_params(modellr10)

error_cat_lr = pd.concat(
    [min_error_valueslr1, min_error_valueslr3, min_error_valueslr10], ignore_index=True,
)
plot_metrics(error_cat_lr, style="scatter")

# %% max depth
md5 = to_path(select_params(filenames, "_md5_"))
min_error_valuesmd5 = aggr_min_error(get_metrics(md5))
modelmd5 = unpickle(md5, min_error_valuesmd5.index.values[0])
paramsmd5 = get_model_params(modelmd5)

md10 = to_path(select_params(filenames, "_md10_"))
min_error_valuesmd10 = aggr_min_error(get_metrics(md10))
modelmd10 = unpickle(md10, min_error_valuesmd10.index.values[0])
paramsmd10 = get_model_params(modelmd10)
error_cat_md = pd.concat(
    [min_error_valuesmd5, min_error_valuesmd10], ignore_index=True,
)
plot_metrics(error_cat_md, style="scatter")


# %% lambda
lam1 = to_path(select_params(filenames, "_lam0.1."))
min_error_valueslam1 = aggr_min_error(get_metrics(lam1))
modellam1 = unpickle(lam1, min_error_valueslam1.index.values[0])
paramslam1 = get_model_params(modellam1)

lam3 = to_path(select_params(filenames, "_lam0.3."))
min_error_valueslam3 = aggr_min_error(get_metrics(lam3))
modellam3 = unpickle(lam3, min_error_valueslam3.index.values[0])
paramslam3 = get_model_params(modellam3)

lam10 = to_path(select_params(filenames, "_lam1.0."))
min_error_valueslam10 = aggr_min_error(get_metrics(lam10))
modellam10 = unpickle(lam10, min_error_valueslam10.index.values[0])
paramslam10 = get_model_params(modellam10)

error_cat_lam = pd.concat(
    [min_error_valueslam1, min_error_valueslam3, min_error_valueslam10],
    ignore_index=True,
)
plot_metrics(error_cat_lam, style="scatter")

# %%
ss3 = to_path(select_params(filenames, "_ss0.3_"))
min_error_valuesss3 = aggr_min_error(get_metrics(ss3))
modelss3 = unpickle(ss3, min_error_valuesss3.index.values[0])
paramsss3 = get_model_params(modelss3)

ss5 = to_path(select_params(filenames, "_ss0.5_"))
min_error_valuesss5 = aggr_min_error(get_metrics(ss5))
modelss5 = unpickle(ss5, min_error_valuesss5.index.values[0])
paramsss5 = get_model_params(modelss5)

ss10 = to_path(select_params(filenames, "_ss1.0_"))
min_error_valuesss10 = aggr_min_error(get_metrics(ss10))
modelss10 = unpickle(ss10, min_error_valuesss10.index.values[0])
paramsss10 = get_model_params(modelss10)

error_cat_ss = pd.concat(
    [min_error_valuesss3, min_error_valuesss5, min_error_valuesss10], ignore_index=True,
)
plot_metrics(error_cat_ss, style="scatter")

# %%
csbt3 = to_path(select_params(filenames, "_csbt0.3_"))
min_error_valuescsbt3 = aggr_min_error(get_metrics(csbt3))
modelcsbt3 = unpickle(csbt3, min_error_valuescsbt3.index.values[0])
paramscsbt3 = get_model_params(modelcsbt3)

csbt5 = to_path(select_params(filenames, "_csbt0.5_"))
min_error_valuescsbt5 = aggr_min_error(get_metrics(csbt5))
modelcsbt5 = unpickle(csbt5, min_error_valuescsbt5.index.values[0])
paramscsbt5 = get_model_params(modelcsbt5)

csbt10 = to_path(select_params(filenames, "_csbt1.0_"))
min_error_valuescsbt10 = aggr_min_error(get_metrics(csbt10))
modelcsbt10 = unpickle(csbt10, min_error_valuescsbt10.index.values[0])
paramscsbt10 = get_model_params(modelcsbt10)

error_cat_csbt = pd.concat(
    [min_error_valuescsbt3, min_error_valuescsbt5, min_error_valuescsbt10],
    ignore_index=True,
)
plot_metrics(error_cat_csbt, style="scatter")

[params30000, paramslam1, paramsss5, paramscsbt10]
pd.concat(
    [
        min_error_values30000,
        min_error_valueslam1,
        min_error_valuesss5,
        min_error_valuescsbt10,
    ]
)
initial_param_inputs = {
    "learning_rate": [0.1, 0.3, 1.0],
    "max_depth": [5, 10],
    "reg_lambda": [0.1, 0.3, 1.0],
    "n_estimators": [1000, 5000, 10000, 30000],
    "subsample": [0.3, 0.5, 1.0],
    "colsample_bytree": [0.3, 0.5, 1.0],
}

# %%


# find which error metric is the lowest across the different types and trace back to model params.
# plot_metrics(data)


# %%
