import streamlit as st
import pandas as pd
import plotly.express as px
from utils.profiler import get_dataset_summary, get_column_statistics
from utils.cleaner import clean_data, auto_clean, generate_cleaning_report
from utils.report import generate_dataset_report
from utils.dashboard import missing_value_summary, get_dashboard_metrics, get_top_risky_columns, get_risk_distribution, get_type_distribution
from utils.file_loader import load_csv
from utils.classifier import classify_columns
from utils.recommendation import generate_recommendations
from utils.quality import calculate_quality_score

st.set_page_config(
    page_title="Automated Data Cleaning Assistant",
    #page_icon="",
    layout="wide"
)

st.title("Automated Data Cleaning Assistant")

st.markdown(
    """
    **Analyze → Detect → Recommend → Clean → Report**

    Upload a CSV dataset to automatically assess data quality,
    identify potential issues, generate intelligent cleaning
    recommendations, and safely clean your data.
    """
)

#File Uploader

uploaded_file = st.file_uploader(
    'Choose a CSV file',
     type=['csv']
)

with st.sidebar:
    st.header("ADCA")
    st.markdown("### Pipeline")
    st.markdown(
        """
        1. 📁 Upload
        2. 🔍 Profile
        3. 🧠 Classify
        4. 🩺 Assess Quality
        5. 💡 Recommend
        6. 🧹 Clean
        7. 📋 Report
        """
    )
    st.divider()
    st.markdown("### Tech Stack")
    st.caption("Python")
    st.caption("Pandas")
    st.caption("Streamlit")
    st.caption("Plotly")

    st.divider()

    st.caption("Automated Data Cleaning Assistant")
    st.caption("Version 1.0")

