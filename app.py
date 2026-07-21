import streamlit as st
import pandas as pd
import plotly.express as px
from utils.profiler import get_dataset_summary
from utils.profiler import get_column_statistics
from utils.cleaner import clean_data
from utils.dashboard import missing_value_summary
from utils.file_loader import load_csv
from utils.classifier import classify_columns
from utils.recommendation import generate_recommendations

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

        #classification_df = classify_columns(df)
        recommendation_df = generate_recommendations(df, classification_df)
        st.subheader("Cleaning Recommendations")

        st.dataframe(
            recommendation_df,
            use_container_width=True,
            hide_index=True
        )

        #Statistics
        summary = get_dataset_summary(df)

        rows = summary["rows"]
        columns = summary["columns"]
        missing_values = summary["missing_values"]
        duplicate_rows = summary["duplicate_rows"]

        column_stats = get_column_statistics(df)

        st.subheader("Column Statistics")
        st.dataframe(
            column_stats,
            use_container_width = True,
            hide_index= True
        )

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

