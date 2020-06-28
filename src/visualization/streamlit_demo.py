# %%
# import libraries
import pandas as pd
from pathlib import Path
import streamlit as st

# import re

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
# %% load data
base_path = Path(
    "/home/victoria/aki-forecaster/data/processed/continuous_vars_only/final_model"
)
ethnicity_dict = (
    pd.read_csv(base_path / "ethnicity_id.csv", header=0, index_col=0,)
    .iloc[:, 0]
    .to_dict()
)

labs_df = (
    pd.read_csv(base_path / "X_test.csv", header=0, index_col=0)
    .reset_index(drop=True)
    .iloc[100:201]
)
demo_df = labs_df.loc[:, ["gender", "ethnicity", "weight", "height", "age"]]

Y_test = (
    pd.read_csv(base_path / "Y_test.csv", header=0, index_col=0)
    .reset_index(drop=True)
    .iloc[100:201]
)

Y_pred_xgb = pd.DataFrame(
    pd.read_csv(base_path / "y_pred.csv", header=0, index_col=0).iloc[100:201]
).rename(columns={"model3": "Creatinine_pred_xgb"})
# %%
st.title("Predicting Acute Kidney Injury in Critical Care/Intensive Care Units")
st.write(
    """
    Creatinine is a biomarker for kidney function and can help clinicians diagnose acute kidney injury (AKI) which commonly occurs in hospital, or chronic kidney disease (CKD).
    
    Progressively worsening kidney function may cause doctors to consider dialysis or change medications and/or dosing for treatment.
    
    This calculator uses past creatinine data and combines it with other laboratory studies that measure function and health of other organ systems in the body to predict creatinine (and kidney function) for the following day.
    """
)
st.write(
    """
AKI is diagnosed if serum creatinine increases by 0.3 mg/dl (26.5 μmol/l) or more in 48 h or rises to at least 1.5-fold from baseline within 7 days
"""
)
st.subheader("Select a patient ID from the left sidebar for predictions")

st.title("Creatinine predictions")


pt_list = st.sidebar.selectbox("Select PatientID", labs_df.index.values)
labs = labs_df.loc[labs_df.index == pt_list]
labs = labs.iloc[:, :-5]
demographics = demo_df.loc[demo_df.index == pt_list]

#%%
Creatinine_avg = round(
    (labs_df.loc[labs_df.index == pt_list].loc[:, "Creatinine[B-C]"].values[0]), 2
)

st.write("Current Creatinine Value (mg/dL):", Creatinine_avg)

Predicted_Creatinine_xgb = round(Y_pred_xgb.loc[labs_df.index == pt_list], 2)
Actual_creatinine_value = Y_test.loc[labs_df.index == pt_list]
Actual_creatinine = Actual_creatinine_value.values[0][0]
pt_demographics = demo_df.loc[demo_df.index == pt_list]
ethnicity = pt_demographics.ethnicity.values[0]
age = pt_demographics.age.values[0]
gender = pt_demographics.gender.values[0]
gender_dict = {0: "MALE", 1: "FEMALE"}
gend = 1
ethn = 1
if gender == 1:
    gend = 0.742
if ethnicity in [6, 13, 15, 18]:
    ethn = 1.210

pt_demographics.ethnicity = pt_demographics.ethnicity.replace(ethnicity_dict)
pt_demographics.gender = pt_demographics.gender.replace(gender_dict)
pt_demographics = pt_demographics.rename(columns={"weight": "weight-kg"})
pt_demographics.height.values[0] = round(pt_demographics.height.values[0], 2)
pt_demographics.age.values[0] = int(pt_demographics.age.values[0])

# # GFR formula
# GFR = (
#     round(
#         (
#             186
#             * ((1 / (Creatinine_avg / 88.4) ** (1.154)))
#             * (1 / (age ** (0.203)))
#             * gend
#             * ethn
#         ),
#         2,
#     )
#     / 178.92
# )

# eGFR = (
#     round(
#         (
#             186
#             * ((1 / (Actual_creatinine / 88.4) ** (1.154)))
#             * (1 / (age ** (0.203)))
#             * gend
#             * ethn
#         ),
#         2,
#     )
#     / 178.92
# )

# Accordingly, AKI is diagnosed if serum creatinine increases by 0.3 mg/dl
# (26.5 μmol/l) or more in 48 h or rises to at least 1.5-fold from baseline
# within 7 days (Table 1). AKI stages are defined by the maximum change of
# either serum creatinine or urine output.Sep 27, 2016
# source: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5037640/#:~:text=Accordingly%2C%20AKI%20is%20diagnosed%20if,serum%20creatinine%20or%20urine%20output.
# st.write(
#     "<style>increased{color:orange} decreased{color:orange} monitor{color:orange} lowered{color:green} normal {color:green} risky{color:red}</style>",
#     unsafe_allow_html=True,
# )

# if (Actual_creatinine >= Creatinine_avg) & (Actual_creatinine >= 1.5):
#     color = "risky"
#     st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)
# elif (Actual_creatinine >= Creatinine_avg) & (Actual_creatinine <= 1.5):
#     color = "increased"
#     st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)
# elif (
#     ((abs(Actual_creatinine - Creatinine_avg)) < 0.3)
#     & (Actual_creatinine <= 1.5)
#     & (Creatinine_avg <= 1.5)
# ):
#     color = "normal"
#     st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)
# elif (Actual_creatinine - Creatinine_avg) >= 0.3:
#     color = "monitor"
#     st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)
# elif (Actual_creatinine <= Creatinine_avg) & (Actual_creatinine >= 1.5):
#     color = "decreased"
#     st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)
# elif (Actual_creatinine <= Creatinine_avg) & (Actual_creatinine <= 1.5):
#     color = "lowered"
#     st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)

