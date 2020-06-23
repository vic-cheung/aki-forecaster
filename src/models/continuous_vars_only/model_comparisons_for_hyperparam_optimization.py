#!/home/victoria/miniconda3/envs/mimic3/bin python
# %% import libraries
import pandas as pd
import numpy as np
from pathlib import Path
import re
import pickle
import altair as alt
import xgboost as xgb
from sklearn.metrics import r2_score

# from tqdm.autonotebook import tqdm

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
alt.data_transformers.disable_max_rows()


# %%
def select_params(fnames: list, param: str) -> list:
    files = [file for file in fnames if re.search(param, file)]
    return files


# %%
def to_path(model_dir: Path, fnames: list) -> Path:
    add_path = [model_dir / name for name in fnames]
    return add_path


# %%
def unpickle(filepath: list, idx: int):
    file = pickle.load(open(filepath[idx], "rb"))
    print(f"file loaded: {filepath[idx].name}")
    return file


# %%
def get_metrics(fnames: list) -> pd.DataFrame:
    # param_eval = dict.fromkeys(["lr", "md", "lam", "n", "ss", "csbt"])
    metrics = pd.DataFrame(columns=["error"])
    for p in fnames:
        model = pickle.load(open(p, "rb"))

        train_val_rmse = pd.DataFrame(
            model.evals_result_["validation_0"]["rmse"], columns=["train_rmse"]
        )
        train_val_rmsle = pd.DataFrame(
            model.evals_result_["validation_0"]["rmsle"], columns=["train_rmsle"]
        )
        train_val_mae = pd.DataFrame(
            model.evals_result_["validation_0"]["mae"], columns=["train_mae"]
        )

        val_val_rmse = pd.DataFrame(
            model.evals_result_["validation_1"]["rmse"], columns=["val_rmse"]
        )
        val_val_rmsle = pd.DataFrame(
            model.evals_result_["validation_1"]["rmsle"], columns=["val_rmsle"]
        )
        val_val_mae = pd.DataFrame(
            model.evals_result_["validation_1"]["mae"], columns=["val_mae"]
        )

        eval_metrics = pd.concat(
            [
                train_val_rmse,
                train_val_rmsle,
                train_val_mae,
                val_val_rmse,
                val_val_rmsle,
                val_val_mae,
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
        "val_rmse",
        "val_rmsle",
        "val_mae",
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


def altair_plot(error_metric: pd.DataFrame):
    num = error_metric.shape[0]
    idx = np.linspace(0, num - 1, 5000).astype(int)
    subset = error_metric.iloc[idx]
    plots = plot_metrics(subset, x_title="number of estimators")
    return plots


# %%
# find min error values in each val
def aggr_min_error(metrics: pd.DataFrame) -> pd.DataFrame:
    aggr = []
    for i in range(len(metrics)):
        data = metrics.error[i]
        data = data.min(axis=0)
        aggr += [data]
    aggr = pd.DataFrame(aggr)
    mask = (
        (aggr == aggr.min(axis=0))
        .loc[:, ["val_rmse", "val_rmsle", "val_mae"]]
        .sum(axis=1)
    )
    mask = (mask == mask.max()).astype(bool)
    selected_min = aggr.loc[mask, :]
    print(f"min_idx: {selected_min.index.values[0]}")
    return selected_min


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


# %%


# %% load data
model_dir = Path("/home/victoria/aki-forecaster/models/prelim/hadm_id_hyperparam_opt5")
pickles = [file for file in model_dir.iterdir()]
filenames = list(map(lambda x: x.name, pickles))
metrics = get_metrics(pickles)

# %% these were for hyperparam_opt1
# p1 = altair_plot(metrics.error[0])  # 15,000 val gets worse
# p2 = altair_plot(metrics.error[1])  # 2000 val gets worse
# p3 = altair_plot(metrics.error[2])  # 500 *
# p4 = altair_plot(metrics.error[3])  # 100 *
# p5 = altair_plot(metrics.error[4])  # 600
# p6 = altair_plot(metrics.error[5])  # 500
# p7 = altair_plot(metrics.error[6])  # models are about the same. 1000
# p8 = altair_plot(metrics.error[7])  # 150
# p9 = altair_plot(metrics.error[8])  # 500 *
# p10 = altair_plot(metrics.error[9])  # 500 *
# p11 = altair_plot(metrics.error[10])  # 500
# p12 = altair_plot(metrics.error[11])  # 500 *
# p13 = altair_plot(metrics.error[12])  # 500 *
# p14 = altair_plot(metrics.error[13])  # 1000
# p15 = altair_plot(metrics.error[14])  # 1000 *
# p16 = altair_plot(metrics.error[15])  # 1000 *
# p17 = altair_plot(metrics.error[16])  # 600 *
# p18 = altair_plot(metrics.error[17])  # 1500 *
# p19 = altair_plot(metrics.error[18])  # 1000
# p20 = altair_plot(metrics.error[19])  # 500 *
# p21 = altair_plot(metrics.error[20])  # 2000
# p22 = altair_plot(metrics.error[21])  # 500 *
# p23 = altair_plot(metrics.error[22])  # 300 *
# p24 = altair_plot(metrics.error[23])  # 1500
# p25 = altair_plot(metrics.error[24])  # 1500
# p26 = altair_plot(metrics.error[25])  # 500 *
# p27 = altair_plot(metrics.error[26])  # 2500


# comparison = pd.concat(
#     [
#         metrics.error[0].iloc[15000],
#         metrics.error[1].iloc[2000],
#         metrics.error[2].iloc[500],
#         metrics.error[3].iloc[100],
#         metrics.error[4].iloc[600],
#         metrics.error[5].iloc[500],
#         metrics.error[6].iloc[1000],
#         metrics.error[7].iloc[150],
#         metrics.error[8].iloc[500],
#         metrics.error[9].iloc[500],
#         metrics.error[10].iloc[500],
#         metrics.error[11].iloc[500],
#         metrics.error[12].iloc[500],
#         metrics.error[13].iloc[1000],
#         metrics.error[14].iloc[1000],
#         metrics.error[15].iloc[1000],
#         metrics.error[16].iloc[600],
#         metrics.error[17].iloc[1500],
#         metrics.error[18].iloc[1000],
#         metrics.error[19].iloc[500],
#         metrics.error[20].iloc[2000],
#         metrics.error[21].iloc[500],
#         metrics.error[22].iloc[300],
#         metrics.error[23].iloc[1500],
#         metrics.error[24].iloc[1500],
#         metrics.error[25].iloc[500],
#         metrics.error[26].iloc[2500],
#     ],
#     axis=1,
#     ignore_index=True,
# )

# model2 = unpickle(pickles, idx=1)
# model19 = unpickle(pickles, idx=18)

p1 = altair_plot(metrics.error[0])
p2 = altair_plot(metrics.error[1])
p3 = altair_plot(metrics.error[2])
p4 = altair_plot(metrics.error[3])
p5 = altair_plot(metrics.error[4])
p6 = altair_plot(metrics.error[5])
p7 = altair_plot(metrics.error[6])
p8 = altair_plot(metrics.error[7])

comparison = pd.concat(
    [
        metrics.error[0].iloc[-1],
        metrics.error[1].iloc[-1],
        metrics.error[2].iloc[-1],
        metrics.error[3].iloc[-1],
        metrics.error[4].iloc[-1],
        # metrics.error[5].iloc[-1],
        # metrics.error[6].iloc[-1],
        # metrics.error[7].iloc[-1],
    ],
    axis=1,
    ignore_index=True,
)

comparison = pd.concat(
    [metrics.error[2].iloc[800], metrics.error[4].iloc[3000]],
    axis=1,
    ignore_index=True,
)


data_dir = Path(
    "/home/victoria/aki-forecaster/data/processed/continuous_vars_only/hadm_id_window1_02"
)
X_test = pd.read_csv(data_dir / "X_test.csv", header=0, index_col=0,)
Y_test = pd.read_csv(data_dir / "Y_test.csv", header=0, index_col=0,).reset_index(
    drop=True
)
model1 = unpickle(pickles, idx=0)
model2 = unpickle(pickles, idx=1)
model3 = unpickle(pickles, idx=2)
model4 = unpickle(pickles, idx=3)
model5 = unpickle(pickles, idx=4)
model6 = unpickle(pickles, idx=5)
model7 = unpickle(pickles, idx=6)
model8 = unpickle(pickles, idx=7)

y1 = model1.predict(X_test.values)
y1 = pd.DataFrame(y1).rename(columns={0: "model1"})
y2 = model2.predict(X_test.values)
y2 = pd.DataFrame(y2).rename(columns={0: "model2"})
y3 = model3.predict(X_test.values)
y3 = pd.DataFrame(y3).rename(columns={0: "model3"})
y4 = model4.predict(X_test.values)
y4 = pd.DataFrame(y4).rename(columns={0: "model4"})
y5 = model5.predict(X_test.values)
y5 = pd.DataFrame(y5).rename(columns={0: "model5"})
y6 = model6.predict(X_test.values)
y6 = pd.DataFrame(y6).rename(columns={0: "model6"})
y7 = model7.predict(X_test.values)
y7 = pd.DataFrame(y7).rename(columns={0: "model7"})
y8 = model8.predict(X_test.values)
y8 = pd.DataFrame(y8).rename(columns={0: "model8"})

save_dir = Path(
    "/home/victoria/aki-forecaster/data/processed/continuous_vars_only/final_model"
)
y1.to_csv(Path(save_dir / "y1_pred.csv"))
y2.to_csv(Path(save_dir / "y2_pred.csv"))
y3.to_csv(Path(save_dir / "y_pred.csv"))
y4.to_csv(Path(save_dir / "y4_pred.csv"))
y5.to_csv(Path(save_dir / "y5_pred.csv"))
y6.to_csv(Path(save_dir / "y6_pred.csv"))
y7.to_csv(Path(save_dir / "y7_pred.csv"))
y8.to_csv(Path(save_dir / "y8_pred.csv"))

chart_concat = pd.concat([Y_test, y1, y2, y3, y4, y5, y6, y7, y8], axis=1)
# chart_concat = pd.concat([Y_test, y1, y2, y3, y4, y5,y6,y7], axis=1)

plot_metrics(
    chart_concat,
    features=[
        # "model1",
        # "model2",
        "model3",
        # "model4",
        # "model5",
        # "model6",
        # "model7",
        # "model8",
    ],
    x_title="True Creatinine Value from Test Set",
    x_inputs="Creatinine_avg",
    y_title="Predicited Creatinine Value",
    style="scatter",
)

chart_concat_2 = pd.concat([Y_test, y3], axis=1)
plot_metrics(
    chart_concat_2,
    features=["model3"],
    x_title="True Creatinine Value from Test Set",
    x_inputs="Creatinine_avg",
    y_title="Predicited Creatinine Value",
    style="scatter",
)

# %%
model1_r2 = r2_score(Y_test, y1)
model2_r2 = r2_score(Y_test, y2)
model3_r2 = r2_score(Y_test, y3)
model4_r2 = r2_score(Y_test, y4)
model5_r2 = r2_score(Y_test, y5)
model6_r2 = r2_score(Y_test, y6)
model7_r2 = r2_score(Y_test, y7)
model8_r2 = r2_score(Y_test, y8)
hyperparams1 = get_model_params(model1)
hyperparams2 = get_model_params(model2)
hyperparams3 = get_model_params(model3)
hyperparams4 = get_model_params(model4)
hyperparams5 = get_model_params(model5)
hyperparams6 = get_model_params(model6)
hyperparams7 = get_model_params(model7)
hyperparams8 = get_model_params(model8)

print(
    f"""
model1 r2 score: {model1_r2}
model2 r2 score: {model2_r2}
model3 r2 score: {model3_r2}
model4 r2 score: {model4_r2}
model5 r2 score: {model5_r2}
model6 r2 score: {model6_r2}
model5 r2 score: {model7_r2}
model6 r2 score: {model8_r2}


hyperparams1: {hyperparams1}
hyperparams2: {hyperparams2}
hyperparams3: {hyperparams3}
hyperparams4: {hyperparams4}
hyperparams5: {hyperparams5}
hyperparams6: {hyperparams6}
hyperparams5: {hyperparams7}
hyperparams6: {hyperparams8}
"""
)
# %%
# metrics.error[27].iloc[15000]
# metrics.error[28].iloc[15000]
# %%
# %% n estimators
# n30000 = to_path(model_dir, select_params(filenames, "n30000_"))
# min_error_values30000 = aggr_min_error(get_metrics(n30000))
# model30000 = unpickle(n30000, min_error_values30000.index.values[0])
# params30000 = get_model_params(model30000)

# n50000 = to_path(model_dir, select_params(filenames, "n50000_"))
# min_error_values50000 = aggr_min_error(get_metrics(n50000))
# model50000 = unpickle(n50000, min_error_values50000.index.values[0])
# params50000 = get_model_params(model50000)

# n100000 = to_path(model_dir, select_params(filenames, "n100000_"))
# min_error_values100000 = aggr_min_error(get_metrics(n100000))
# model100000 = unpickle(n100000, min_error_values100000.index.values[0])
# params100000 = get_model_params(model100000)

# error_cat_n = pd.concat(
#     [min_error_values30000, min_error_values50000, min_error_values100000],
#     ignore_index=True,
# )

# plot_metrics(error_cat_n, style="scatter")

# # %% learning rate
# lr1 = to_path(select_params(filenames, "_lr0.1_"))
# min_error_valueslr1 = aggr_min_error(get_metrics(lr1))
# modellr1 = unpickle(lr1, min_error_valueslr1.index.values[0])
# paramslr1 = get_model_params(modellr1)

# lr3 = to_path(select_params(filenames, "_lr0.3_"))
# min_error_valueslr3 = aggr_min_error(get_metrics(lr3))
# modellr3 = unpickle(lr3, min_error_valueslr3.index.values[0])
# paramslr3 = get_model_params(modellr3)

# lr10 = to_path(select_params(filenames, "_lr1.0_"))
# min_error_valueslr10 = aggr_min_error(get_metrics(lr10))
# modellr10 = unpickle(lr10, min_error_valueslr10.index.values[0])
# paramslr10 = get_model_params(modellr10)

# error_cat_lr = pd.concat(
#     [min_error_valueslr1, min_error_valueslr3, min_error_valueslr10], ignore_index=True,
# )
# plot_metrics(error_cat_lr, style="scatter")

# # %% max depth
# md5 = to_path(select_params(filenames, "_md5_"))
# min_error_valuesmd5 = aggr_min_error(get_metrics(md5))
# modelmd5 = unpickle(md5, min_error_valuesmd5.index.values[0])
# paramsmd5 = get_model_params(modelmd5)

# md10 = to_path(select_params(filenames, "_md10_"))
# min_error_valuesmd10 = aggr_min_error(get_metrics(md10))
# modelmd10 = unpickle(md10, min_error_valuesmd10.index.values[0])
# paramsmd10 = get_model_params(modelmd10)
# error_cat_md = pd.concat(
#     [min_error_valuesmd5, min_error_valuesmd10], ignore_index=True,
# )
# plot_metrics(error_cat_md, style="scatter")


# # %% lambda
# lam1 = to_path(select_params(filenames, "_lam0.1."))
# min_error_valueslam1 = aggr_min_error(get_metrics(lam1))
# modellam1 = unpickle(lam1, min_error_valueslam1.index.values[0])
# paramslam1 = get_model_params(modellam1)

# lam3 = to_path(select_params(filenames, "_lam0.3."))
# min_error_valueslam3 = aggr_min_error(get_metrics(lam3))
# modellam3 = unpickle(lam3, min_error_valueslam3.index.values[0])
# paramslam3 = get_model_params(modellam3)

# lam10 = to_path(select_params(filenames, "_lam1.0."))
# min_error_valueslam10 = aggr_min_error(get_metrics(lam10))
# modellam10 = unpickle(lam10, min_error_valueslam10.index.values[0])
# paramslam10 = get_model_params(modellam10)

# error_cat_lam = pd.concat(
#     [min_error_valueslam1, min_error_valueslam3, min_error_valueslam10],
#     ignore_index=True,
# )
# plot_metrics(error_cat_lam, style="scatter")

# # %%
# ss3 = to_path(select_params(filenames, "_ss0.3_"))
# min_error_valuesss3 = aggr_min_error(get_metrics(ss3))
# modelss3 = unpickle(ss3, min_error_valuesss3.index.values[0])
# paramsss3 = get_model_params(modelss3)

# ss5 = to_path(select_params(filenames, "_ss0.5_"))
# min_error_valuesss5 = aggr_min_error(get_metrics(ss5))
# modelss5 = unpickle(ss5, min_error_valuesss5.index.values[0])
# paramsss5 = get_model_params(modelss5)

# ss10 = to_path(select_params(filenames, "_ss1.0_"))
# min_error_valuesss10 = aggr_min_error(get_metrics(ss10))
# modelss10 = unpickle(ss10, min_error_valuesss10.index.values[0])
# paramsss10 = get_model_params(modelss10)

# error_cat_ss = pd.concat(
#     [min_error_valuesss3, min_error_valuesss5, min_error_valuesss10], ignore_index=True,
# )
# plot_metrics(error_cat_ss, style="scatter")

# # %%
# csbt3 = to_path(select_params(filenames, "_csbt0.3_"))
# min_error_valuescsbt3 = aggr_min_error(get_metrics(csbt3))
# modelcsbt3 = unpickle(csbt3, min_error_valuescsbt3.index.values[0])
# paramscsbt3 = get_model_params(modelcsbt3)

# csbt5 = to_path(select_params(filenames, "_csbt0.5_"))
# min_error_valuescsbt5 = aggr_min_error(get_metrics(csbt5))
# modelcsbt5 = unpickle(csbt5, min_error_valuescsbt5.index.values[0])
# paramscsbt5 = get_model_params(modelcsbt5)

# csbt10 = to_path(select_params(filenames, "_csbt1.0_"))
# min_error_valuescsbt10 = aggr_min_error(get_metrics(csbt10))
# modelcsbt10 = unpickle(csbt10, min_error_valuescsbt10.index.values[0])
# paramscsbt10 = get_model_params(modelcsbt10)

# error_cat_csbt = pd.concat(
#     [min_error_valuescsbt3, min_error_valuescsbt5, min_error_valuescsbt10],
#     ignore_index=True,
# )
# plot_metrics(error_cat_csbt, style="scatter")

# [params30000, paramslam1, paramsss5, paramscsbt10]
# pd.concat(
#     [
#         min_error_values30000,
#         min_error_valueslam1,
#         min_error_valuesss5,
#         min_error_valuescsbt10,
#     ]
# )
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
