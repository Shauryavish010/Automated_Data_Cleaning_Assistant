import pandas as pd

RULES = {
    "Identifier": {
        "recommendation": "Leave Missing",
        "reason": "Identifiers should never be fabricated.",
        "auto": False
    },

    "Date/Time":{
        "recommendation": "Review",
        "reason": "It affects chronological analysis.",
        "auto": False
    },

    "Financial": {
        "recommendation": "Fill Median",
        "reason": "Median is less affected by outliers.",
        "auto": True
    },

    "Numeric": {
        "recommendation": "Fill Median",
        "reason": "Median preserves numeric distribution.",
        "auto": True
    },

    "Categorical": {
        "recommendation": "Fill Mode",
        "reason": "Mode works well for repeated categories.",
        "auto": True
    },

    "Boolean": {
        "recommendation": "Review",
        "reason": "Boolean values depend on business logic.",
        "auto": False
    },

    "Contact": {
        "recommendation": "Leave Missing",
        "reason": "Contact cannot be safely guessed.",
        "auto": False
    },

    "Location": {
        "recommendation": "Leave Missing",
        "reason": "Fake Location can mislead analysis.",
        "auto": False
    },

    "Free Text": {
        "recommendation": "Leave Missing",
        "reason": "Free text cannot be reliably inferred.",
        "auto": False
    },

    "Unknown": {
        "recommendation": "Review",
        "reason": "Column type could not be identified.",
        "auto": False
    }
}

def generate_recommendations(df, classification_df):
    recommendations = []

    for _, row in classification_df.iterrows():
        column = row["Column"]
        detected_type = row["Detected Type"]

        missing = df[column].isna().sum()
        missing_percent = round((missing / len(df)) * 100, 2)

        rule = RULES.get(detected_type, RULES["Unknown"])

        recommendations.append({
            "Column": column,
            "Detected Type": detected_type,
            "Missing Values": missing,
            "Missing %": missing_percent,
            "Recommendation": rule["recommendation"],
            "Reason": rule["reason"],
            "Auto Applicable": rule["auto"]
        })
    return pd.DataFrame(recommendations)