import pandas as pd


def clean_data(df, remove_duplicates=False, fill_missing=False, convert_datetime=False, trim_spaces=False):
    cleaned_df = df.copy()

    summary = []
    if remove_duplicates:
        before = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        removed = before - len(cleaned_df)
        summary.append(f"Removed {removed} duplicate rows.")

    if fill_missing:
        total_missing = cleaned_df.isnull().sum().sum()
        for column in cleaned_df.columns:
            if cleaned_df[column].dtype == "object":
                mode = cleaned_df[column].mode()
                if not mode.empty:
                    cleaned_df[column] = cleaned_df[column].fillna(mode[0])
            else:
                cleaned_df[column] = cleaned_df[column].fillna(
                    cleaned_df[column].median()
                )

        summary.append(f"Filled {total_missing} missing values.")

    if convert_datetime:
        converted = 0

        for column in cleaned_df.columns:
            if cleaned_df[column].dtype == "object":
                try:
                    cleaned_df[column] = pd.to_datetime(
                        cleaned_df[column]
                    )
                    converted += 1
                except:
                    pass

        summary.append(
            f"Converted {converted} columns to datetime."
        )

    if trim_spaces:
        text_columns = cleaned_df.select_dtypes(
            include=["object"]
        ).columns

        for column in text_columns:
            cleaned_df[column] = cleaned_df[column].str.strip()

        summary.append(
            f"Trimmed spaces from {len(text_columns)} text columns."
        )
    return cleaned_df, summary


def apply_recommendation(cleaned_df, column, recommendation):
    if recommendation == "Fill Median":
        cleaned_df[column] = cleaned_df[column].fillna(cleaned_df[column].median())
    elif recommendation == "Fill Mode":
        mode = cleaned_df[column].mode()
        if not mode.empty:
            cleaned_df[column] = cleaned_df[column].fillna(mode.iloc[0])
    elif recommendation == "Fill Mean":
        cleaned_df[column] = cleaned_df[column].fillna(cleaned_df[column].mean())
    elif recommendation =="Remove Duplicates":
        cleaned_df.drop_duplicates(inplace = True)
    elif recommendation == "Trim Spaces":
        cleaned_df[column] = cleaned_df[column].astype(str).str.strip()
    elif recommendation == "Convert Date/Time":
        cleaned_df[column] = pd.to_datetime(cleaned_df[column], errors = "coerce")
    elif recommendation == "Drop Missing Rows":
        cleaned_df.dropna(
            subset=[column],
            inplace = True
        )
    return cleaned_df

def auto_clean(df, recommendation_df):
    cleaned_df = df.copy()
    summary =[]

    for _, row in recommendation_df.iterrows():
        column = row["Column"]
        recommendation = row["Recommendation"]
        auto = row["Auto Applicable"]
        if not auto:
            continue

        cleaned_df = apply_recommendation(cleaned_df, column, recommendation)
        summary.append(f"{column}: {recommendation}")
        return cleaned_df, summary

def generate_cleaning_report(cleaning_summary):
    median = 0
    mode = 0
    mean = 0
    duplicates = 0
    datetime_cols = 0
    skipped = 0

    for item in cleaning_summary:
        if "Fill median" in item:
            median +=1
        elif "Fill Mode" in item:
            mode +=1
        elif "Fill Mean" in item:
            mean +=1    
        elif "Remove Duplicates" in item:
            duplicates +=1
        elif "Convert Date/Time" in item:
            datetime_cols +=1
        else:
            skipped +=1

    report =[]

    if median > 0:
        report.append(
            f"Filled missing values in {median} column(s) using Median."
        )
    if mode > 0:
        report.append(
            f"Filled missing values in {mode} column(s) using Mode."
        )
    if mean > 0:
        report.append(
            f"Filled missing values in {mean} column(s) using Mean."
        )
    if duplicates > 0:
        report.append(
            f"Removed duplicate rows."
        )
    if datetime_cols > 0:
        report.append(
            f"Converted {datetime_cols} column(s) to DateTime."
        )
    if skipped > 0:
        report.append(
            f"{skipped} operation(s) were skipped because manual review is required."
        )
        
    report.append("Cleaning Completed Successfully")
    return report