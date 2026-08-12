def generate_dataset_report(summary, quality, recommendation_df, cleaning_report):
    report = "# Dataset Report\n\n"

    report += "## Dataset Summary\n\n"
    report += f"- **Rows:** {summary['rows']}\n"
    report += f"- **Columns:** {summary['columns']}\n"
    report += f"- **Missing Values:** {summary['missing_values']}\n"
    report += f"- **Duplicate Rows:** {summary['duplicate_rows']}\n"
    report += f"- **Overall Quality Score:** {quality['Overall']}%\n\n"

    report += "## Quality Assesment\n\n"
    if quality["Overall"] >= 90:
        report += (
            "The dataset has a **high overall quality**. "
            "Most columns are complete and suitable for analysis.\n\n"
        )
    elif quality["Overall"] >= 75:
        report += (
            "The dataset has a **moderate quality**. "
            "Some cleaning is recommended before analysis.\n\n"
        )
    else:
        report += (
            "The dataset has a **low quality**. "
            "Significant cleaning is recommended.\n\n"
        )

    report += "## High Risk Column\n\n"
    high_risk = recommendation_df[
        recommendation_df["Risk"] == "High"
    ]

    if high_risk.empty:
        report += "No high-risk columns detected.\n\n"
    else:
        for column in high_risk["Column"]:
            report += f"- {column}\n"
        report += "\n"

    report += "## Cleaning Summary\n\n"
    for item in cleaning_report:
        report += f"- {item}\n"
    report += "\n"

    report += "## Final Recommendation\n\n"
    if quality["Overall"] >= 95:
        report += (
            "The dataset is ready for dashboarding, "
            "machine learning, and statistical analysis."
        )
    elif quality["Overall"] >= 80:
        report += (
            "The dataset is suitable for analysis after "
            "reviewing the highlighted high-risk columns."
        )
    else:
        report += (
            "Further data cleaning is recommended before "
            "using this dataset for analysis."
        )

    return report