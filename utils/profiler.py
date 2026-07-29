import pandas as pd

def get_dataset_summary(df):

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": df.isnull().sum().sum(),
        "duplicate_rows": df.duplicated().sum()
    }


def get_column_statistics(df):
    statistics = []

    for column in df.columns:
        series = df[column]
        statistics.append({
            "Column": column,
            "Pandas Type": str(series.dtype),
            "Rows": len(series),
            "Missing Values": series.isna().sum(),
            "Missing %": round(series.isna().mean()*100, 2),
            "Unique Values": series.nunique(),
            "Unique %": round(series.nunique()/len(series)*100, 2),
            "Duplicate Values": (len(series) - series.nunique())
        })
    
    return pd.DataFrame(statistics)