#If file is uploaded
if uploaded_file is not None:
    try:
        df = load_csv(uploaded_file)
        st.success(
            f"Dataset loaded successfully - "
            f"{df.shape[0]:,} rows x {df.shape[1]:,} columns"
        )

        summary = get_dataset_summary(df)

        rows = summary["rows"]
        columns = summary["columns"]
        missing_values = summary["missing_values"]
        duplicate_rows = summary["duplicate_rows"]


        classification_df = classify_columns(df)
        column_stats = get_column_statistics(df)
        recommendation_df = generate_recommendations(classification_df, column_stats)
        quality = calculate_quality_score(df, column_stats, classification_df)

        dashboard_metrics = get_dashboard_metrics(recommendation_df)
        top_risky = get_top_risky_columns(recommendation_df)
        risk_distribution = get_risk_distribution(recommendation_df)
        type_distribution = get_type_distribution(classification_df)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "Overview",
                "Data Quality",
                "Recommendation",
                "Auto Cleaning",
                "Manual Cleaning"
            ]
        )

        with tab1:
            st.subheader("Dataset Overview")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Rows",
                    f"{rows:,}"
                )
            with col2:
                st.metric(
                    "Total Columns",
                    f"{columns:,}"
                )
            with col3:
                st.metric(
                    "Missing Values",
                    f"{missing_values:,}"
                )
            with col4:
                st.metric(
                    "Duplicate Rows",
                    f"{duplicate_rows:,}"
                )
            st.divider()

            st.subheader("Dataset Preview")
            st.dataframe(
                df.head(10),
                width = "stretch",
                hide_index = True
            )
            st.divider()

            st.subheader("Semantic Type Distribution")
            st.bar_chart(
                type_distribution.set_index(
                    "Detected Type"
                )
            )
            st.divider()

            st.subheader("Column Classification")
            st.caption(
                "Columns are classified using semantic rules "
                "based on names, data types and value patterns."
            )
            st.dataframe(
                classification_df,
                width = "stretch",
                hide_index = True
            )

        with tab2:
            st.subheader("Data Quality Score")

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric(
                    "Overall",
                    f"{quality['Overall']}%"
                )
            with col2:
                st.metric(
                    "Completeness",
                    f"{quality['Completeness']}%"
                )
            with col3:
                st.metric(
                    "Uniqueness",
                    f"{quality['Uniqueness']}%"
                )
            with col4:
                st.metric(
                    "Validity",
                    f"{quality['Validity']}%"
                )
            with col5:
                st.metric(
                    "Consistency",
                    f"{quality['Consistency']}%"
                )
            st.divider()


            st.subheader("Risk Overview")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "High Risk",
                    dashboard_metrics["high_risk"]
                )
            with col2:
                st.metric(
                    "Medium Risk",
                    dashboard_metrics["medium_risk"]
                )
            with col3:
                st.metric(
                    "Low Risk",
                    dashboard_metrics["low_risk"]
                )
            with col4:
                st.metric(
                    "Auto Cleanable",
                    dashboard_metrics["auto"]
                )
            st.divider()

            st.subheader("Risk Distribution")
            st.bar_chart(
                risk_distribution.set_index("Risk")
            )
            st.divider()

            st.subheader("Top 5 Critical Column")
            st.caption("Columns ranked by risk score and priority.")

            st.dataframe(
                top_risky,
                width = "stretch",
                hide_index = True
            )
            st.divider()

            st.subheader("Missing Values Distribution")
            missing = missing_value_summary(df)

            if not missing.empty:
                fig = px.bar(
                    x = missing.index,
                    y = missing.values,
                    labels = {
                        "x" : "Columns",
                        "y" : "Missing Values"
                    },
                    title = "Missing Values by Column"
                )

                st.plotly_chart(
                    fig, 
                    width = "stretch"
                )

            else:
                st.success("No missing values found.")

            st.divider()

            st.subheader("Column Statistics")
            st.dataframe(
                column_stats,
                width = "stretch",
                hide_index = True
            )

        with tab3:
            st.subheader("Cleaning Recommendation")
            st.markdown(
                """
                Recommendations are generated using:

                - Semantic column classification
                - Missing-value patterns
                - Risk scoring
                - Priority assignment
                - Auto-applicable cleaning rules
                """
            )

            st.info(
                "P1 = Highest Priority | "
                "P2 = Medium Priority | "
                "P3 = Low Priority"
            )

            st.dataframe(
                recommendation_df,
                width = "stretch",
                hide_index = True
            )

        with tab4:
            st.subheader("Intelligent Auto Cleaning")
            st.markdown(
                """Automatically applies only safe cleaning operations 
                recommended by the recommendation engine"""
            )
            st.markdown(
                "Only recommendation marked as "
                "'Auto-Applicable' willbe executed automatically" 
            )

            if st.button(
                "Auto Clean Dataset",
                type = "primary",
                width = "stretch"
            ):
                cleaned_df, cleaning_summary = auto_clean(df, recommendation_df)
                st.success("Dataset Cleaned Sucessfully")

                cleaning_report = generate_cleaning_report(cleaning_summary)
                st.subheader("Cleaning Report")
                for line in cleaning_report:
                    st.write(line)
                st.divider()

                cleaned_summary = get_dataset_summary(cleaned_df)
                cleaned_column_stats = get_column_statistics(cleaned_df)
                cleaned_classification = classify_columns(cleaned_df)
                cleaned_quality = calculate_quality_score(cleaned_df, cleaned_column_stats, cleaned_classification)

                st.subheader("Before vs After")
                col1, col2, col3 = st.columns(3)

                quality_change = round(cleaned_quality["Overall"] - quality["Overall"], 2)
                missing_change = round(cleaned_summary["missing_values"] - missing_values)
                duplicate_change = round(cleaned_summary["duplicate_rows"] - duplicate_rows)

                with col1:
                    st.metric(
                        "Quality Score",
                        f"{cleaned_quality['Overall']}%",
                        delta = f"{quality_change:+.2f}%"
                    )
                with col2:
                    st.metric(
                        "Missing Values",
                        f"{cleaned_summary['missing_values']:,}",
                        delta = f"{missing_values:,}"
                    )
                with col3:
                    st.metric(
                        "Duplicate Rows",
                        f"{cleaned_summary['duplicate_rows']:,}",
                        delta = f"{duplicate_change:,}"
                    )
                st.divider()

                comparison_df = pd.DataFrame(
                    {
                        "Metric": ["Missing Values", "Duplicate Rows", "Quality Score"],
                        "Before": [missing_values, duplicate_rows, quality["Overall"]],
                        "After": [cleaned_summary["missing_values"], cleaned_summary["duplicate_rows"], cleaned_quality["Overall"]]
                    }
                )

                st.dataframe(
                    comparison_df,
                    width = "stretch",
                    hide_index = True
                )

                st.divider()

                st.subheader("Dataset Assessment Report")
                ai_report = generate_dataset_report(cleaned_summary, cleaned_quality, recommendation_df, cleaning_report)
                st.markdown(ai_report)

                st.divider()

                st.subheader("Cleaned Dataset Preview")

                st.dataframe(
                    cleaned_df.head(10),
                    width = "stretch",
                    hide_index = True
                )

                st.download_button(
                    label = "Download Cleaned Dataset",
                    data = cleaned_df.to_csv(index = False),
                    file_name = "auto_cleaned_dataset.csv",
                    mime = "text/csv",
                    width = "stretch"
                )

        with tab5:
            st.subheader("Manual Data Cleaning")
            st.caption(
                "Use these controls when you want direct control "
                "over cleaning option"
            )

            remove_duplicates = st.checkbox("Remove Duplicate Rows")
            fill_missing = st.checkbox("Fill Missing Values")
            convert_datetime = st.checkbox("Convert Date Columns Automatically")
            trim_spaces = st.checkbox("Trim Extra Spaces from Text Columns")

            if st.button (
                "Clean Data",
                type = "primary"
            ):
                cleaned_df, cleaning_summary = clean_data(df, remove_duplicates=remove_duplicates, 
                                                          fill_missing=fill_missing,
                                                          convert_datetime=convert_datetime,
                                                          trim_spaces=trim_spaces)
                st.success("Data Cleaning Completed")
                st.dataframe(
                    cleaned_df.head(10),
                    width = "stretch",
                    hide_index = True
                )
                if cleaning_summary:
                    st.subheader("Cleaning Summary")

                    for item in cleaning_summary:
                        st.write(f"{item}")
                else:
                    st.info("No cleaning operation were selected")

                st.download_button(
                    label = "Download Cleaned Dataset",
                    data = cleaned_df.to_csv(index= False),
                    file_name = "cleaned_data.csv",
                    mime = "text/csv"
                )

    except Exception as e:
        st.error(f"Error Reading file: {e}")
        st.exception(e)


else:
    st.info("Upload a CSV file to get started.")

    st.markdown(
         """
        ### What ADCA can do

        | Feature | Description |
        |---|---|
        | Profiling | Analyze dataset structure |
        | Classification | Detect semantic column types |
        | Quality Score | Measure dataset health |
        | Recommendations | Suggest cleaning actions |
        | Risk Engine | Prioritize data issues |
        | Auto Cleaning | Apply safe cleaning rules |
        | Reports | Generate dataset assessment |
        | ⬇Export | Download cleaned datasets |
        """
    )
