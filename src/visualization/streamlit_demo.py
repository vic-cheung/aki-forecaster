# %%
# import libraries
import pandas as pd
from pathlib import Path
import streamlit as st
import re

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
# %% load data
base_path = Path("/home/victoria/predicting-insulin-regimen")
demo_df = pd.read_csv(
    base_path / "streamlit_loadfiles" / "valid_x_demographics.csv",
    header=0,
    index_col=0,
    nrows=20,
)

labs_df = pd.read_csv(
    base_path / "streamlit_loadfiles" / "valid_x_no_demographics.csv",
    header=0,
    index_col=0,
    nrows=20,
)
X_test = pd.read_csv(
    base_path / "processed_data_linreg" / "X_test.csv", header=0, index_col=0, nrows=20
)

Y_pred_linrg = pd.read_csv(
    (base_path / "processed_data_linreg" / "Y_pred_linrg.csv"),
    header=0,
    index_col=0,
    nrows=20,
)

Y_pred_xgb = pd.DataFrame(
    pd.read_csv(
        base_path / "xgb_models2" / "xgb_pred.csv", header=0, index_col=0, nrows=20
    )
).rename(columns={"0": "Creatinine_pred_xgb"})

Y_valid = pd.read_csv(
    base_path / "processed_data_linreg" / "Y_valid.csv",
    header=0,
    index_col=0,
    nrows=20,
)
# %%
st.title("Predicting Acute Kidney Injury in Critical Care/Intensive Care Units")
st.write(
    """
    Creatinine is a biomarker for kidney function and can help clinicians diagnose acute kidney injury (AKI) which commonly occurs in hospital, or chronic kidney disease (CKD).
    
    Progressively worsening kidney function may cause doctors to consider dialysis or change medications and/or dosing for treatment.
    
    This calculator uses past creatinine data and combines it with other laboratory studies that measure function and health of other organ systems in the body to predict creatinine (and kidney function) for the following day.
    """
)
st.subheader("Select a patient ID from the left sidebar for predictions")

st.title("Creatinine predictions")


pt_list = st.sidebar.selectbox("Select PatientID", labs_df.index.values)
labs = labs_df.loc[labs_df.index == pt_list]
demographics = demo_df.loc[demo_df.index == pt_list]

#%%
Creatinine_avg = round(
    (X_test.loc[labs_df.index == pt_list].loc[:, "Creatinine[B-C]_avg"].values[0]), 2
)

st.write("Creatinine 3-day average (mg/dL):", Creatinine_avg)

Predicted_Creatinine_xgb = round(Y_pred_xgb.loc[labs_df.index == pt_list], 2)
Predicted_Creatinine_linrg = round(Y_pred_linrg.loc[labs_df.index == pt_list], 2)
Actual_creatinine_value = Y_valid.loc[labs_df.index == pt_list]
Actual_creatinine = Actual_creatinine_value.values[0][0]
pt_demographics = demo_df.loc[demo_df.index == pt_list]
ethnicity = pt_demographics.ethnicity.values[0].lower()
substring = "black"
age = pt_demographics.age.values[0]
gender = pt_demographics.gender.values[0].lower()

gend = 1
ethn = 1
if gender != "male":
    gend = 0.742
try:
    isblack = ethnicity.index(substring)
    if isblack == 0:
        ethn = 1.210
except ValueError:
    print("Not found!")
else:
    print("Found!")

# GFR formula
# GFR = round(186 * (Creatinine_avg / 88.4) - (1.154 * (age)) - (0.203 * gend * ethn), 2)

# Accordingly, AKI is diagnosed if serum creatinine increases by 0.3 mg/dl
# (26.5 μmol/l) or more in 48 h or rises to at least 1.5-fold from baseline
# within 7 days (Table 1). AKI stages are defined by the maximum change of
# either serum creatinine or urine output.Sep 27, 2016
# source: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5037640/#:~:text=Accordingly%2C%20AKI%20is%20diagnosed%20if,serum%20creatinine%20or%20urine%20output.
st.write(
    "<style>increased{color:orange} decreased{color:orange} monitor{color:orange} lowered{color:green} normal {color:green} risky{color:red}</style>",
    unsafe_allow_html=True,
)

if (Actual_creatinine >= Creatinine_avg) & (Actual_creatinine >= 1.5):
    color = "risky"
    st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)
elif (Actual_creatinine >= Creatinine_avg) & (Actual_creatinine <= 1.5):
    color = "increased"
    st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)
elif (
    ((abs(Actual_creatinine - Creatinine_avg)) < 0.3)
    & (Actual_creatinine <= 1.5)
    & (Creatinine_avg <= 1.5)
):
    color = "normal"
    st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)
elif (Actual_creatinine - Creatinine_avg) >= 0.3:
    color = "monitor"
    st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)
elif (Actual_creatinine <= Creatinine_avg) & (Actual_creatinine >= 1.5):
    color = "decreased"
    st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)
elif (Actual_creatinine <= Creatinine_avg) & (Actual_creatinine <= 1.5):
    color = "lowered"
    st.write(f"<{color}>{color}</{color}>", unsafe_allow_html=True)

