import streamlit as st
import pandas as pd

st.title("QuickBooks Aging Report → Bill Import Converter")

uploaded_file = st.file_uploader("Upload Aging Report CSV", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = {
            "Vendor": "Vendor",
            "Date": "BillDate",
            "Due date": "DueDate",
            "Open balance": "Amount",
            "Num": "RefNumber"
        }

        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            st.error(f"Missing columns: {', '.join(missing)}")
        else:
            # Rename and select only the needed columns
            output_df = df.rename(columns=required_columns)[list(required_columns.values())]
            output_df = output_df.loc[:, ~output_df.columns.duplicated()]

            # Clean Amount
            output_df["Amount"] = output_df["Amount"].replace(",", "", regex=True).astype(float)

            # Parse and format BillDate and DueDate as MM/DD/YYYY (force string)
            output_df["BillDate"] = pd.to_datetime(output_df["BillDate"], errors="coerce").dt.strftime("%m/%d/%Y")
            output_df["DueDate"] = pd.to_datetime(output_df["DueDate"], errors="coerce").dt.strftime("%m/%d/%Y")

            # Ensure these columns are type 'str' just in case
            output_df["BillDate"] = output_df["BillDate"].astype(str)
            output_df["DueDate"] = output_df["DueDate"].astype(str)

            st.success("File converted successfully!")
            st.dataframe(output_df)

            # Export CSV with BOM to help Excel and QuickBooks parse dates
            csv = output_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 Download Converted CSV",
                data=csv,
                file_name="converted_for_qb_import.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Error: {e}")
