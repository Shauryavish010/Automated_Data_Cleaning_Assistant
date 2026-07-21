import pandas as pd 
import re

SEMANTIC_RULES = {

    "Identifier": {
        "tokens": [
            "id",
            "key",
            "number",
            "no",
            "code",
            "uuid",
            "identifier",
            "serial",
            "reference"
        ],
        "negative_tokens": [],
        "priority": 100
    },

    "Date/Time": {
        "tokens": [
            "date",
            "time",
            "timestamp",
            "created",
            "updated",
            "modified",
            "dob",
            "birth"
        ],
        "negative_tokens": [],
        "priority": 95
    },

    "Financial": {
        "tokens": [
            "price",
            "cost",
            "sales",
            "revenue",
            "profit",
            "discount",
            "tax",
            "income",
            "salary",
            "amount"
        ],
        "negative_tokens": [
            "number",
            "key",
            "id",
            "code"
        ],
        "priority": 90
    },

    "Numeric": {

        "tokens": [],
        "negative_tokens": [],
        "priority": 30
    },

    "Categorical": {
        "tokens": [
            "category",
            "subcategory",
            "gender",
            "city",
            "country",
            "state",
            "department",
            "status",
            "color"
        ],
        "negative_tokens": [],
        "priority": 60
    },

    "Boolean": {
        "tokens": [
            "active",
            "enabled",
            "paid",
            "verified",
            "flag"
        ],
        "negative_tokens": [],
        "priority": 70
    },

    "Contact": {
        "tokens": [
            "email",
            "phone",
            "mobile",
            "contact"
        ],
        "negative_tokens": [],
        "priority": 90
    },

    "Location": {
        "tokens": [
            "latitude",
            "longitude",
            "lat",
            "lon",
            "zipcode",
            "postal",
            "address"
        ],
        "negative_tokens": [],
        "priority": 80
    },

    "Free Text": {
        "tokens": [
            "comment",
            "description",
            "remarks",
            "notes",
            "feedback"
        ],
        "negative_tokens": [],
        "priority": 40
    }

}

def normalize_column_name(column_name):
    name = str(column_name)
    name = re.sub(
        r"([a-z])([A-Z])",
        r"\1_\2",
        name
    )
    name = name.lower()
    name = re.sub(
        r"[^a-z0-9]+",
        "_",
        name
    )
    return name.strip("_")

def analyze_column(series):
    non_null = series.dropna()
    if len(non_null) == 0:
        return {
            "unique_ratio": 0,
            "date_ratio": 0,
            "email_ratio": 0,
            "boolean_ratio": 0,
            "average_text_length": 0, 
        }
    unique_ratio = non_null.nunique() / len(non_null)
    text_values = non_null.astype(str)
    email_ratio = text_values.str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$").mean()
    boolean_values = {"true", "false", "yes", "no", "y", "n", "1", "0"}
    boolean_ratio = (
        text_values.str.lower().isin(boolean_values).mean()
    )

    average_text_length = (text_values.str.len().mean())

    date_ratio = 0

    if series.dtype == "object":
        try:
            parsed_dates = pd.to_datetime(non_null, errors = "coerce")
            
            date_ratio = parsed_dates.notna().mean()
        except Exception:
            date_ratio = 0

    return {
        "unique_ratio": unique_ratio,
        "date_ratio": date_ratio,
        "email_ratio": email_ratio,
        "boolean_ratio": boolean_ratio,
        "average_text_length": average_text_length
    }

def classify_column(column_name, series):
    normalized_name = normalize_column_name(column_name)
    signals = analyze_column(series)

    scores = {
        "Identifier": 0,
        "Date/Time": 0,
        "Financial": 0,
        "Categorical": 0,
        "Contact": 0,
        "Location": 0,
        "Boolean": 0,
        "Free Text": 0, 
        "Numeric": 0,
    }

    reasons = []

    # Column name signals

    for category, rule in SEMANTIC_RULES.items():
        for keyword in rule["tokens"]:
            if keyword in normalized_name:
                scores[category] += 40
                reasons.append(
                    f"Column name contains '{keyword}'"
                )
                break
    
    if signals["unique_ratio"] >0.95:
        scores["Identifier"] += 30
        reasons.append(
            f"More than 95% of values are unique"
        )

    if signals["date_ratio"] >0.80:
        scores["Date/Time"] += 30
        reasons.append(
            f"Most values can be parsed as dates"
        )

    if signals["email_ratio"] >0.80:
        scores["Contact"] += 60
        reasons.append(
            f"Most values match email format"
        )

    if signals["boolean_ratio"] >0.90:
        scores["Boolean"] += 60
        reasons.append(
            f"Values follow a boolean pattern"
        )

    if pd.api.types.is_numeric_dtype(series):
        scores["Numeric"] += 30
        reasons.append(
            f"Column contains numeric values"
        )
    
    if (
        series.dtype == "object"
        and signals["unique_ratio"] < 0.20
    ):
        scores["Categorical"] += 30
        reasons.append(
            f"Column contains repeated text values"
        )

    if (
        series.dtype == "object"
        and signals["average_text_length"] > 50
    ):
        scores["Free Text"] += 40
        reasons.append(
            f"Column contains long text values"
        )
    
    detected_type = max(
        scores, key=scores.get
    )

    highest_score = scores[detected_type]

    if highest_score == 0:
        detected_type = "Unknown"

    confidence = min(highest_score, 100)

    return{
        "detected_type": detected_type,
        "confidence": confidence,
        "reason": "; ".join(reasons)
    }



def classify_columns(df):
    classifications = []

    for column in df.columns:
        result = classify_column(
            column,
            df[column]
        )

        classifications.append({
            "Column": column,
            "Pandas Type": str(df[column].dtype),
            "Detected Type": result["detected_type"],
            "Detection Score": result["confidence"],
            "Detection Reason": result["reason"]
        })

    return pd.DataFrame(classifications)