st.write(
    "XGBoost Predicted Creatinine value (mg/dL) on next day:",
    round(Predicted_Creatinine_xgb.values[0][0], 2),
)
# st.write(
#     "Actual Creatinine value (mg/dL) on next day:", round(Actual_creatinine, 2),
# )

# st.write(
#     "GFR calculated with Creatinine_avg (ml/min/1.73m2):", round(GFR, 2),
# )

# st.write(
#     "GFR calculated with Predicted Creatinine Values (ml/min/1.73m2):", round(eGFR, 2),
# )

st.title("Patient health record")
st.write(
    "The following demographic and laboratory data is used as inputs into predictive models i.e. XGBoost and LinearRegression."
)
st.header("Patient Demographic Data")
st.table(pt_demographics.T)
st.header("Patient Lab Data")
st.write(
    """Lab data displayed is a 3-day average immediately preceeding the day for which predictions are made."""
)
st.subheader("Complete Blood Count Panel")
cbc_labels = [
    "Red Blood Cells[B-H]",
    "White Blood Cells[B-H]",
    "WBC Count[B-H]",
    "Platelet Count[B-H]",
    "Hemoglobin[B-H]",
    "Hematocrit[B-H]",
    "MCV[B-H]",
]
table = labs.loc[:, cbc_labels].T
table.index = [x.split("[")[0] for x in table.index]
table = round(table, 2)
st.table(table)

st.subheader("Other Blood Labs")
cbc_other_labels = [
    "Neutrophils[B-H]",
    "Hypersegmented Neutrophils[B-H]",
    "Large Platelets[B-H]",
    "Platelet Clumps[B-H]",
    "Glucose[B-G]",
    "Hemoglobin[B-G]",
]
table = labs.loc[:, cbc_other_labels].T
table.index = [x.split("[")[0] for x in table.index]
table = round(table, 2)
st.table(table)

st.subheader("Chemistry Panel")
chem_labels = [
    "Sodium[B-C]",
    "Potassium[B-C]",
    "Chloride[B-C]",
    "Bicarbonate[B-C]",
    "Creatinine[B-C]",
    "Glucose[B-C]",
    "Phosphate[B-C]",
]
table = labs.loc[:, chem_labels].T
table.index = [x.split("[")[0] for x in table.index]
table = round(table, 2)
st.table(table)

st.subheader("Liver Function Panel")
lft_labels = [
    "Asparate Aminotransferase (AST)[B-C]",
    "Alanine Aminotransferase (ALT)[B-C]",
    "Alkaline Phosphatase[B-C]",
    "Bilirubin, Total[B-C]",
    "Bilirubin, Direct[B-C]",
    "Bilirubin, Indirect[B-C]",
    # "Albumin[B-C]",
]
table = labs.loc[:, lft_labels].T
table.index = [x.split("[")[0] for x in table.index]
table = round(table, 2)
st.table(table)

st.subheader("Cardiac Biomarkers")
cardiac_labels = ["Troponin I[B-C]", "Troponin T[B-C]", "NTproBNP[B-C]"]
table = labs.loc[:, cardiac_labels].T
table.index = [x.split("[")[0] for x in table.index]
table = round(table, 2)
st.table(table)

st.subheader("Diabetes Biomarkers")
diabetes_labels = ["% Hemoglobin A1c[B-C]", "Estimated Actual Glucose[B-C]"]
table = labs.loc[:, diabetes_labels].T
table.index = [x.split("[")[0] for x in table.index]
table = round(table, 2)
st.table(table)

st.subheader("Inflammatory Biomarkers")
inflammatory_labels = ["C-Reactive Protein[B-C]", "Sedimentation Rate[B-H]"]
table = labs.loc[:, inflammatory_labels].T
table.index = [x.split("[")[0] for x in table.index]
table = round(table, 2)
st.table(table)

st.subheader("Urinalysis Panel")
urinalysis_labels = [
    "pH[U-H]",
    "Specific Gravity[U-H]",
    # "Urine Color[U-H]",
    "RBC[U-H]",
    "WBC[U-H]",
    "Bacteria[U-H]",
    # "Yeast[U-H]",
    "Ketone[U-H]",
    "Protein[U-H]",
    "Broad Casts[U-H]",
    "Cellular Cast[U-H]",
    "Urine Casts, Other[U-H]",
]
table = labs.loc[:, urinalysis_labels].T
table.index = [x.split("[")[0] for x in table.index]
table = round(table, 2)
st.table(table)

st.subheader("Urine Chemistries Panel")
urine_chem_labels = [
    "pH[U-C]",
    "Sodium[U-C]",
    "Osmolality[U-C]",
    "Urine Creatinine[U-C]",
    "Protein/Creatinine Ratio[U-C]",
    "Albumin[U-C]",
    "Albumin/Creatinine[U-C]",
    "Urine Volume[U-C]",
    "Urine Volume, Total[U-C]",
]
table = labs.loc[:, urine_chem_labels].T
table.index = [x.split("[")[0] for x in table.index]
table = round(table, 2)
st.table(table)


# %%


# %%
