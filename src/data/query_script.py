#!/home/victoria/miniconda3/envs/mimic3/bin python
# %% import libraries
from pathlib import Path
from src.data.connect_and_run_pgsql import run_query
from src.data.query_inputs_to_mimic import (
    build_query_labs,
    build_query_kidney_events,
    build_query_adm,
    build_query_height,
    build_query_weight,
)

print("Starting Script...")


def run_query_and_save(sql: str, filename: str = None):
    "Execute SQL query, optionally save result in specified file, and return result."
    print("Starting query...")
    df = run_query(sql)
    if filename:
        data_dir = Path("/home/victoria/aki-forecaster/data/raw_hadmid")
        filename = data_dir / filename
        df.to_csv(Path(filename))
        print(f"Saved file: {filename}")
    return df


# %% Query Data
lab_events_query, lab_items_query = build_query_labs()

run_query_and_save(sql=lab_events_query, filename="lab_events.csv")
run_query_and_save(sql=lab_items_query, filename="lab_items_id.csv")
run_query_and_save(sql=build_query_kidney_events(), filename="kidney_events.csv")
run_query_and_save(sql=build_query_adm(), filename="admissions.csv")
run_query_and_save(sql=build_query_height(), filename="heights.csv")
run_query_and_save(sql=build_query_weight(), filename="weights.csv")

print("All queries are finished!")