st.write(
    "linrg Predicted Creatinine value (mg/dL) on next day:",
    Predicted_Creatinine_linrg.values[0][0],
)
st.write(
    "xgb Predicted Creatinine value (mg/dL) on next day:",
    Predicted_Creatinine_xgb.values[0][0],
)
st.write(
    "Actual Creatinine value (mg/dL) on next day:", Actual_creatinine,
)

# st.write(
#     "GFR calculated with Creatinine_avg:", GFR,
# )

st.title("Patient health record")
st.write(
    "The following demographic and laboratory data is used as inputs into predictive models i.e. XGBoost and LinearRegression."
)
st.header("Patient Demographic Data")
st.table(demographics.T)
st.header("Patient Lab Data")
st.write(
    """Lab data displayed is a 3-day average immediately preceeding the day for which predictions are made."""
)
st.subheader("Complete Blood Count Panel")
cbc_labels = [
    "Red Blood Cells[B-H]_avg",
    "White Blood Cells[B-H]_avg",
    "WBC Count[B-H]_avg",
    "Platelet Count[B-H]_avg",
    "Hemoglobin[B-H]_avg",
    "Hematocrit[B-H]_avg",
    "MCV[B-H]_avg",
]
table = labs.loc[:, cbc_labels].T
table.index = [x.split("[")[0] for x in table.index]
st.table(table)

st.subheader("Other Blood Labs")
cbc_other_labels = [
    "Neutrophils[B-H]_avg",
    "Hypersegmented Neutrophils[B-H]_avg",
    "Large Platelets[B-H]_avg",
    "Platelet Clumps[B-H]_avg",
    "Glucose[B-G]_avg",
    "Hemoglobin[B-G]_avg",
]
table = labs.loc[:, cbc_other_labels].T
table.index = [x.split("[")[0] for x in table.index]
st.table(table)

st.subheader("Chemistry Panel")
chem_labels = [
    "Sodium[B-C]_avg",
    "Potassium[B-C]_avg",
    "Chloride[B-C]_avg",
    "Bicarbonate[B-C]_avg",
    "Creatinine[B-C]_avg",
    "Glucose[B-C]_avg",
    "Phosphate[B-C]_avg",
]
table = labs.loc[:, chem_labels].T
table.index = [x.split("[")[0] for x in table.index]
st.table(table)

st.subheader("Liver Function Panel")
lft_labels = [
    "Asparate Aminotransferase (AST)[B-C]_avg",
    "Alanine Aminotransferase (ALT)[B-C]_avg",
    "Alkaline Phosphatase[B-C]_avg",
    "Bilirubin, Total[B-C]_avg",
    "Bilirubin, Direct[B-C]_avg",
    "Bilirubin, Indirect[B-C]_avg",
    "Albumin[B-C]_avg",
]
table = labs.loc[:, lft_labels].T
table.index = [x.split("[")[0] for x in table.index]
st.table(table)

st.subheader("Cardiac Biomarkers")
cardiac_labels = ["Troponin I[B-C]_avg", "Troponin T[B-C]_avg", "NTproBNP[B-C]_avg"]
table = labs.loc[:, cardiac_labels].T
table.index = [x.split("[")[0] for x in table.index]
st.table(table)

st.subheader("Diabetes Biomarkers")
diabetes_labels = ["% Hemoglobin A1c[B-C]_avg", "Estimated Actual Glucose[B-C]_avg"]
table = labs.loc[:, diabetes_labels].T
table.index = [x.split("[")[0] for x in table.index]
st.table(table)

st.subheader("Inflammatory Biomarkers")
inflammatory_labels = ["C-Reactive Protein[B-C]_avg", "Sedimentation Rate[B-H]_avg"]
table = labs.loc[:, inflammatory_labels].T
table.index = [x.split("[")[0] for x in table.index]
st.table(table)

st.subheader("Urinalysis Panel")
urinalysis_labels = [
    "pH[U-H]_avg",
    "Specific Gravity[U-H]_avg",
    "Urine Color[U-H]_avg",
    "RBC[U-H]_avg",
    "WBC[U-H]_avg",
    "Bacteria[U-H]_avg",
    "Yeast[U-H]_avg",
    "Ketone[U-H]_avg",
    "Protein[U-H]_avg",
    "Broad Casts[U-H]_avg",
    "Cellular Cast[U-H]_avg",
    "Urine Casts, Other[U-H]_avg",
]
table = labs.loc[:, urinalysis_labels].T
table.index = [x.split("[")[0] for x in table.index]
st.table(table)

st.subheader("Urine Chemistries Panel")
urine_chem_labels = [
    "pH[U-C]_avg",
    "Sodium[U-C]_avg",
    "Osmolality[U-C]_avg",
    "Urine Creatinine[U-C]_avg",
    "Protein/Creatinine Ratio[U-C]_avg",
    "Albumin[U-C]_avg",
    "Albumin/Creatinine[U-C]_avg",
    "Urine Volume[U-C]_avg",
    "Urine Volume, Total[U-C]_avg",
]
table = labs.loc[:, urine_chem_labels].T
table.index = [x.split("[")[0] for x in table.index]
st.table(table)

# st.table(labs.T)


# %%
