import pandas as pd

RULES = {
    "Identifier": {
        "recommendation": "Leave Missing",
        "reason": "Identifiers should never be fabricated.",
        "risk": "High",
        "priority": "High",
        "auto": False
    },
    "Date/Time": {
        "recommendation": "Review",
        "reason": "Dates affect chronological analysis.",
        "risk": "Medium",
        "priority": "High",
        "auto": False
    },
    "Financial": {
        "recommendation": "Fill Median",
        "reason": "Median is robust against outliers.",
        "risk": "Low",
        "priority": "Medium",
        "auto": True
    },
    "Numeric": {
        "recommendation": "Fill Median",
        "reason": "Median preserves numeric distribution.",
        "risk": "Low",
        "priority": "Medium",
        "auto": True
    },
    "Categorical": {
        "recommendation": "Fill Mode",
        "reason": "Most frequent category is appropriate.",
        "risk": "Low",
        "priority": "Medium",
        "auto": True
    },
    "Boolean": {
        "recommendation": "Fill Mode",
        "reason": "Binary values are best filled using mode.",
        "risk": "Low",
        "priority": "Low",
        "auto": True
    },
    "Text": {
        "recommendation": "Review",
        "reason": "Text requires contextual understanding.",
        "risk": "Medium",
        "priority": "Medium",
        "auto": False
    },
    "Unknown": {
        "recommendation": "Review",
        "reason": "Unknown column type.",
        "risk": "High",
        "priority": "High",
        "auto": False
    }
}

def generate_recommendations(classification_df, column_stats):

    merged_df = classification_df.merge(
        column_stats,
        on="Column",
        how="left"
    )

    #print("Merged Columns:", merged_df.columns.tolist())

    recommendations = []

    for i, row in merged_df.iterrows():

        try:
            #print(f"\nProcessing row {i}")
            #print(row.to_dict())

            detected_type = row["Detected Type"]
            column = row["Column"]

            missing = row["Missing Values"]
            missing_percent = row["Missing %"]

            rule = get_dynamic_recommendation(detected_type, missing_percent)

            recommendations.append({
                "Column": column,
                "Detected Type": detected_type,
                "Missing Values": missing,
                "Missing %": missing_percent,
                "Recommendation": rule["recommendation"],
                "Risk Score": rule["risk_score"],
                "Risk": rule["risk"],
                "Priority": rule["priority"],
                "Reason": rule["reason"],
                "Auto Applicable": rule["auto"]
            })

        except Exception as e:
            #print("FAILED ROW:")
            #print(row.to_dict())
            raise e

    return pd.DataFrame(recommendations)

def get_priority(risk):
    if risk == "High":
        return "P1"
    elif risk == "Medium":
        return "P2"
    else:
        return "P3"
    risk = "Low"


def calculate_risk_score(detected_type, missing_percent):
    score = 0

    if missing_percent == 0:
        score += 0
    elif missing_percent < 1:
        score += 5
    elif missing_percent < 5:
        score += 20
    elif missing_percent < 20:
        score += 50
    else:
        score += 80

    if detected_type == "Identifier":
        score += 20
    elif detected_type == "Date/Time":
        score += 15
    elif detected_type in ["Financial", "Numeric"]:
        score += 10
    elif detected_type == "Text":
        score += 8
    elif detected_type == "Categorical":
        score += 5
    elif detected_type == "Boolean":
        score += 2

    return min(score, 100)

def get_dynamic_recommendation(detected_type, missing_percent):
    risk_score = calculate_risk_score(detected_type, missing_percent)
    if detected_type == "Identifier":
        if missing_percent == 0:
            return {
                "recommendation": "No Action",
                "reason": "Identifier column is complete.",
                "risk_score": risk_score,
                "risk": "Low",
                "priority": get_priority("Low"),
                "auto": True
            }
        else:
            return {
                "recommendation": "Leave Missing",
                "reason": "Identifiers should never be fabricated.",
                "risk_score": risk_score,
                "risk": "High",
                "priority": get_priority("High"),
                "auto": False
            }
    if detected_type in ["Financial", "Numeric"]:
        if missing_percent == 0:
            return {
                "recommendation": "No Action",
                "reason": "Column is complete.",
                "risk_score": risk_score,
                "risk": "Low",
                "priority": get_priority("Low"),
                "auto": True
            }

        elif missing_percent < 5:
            return {
                "recommendation": "Fill Median",
                "reason": "Small amount of missing data.",
                "risk_score": risk_score,
                "risk": "Low",
                "priority": get_priority("Medium"),
                "auto": True
            }

        elif missing_percent <= 20:
            return {
                "recommendation": "Review",
                "reason": "Moderate amount of missing data.",
                "risk_score": risk_score,
                "risk": "Medium",
                "priority": get_priority("High"),
                "auto": False
            }

        else:
            return {
                "recommendation": "Consider Dropping Column",
                "reason": "Large amount of missing data.",
                "risk_score": risk_score,
                "risk": "High",
                "priority": get_priority("High"),
                "auto": False
            }
    if detected_type == "Categorical":
        if missing_percent == 0:
            #print("Inside Categorical Rule")
            #print(detected_type, missing_percent)
            return {
                "recommendation": "No Action",
                "reason": "Column is complete.",
                "risk_score": risk_score,
                "risk": "Low",
                "priority": get_priority("Low"),
                "auto": True
            }

        elif missing_percent < 10:
            return {
                "recommendation": "Fill Mode",
                "reason": "Few missing values in a categorical column.",
                "risk_score": risk_score,
                "risk": "Low",
                "priority": get_priority("Medium"),
                "auto": True
            }

        else:
            return {
                "recommendation": "Review",
                "reason": "Too many missing categorical values.",
                "risk_score": risk_score,
                "risk": "Medium",
                "priority": get_priority("High"),
                "auto": False
            }
    if detected_type == "Date/Time":
        if missing_percent == 0:
            #print("Inside Date Rule")
            #print(detected_type, missing_percent)
            return{
                "recommendation": "No Action",
                "reason": "Date column is complete.",
                "risk_score": risk_score,
                "risk": "Low",
                "priority": get_priority("Low"),
                "auto": True
            }
        elif missing_percent < 1:
            return{
                "recommendation": "Drop Missing Rows",
                "reason": "Very few rows contain missing values.",
                "risk_score": risk_score,
                "risk": "Low",
                "priority": get_priority("Medium"),
                "auto": True
            }
        elif missing_percent <= 10:
            return{
                "recommendation": "Leave Missing",
                "reason": "Missing dates may represent real events.",
                "risk_score": risk_score,
                "risk": "Medium",
                "priority": get_priority("High"),
                "auto": False
            }
        else:
            return{
                "recommendation": "Review manually",
                "reason": "large amount of missing dates.",
                "risk_score": risk_score,
                "risk": "High",
                "priority": get_priority("High"),
                "auto": False
            }
    return {
    "recommendation": "Review",
    "reason": "No rule available yet.",
    "risk_score": risk_score,
    "risk": "Medium",
    "priority": get_priority("Medium"),
    "auto": False
    }
        
#print(get_dynamic_recommendation("Identifier", 0))
#print(get_dynamic_recommendation("Identifier", 5))
#print(get_dynamic_recommendation("Financial", 3))
   