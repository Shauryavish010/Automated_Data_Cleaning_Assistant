import pandas as pd


def clean_data(
    df,
    remove_duplicates=False,
    fill_missing=False,
    convert_datetime=False,
    trim_spaces=False
):

    cleaned_df = df.copy()

    summary = []

    # Remove duplicates
    if remove_duplicates:
        before = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        removed = before - len(cleaned_df)

        summary.append(f"Removed {removed} duplicate rows.")

    # Fill missing values
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

    # Convert datetime columns
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

    # Trim spaces
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