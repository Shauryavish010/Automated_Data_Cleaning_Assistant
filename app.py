import streamlit as st
import pandas as pd
import plotly.express as px
from utils.profiler import get_dataset_summary, get_column_statistics
from utils.cleaner import clean_data, auto_clean
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

st.write("Upload a CSV to analyze and clean your dataset.")

#File Uploader

uploaded_file = st.file_uploader(
    'Choose a CSV file',
     type=['csv']
)

#If file is uploaded
if uploaded_file is not None:
    try:
        df = load_csv(uploaded_file)
        st.success("File Uploaded Successfully")
        st.dataframe(df.head())
        st.subheader("Data Information")

        st.subheader("Column Classification")
        classification_df = classify_columns(df)
        st.dataframe(
            classification_df,
            use_container_width=True,
            hide_index=True
        )

        #Statistics
        summary = get_dataset_summary(df)

        rows = summary["rows"]
        columns = summary["columns"]
        missing_values = summary["missing_values"]
        duplicate_rows = summary["duplicate_rows"]

        classification_df = classify_columns(df)
        column_stats = get_column_statistics(df)

        recommendation_df = generate_recommendations(classification_df, column_stats)
        st.subheader("Cleaning Recommendations")
        st.dataframe(
            recommendation_df,
            width="stretch",
            hide_index=True
        )

        dashboard_metrics = get_dashboard_metrics(recommendation_df)
        st.subheader("Dataset Health Dashboard")
        quality = calculate_quality_score(df, column_stats, classification_df)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Overall Quality", f"{quality['Overall']}%")
        with col2:
            st.metric("High Risk", dashboard_metrics["high_risk"])
        with col3:
            st.metric("Medium Risk", dashboard_metrics["medium_risk"])
        with col4:
            st.metric("Low Risk", dashboard_metrics["low_risk"])

        col5, col6, col7, col8 = st.columns(4)

        with col5:
            st.metric("P1 Priority", dashboard_metrics["p1"])
        with col6:
            st.metric("P2 Priority", dashboard_metrics["p2"])
        with col7:
            st.metric("P3 Priority", dashboard_metrics["p3"])
        with col8:
            st.metric("Auto Cleanable", dashboard_metrics["auto"])
        

        top_risky = get_top_risky_columns(recommendation_df)
        st.subheader("Top 5 Critical Columns")
        st.dataframe(
            top_risky,
            width="stretch",
            hide_index=True
        )

        risk_distribution = get_risk_distribution(recommendation_df)
        st.subheader("Risk Distribution")
        st.bar_chart(risk_distribution.set_index("Risk"))

        type_distribution = get_type_distribution(classification_df)
        st.subheader("Semantic Type Distribution")
        st.bar_chart(type_distribution.set_index("Detected Type"))

        st.subheader("Column Statistics")
        st.dataframe(
            column_stats,
            width="stretch",
            hide_index=True
        )

        quality = calculate_quality_score(df, column_stats, classification_df)
        st.subheader("Data Quality Score")
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Overall", f"{quality['Overall']}%")
        col2.metric("Completeness", f"{quality['Completeness']}%")
        col3.metric("Uniqueness", f"{quality['Uniqueness']}%")
        col4.metric("Validity", f"{quality['Validity']}%")
        col5.metric("Consistency", f"{quality['Consistency']}%")

        #Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows", rows)
        col2.metric("Total Columns", columns)
        col3.metric("Missing Values", missing_values)
        col4.metric("Duplicate Rows", duplicate_rows)

        missing = missing_value_summary(df)

        if not missing.empty:
            st.subheader("Missing Values Summary")

            fig = px.bar(
                x = missing.index,
                y = missing.values,
                labels = {
                    "x : Columns",
                    "y : Missing Values"
                },
                title = "Missing Values Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("NO Missing Values Found")
        
        st.subheader("Column Data types")
        st.dataframe(
            df.dtypes.astype(str).reset_index().rename(
                columns={
                    "index": "Column Name",
                    0: "Data Type"                
                }
            )
        )

        st.subheader("Missing Values by Columns")
        missing_df = df.isnull().sum().reset_index()
        missing_df.columns = ["Column Name", "Missing Values"]
        with st.expander("View Missing Values Table"):
            st.dataframe(missing_df, use_container_width=True)

        #Data Cleaning Options 

        st.subheader("Intelligent Auto Cleaning")
        st.write(
            "Automatically applies only safe cleaning operations "
            "based on the recommendation engine."
        )
        if st.button("Auto Clean Dataset"):
            cleaned_df, cleaning_summary = auto_clean(df, recommendation_df)
            st.success("Dataset Cleaned")

            cleaned_summary = get_dataset_summary(cleaned_df)
            cleaned_column_stats = get_column_statistics(cleaned_df)
            cleaned_classification = classify_columns(cleaned_df)
            cleaned_quality = calculate_quality_score(
                cleaned_df, cleaned_column_stats, cleaned_classification
            )

            comparison_df = pd.DataFrame({
                "Metric":[
                    "Missing Values",
                    "Duplicate Rows",
                    "Quality Score"
                ],
                "Before":[
                    missing_values,
                    duplicate_rows,
                    quality["Overall"]
                ],
                "After":[
                    cleaned_summary["missing_values"],
                    cleaned_summary["duplicate_rows"],
                    cleaned_quality["Overall"]
                ]
            })

            st.subheader("Before and After Comparison")
            st.dataframe(
                comparison_df, 
                width = "stretch",
                hide_index = True
            )

            st.subheader("Cleaning Summary")
            for item in cleaning_summary:
                st.write(f"{item}")

            st.subheader("Cleaned Data Preview")
            st.dataframe(
                cleaned_df.head(10),
                width = "stretch"
            )

            st.download_button(
                label = "Download Auto Cleaned CSV",
                data = cleaned_df.to_csv(index = False),
                file_name = "auto_cleaned_dataset.csv",
                mime = "text/csv"
            )

        st.subheader("Data Cleaning Options")
        remove_duplicates = st.checkbox("Remove Duplicate Rows")
        fill_missing = st.checkbox("Fill Missing Values")
        convert_datetime = st.checkbox("Convert Date Columns Automatically")
        trim_spaces = st.checkbox("Trim Extra Spaces from Text Columns")


        if st.button("Clean Data"):

            cleaned_df, cleaning_summary = clean_data(
                df,
                remove_duplicates=remove_duplicates,
                fill_missing=fill_missing,
                convert_datetime=convert_datetime,
                trim_spaces=trim_spaces
            )

            st.success("Data cleaning completed!")

            st.subheader("Cleaning Summary")

            if cleaning_summary:
                for item in cleaning_summary:
                    st.write(f"{item}")
            else:
                st.info("No cleaning operations were selected.")

            st.subheader("Cleaned Data Preview")
            st.dataframe(cleaned_df.head(10))

            st.download_button(
                label="Download Cleaned CSV",
                data=cleaned_df.to_csv(index=False),
                file_name="cleaned_data.csv",
                mime="text/csv"
            )


    except Exception as e:
        st.error(f"Error reading file: {e}")

