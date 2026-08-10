import pandas as pd


def missing_value_summary(df):
    missing = df.isnull().sum()
    missing = missing[missing>0]
    return missing.sort_values(ascending=False)

def get_dashboard_metrics(recommendation_df):
    high_risk = (recommendation_df["Risk"] == "High").sum()
    medium_risk = (recommendation_df["Risk"] == "Medium").sum()
    low_risk = (recommendation_df["Risk"] == "Low").sum()

    p1 = (recommendation_df["Priority"] == "P1").sum()
    p2 = (recommendation_df["Priority"] == "P2").sum()
    p3 = (recommendation_df["Priority"] == "P3").sum()

    auto = recommendation_df["Auto Applicable"].sum()
    manual = len(recommendation_df) - auto

    return{
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "p1": p1,
        "p2": p2,
        "p3": p3,
        "auto": auto,
        "manual": manual
    }


def get_top_risky_columns(recommendation_df):
    top_risk_columns = recommendation_df.sort_values(
        by = ["Risk Score", "Priority"], ascending = [False, True]).head(5)
    return top_risk_columns[
        ["Column", "Risk Score", "Risk", "Priority", "Recommendation", ]
    ]

def get_risk_distribution(recommendation_df):
    risk_distribution = (
        recommendation_df["Risk"]
        .value_counts()
        .reset_index()
    )

    risk_distribution.columns = ["Risk", "Count"]
    return risk_distribution

def get_type_distribution(classification_df):
    type_distribution = (
        classification_df["Detected Type"]
        .value_counts()
        .reset_index()
    )

    type_distribution.columns = ["Detected Type","Count"]
    return type_distribution