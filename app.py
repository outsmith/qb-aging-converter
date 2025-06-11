import streamlit as st
import pandas as pd

st.title("QuickBooks Aging Report → Bill Import Converter")

uploaded_file = st.file_uploader("Upload Aging Report CSV", type="csv")

if uploaded_file:
    try:
        # Define expected column names from QB aging export
        column_headers = [
            "Date",
            "Transaction type",
            "Num",
            "Vendor display name",
            "Vendor",
            "Due date",
            "Past due",
            "Amount",         # <- ignored now
            "Open balance"
        ]

        # Load CSV and skip only the title row
        df = pd.read_csv(uploaded_file, skiprows=1, names=column_headers)

        # Remove any repeated headers or summary rows
        df = df[df["Date"] != "Date"]
        df = df[pd.to_datetime(df["Date"], errors="coerce").notna()]
        df.reset_index(drop=True, inplace=True)

        # Map to QuickBooks import format — ignore "Past due" and "Amount"
        output_df = df.rename(columns={
            "Vendor": "Vendor",
            "Date": "BillDate",
            "Due date": "DueDate",
            "Open balance": "Amount",
            "Num": "RefNumber"
        })[["Vendor", "BillDate", "DueDate", "Amount", "RefNumber"]]

        # Clean up Amount
        output_df["Amount"] = output_df["Amount"].replace(",", "", regex=True).astype(float)

        # Format dates as MM/DD/YYYY
        output_df["BillDate"] = pd.to_datetime(output_df["BillDate"], errors="coerce").dt.strftime("%m/%d/%Y")
        output_df["DueDate"] = pd.to_datetime(output_df["DueDate"], errors="coerce").dt.strftime("%m/%d/%Y")

        # Ensure these are strings for clean CSV export
        output_df["BillDate"] = output_df["BillDate"].astype(str)
        output_df["DueDate"] = output_df["DueDate"].astype(str)

        st.success("File cleaned and converted successfully!")
        st.dataframe(output_df)

        csv = output_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Download Converted CSV",
            data=csv,
            file_name="converted_for_qb_import.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error: {e}")
