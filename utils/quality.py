import pandas as pd

def calculate_completeness(df):
    total_cells = df.shape[0] * df.shape[1]
    missing = df.isna().sum().sum()
    score = ((total_cells - missing) / total_cells) *100
    return round(score, 2)

def calculate_uniqueness(classification_df,column_stats):
    merged_df = classification_df.merge(
        column_stats,
        on="Column",
        how="left"
    )
    score = 0
    total_columns = len(merged_df)

    for _, row in merged_df.iterrows():
        detected_type = row["Detected Type"]
        unique_percent = row["Unique %"]

        if detected_type == "Indentifier":
            if unique_percent >= 95:
                score +=1
        elif detected_type == "Categorical":
            score +=1
        elif detected_type == "Financial":
            score +=1
        elif detected_type == "Boolean":
            score +=1
        elif detected_type == "Date/Time":
            score +=1
        elif detected_type == "Numeric":
            score +=1
        else:
            pass

    uniqueness_score = (score / total_columns) *100
    return round(uniqueness_score, 2)

def calculate_validity(df):
    return 100

def calculate_consistency(df):
    return 100

def calculate_quality_score(df, column_stats, classification_df):
    completeness = calculate_completeness(df)
    uniqueness = calculate_uniqueness(classification_df, column_stats)
    validity = calculate_validity(df)
    consistency = calculate_consistency(df)

    overall = round((completeness + uniqueness + validity + consistency) / 4, 2)
    return{
        "Overall": overall,
        "Completeness": completeness,
        "Uniqueness": uniqueness,
        "Validity": validity,
        "Consistency": consistency
    }



