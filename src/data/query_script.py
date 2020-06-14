#!/home/victoria/miniconda3/envs/mimic3/bin python
# %% import libraries
from pathlib import Path
from connect_and_run_pgsql import run_query
from src.data.query_inputs_to_mimic import (
    build_query_lab_events,
    build_query_kidney_events,
    build_query_adm,
    build_query_htwt,
)

print("Starting Script...")

# %% Query data
query_labs = build_query_lab_events()
# %%

data_dir = Path("/home/victoria/aki-forecaster/data/raw")
filename = data_dir / "labevents_of_patients.csv"

# %% Actually Run Query & Get Data
print("Starting query...")
df = run_query(query_labs)
df.to_csv(Path(filename))
print(f"Saved file: {filename}")
print("Data Preview: ")
print(df.shape)
print(df.head(10))


# %%
