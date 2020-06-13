#!/home/victoria/miniconda3/envs/mimic3/bin python
# %% import libraries
from pathlib import Path
from utils import run_query
from query_inputs_to_mimic import build_query_lab_events

print("Starting Script...")

# %% Query data
query_labs = build_query_lab_events()
# %%
parent_dir = "/home/victoria/predicting-insulin-regimen/"
item = "labevents_of_patients"
filename = parent_dir + item + ".csv"

# %% Actually Run Query & Get Data
print("Starting query...")
df = run_query(query_labs)
df.to_csv(Path(filename))
print(f"Saved file: {filename}")
print("Data Preview: ")
print(df.shape)
print(df.head(10))


# %%
