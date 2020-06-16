def simplify_label(label: str) -> str:
    "Simplifies `label` with comma in it by dropping after comma."
    split_label = label.split(", ")
    if len(split_label) == 1:
        return label
    elif split_label[1] in ("Whole Blood", "Blood", "Urine", "Calculated"):
        return split_label[0]
    else:
        return label


def uniquify_label(row: pd.Series):
    "Uniquifies `label` by appending abbreviated `fluid` and `category`"

    label = simplify_label(row.label)

    if row.fluid.lower() == "blood":
        fluid_str = "B"
    elif row.fluid.lower() == "urine":
        fluid_str = "U"
    else:
        fluid_str = "X"
    if row.category.lower() == "hematology":
        cat_str = "H"
    elif row.category.lower() == "chemistry":
        cat_str = "C"
    elif row.category.lower() == "blood gas":
        cat_str = "G"
    else:
        cat_str = "X"

    new_label = label + f"[{fluid_str}-{cat_str}]"
    return new_label


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
    # Interpolate NaN values of numerical columns
    columns = [col for col in data.columns]
    categorical = ["50872", "51466", "51487", "51266", "51506", "51508", "51519"]
    continuous = [item for item in np.setdiff1d(columns, categorical)]
    data.loc[:, continuous] = (
        data.loc[:, continuous]
        .apply(pd.to_numeric, errors="coerce")
        .interpolate(limit_direction="both")
    )
    try:
        cat_mode = data.loc[:, categorical].mode().to_dict("r")[0]  # Create Dataset
        data = data.fillna(value=cat_mode)
    except Exception:
        print("No values in cat_mode")

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
            if not y["50912"].empty:
                # Add X to Dataset
                X_data_raw += [x]
                # Add Y to Dataset
                Y_data_raw += [y]

        # Move Start Interval
        start_date = start_date + pd.Timedelta(days=1)
    return X_data_raw, Y_data_raw, categorical, continuous


def featurize_X(X_data_raw: pd.DataFrame, categorical: list, continuous: list):
    "Returns pd.DataFrame of Labs"
    X = []
    means_raw = []
    modes_raw = []
    for x in X_data_raw:
        means = x.loc[:, continuous].mean()
        # means.index = [item + "_avg" for item in means.index]
        modes = x.loc[:, categorical].iloc[-1]
        # modes.index = [item + "_mode" for item in modes.index]
        means_raw += [means]
        modes_raw += [modes]
    mean_df = pd.DataFrame(means_raw)
    mode_df = pd.DataFrame(modes_raw).reset_index(drop=True)
    X = pd.concat([mean_df, mode_df], axis=1)
    return X


def featurize_Y(Y_data_raw: pd.DataFrame):
    "Returns pd.Series of Creatinine for day after X"
    Y_cr_only = [Y["50912"] for Y in Y_data_raw]
    Y = pd.Series([item.mean() for item in Y_cr_only], name="Creatinine_avg")
    return Y


def featurize(csv_file, labs_to_include: list):
    """Generate final `X` & `Y` dataframes used for modeling.
    Splits raw lab data into samples based on sliding window in `create_samples`.
    Featurize `X`, then Featurize `Y.  Returns `X` & `Y`.
    """
    pt_data = pd.read_csv(csv_file, header=[0, 1], index_col=0).labevents_value

    # Only consider patients who have all columns in `labs_to_include`
    cols_to_add = [
        item
        for item in [str(item) for item in labs_to_include]
        if item not in pt_data.columns
    ]
    # Add columns
    for col in cols_to_add:
        pt_data[col] = np.nan
    pt_data = pt_data.loc[:, pt_data.columns.isin(labs_to_include)]

    # Only create training example if patient has Creatinine Value (corresponding to itemid: 50912)
    if "50912" in pt_data.columns:
        # Try to Preprocess Data
        try:
            X_raw, Y_raw, categorical, continuous = create_samples(pt_data)
            x = featurize_X(X_raw, categorical, continuous)
            y = featurize_Y(Y_raw)
            if x.empty or y.empty:
                return None
            else:
                return {"x": x, "y": y}
        # If Error occurs, skip patient
        except Exception as e:
            print(f"Error occurred in file: {csv_file}.  Error: {e}")
            return None
