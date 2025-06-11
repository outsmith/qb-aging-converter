import streamlit as st
import pandas as pd

st.title("QuickBooks Aging Report → Bill Import Converter")

uploaded_file = st.file_uploader("Upload Aging Report CSV", type="csv")

if uploaded_file:
    try:
        # Load CSV, skipping the title and blank rows, with fixed column headers
        df = pd.read_csv(uploaded_file, skiprows=2, names=[
            "Date",
            "Transaction type",
            "Num",
            "Vendor display name",
            "Vendor",
            "Due date",
            "Past due",
            "Amount",        # <- this one gets dropped
            "Open balance"
        ])

        # Remove header rows or junk
        df = df[df["Date"] != "Date"]
        df = df[pd.to_datetime(df["Date"], errors="coerce").notna()]
        df.reset_index(drop=True, inplace=True)

        # Drop unneeded "Amount" column (keeps "Open balance" only)
        df = df.drop(columns=["Amount"])

        # Rename columns and select output
        output_df = df.rename(columns={
            "Date": "BillDate",
            "Due date": "DueDate",
            "Open balance": "Amount",
            "Num": "RefNumber"
        })[["Vendor", "BillDate", "DueDate", "Amount", "RefNumber"]]

        # Clean and format
        output_df["Amount"] = output_df["Amount"].replace(",", "", regex=True).astype(float)
        output_df["BillDate"] = pd.to_datetime(output_df["BillDate"], errors="coerce").dt.strftime("%m/%d/%Y")
        output_df["DueDate"] = pd.to_datetime(output_df["DueDate"], errors="coerce").dt.strftime("%m/%d/%Y")

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
