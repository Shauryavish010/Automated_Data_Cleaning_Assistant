def get_dataset_summary(df):

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": df.isnull().sum().sum(),
        "duplicate_rows": df.duplicated().sum()
    }