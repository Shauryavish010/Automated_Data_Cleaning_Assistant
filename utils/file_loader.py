import pandas as pd

def load_csv(file):

    encodings = [
        "utf-8",
        "utf-8-sig",
        "latin1",
        "ISO-8859-1",
        "cp1252"
    ]
    separators = [None, ",", ";", "\t"]

    for encoding in encodings:
        for sep in separators:
            try:
                file.seek(0)

                return pd.read_csv(
                    file,
                    encoding=encoding,
                    sep=sep,
                    engine="python",
                    on_bad_lines="skip"
                )

            except Exception:
                continue

    raise ValueError("Unable to read the uploaded CSV.")

    