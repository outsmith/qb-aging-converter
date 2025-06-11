import streamlit as st
import pandas as pd

st.title("QuickBooks Aging Report → Bill Import Converter")

uploaded_file = st.file_uploader("Upload Aging Report CSV", type="csv")

if uploaded_file:
    try:
        # Manually define expected column names from QB aging export
        column_headers = [
            "Date",
            "Transaction type",
            "Num",
            "Vendor display name",
            "Vendor",
            "Due date",
            "Past due",
            "Amount",         # Ignored
            "Open balance"
        ]

        # Skip title row, assign proper headers
        df = pd.read_csv(uploaded_file, skiprows=1, names=column_headers)

        # Remove duplicate headers or subtotal lines
        df = df[df["Date"] != "Date"]
        df = df[pd.to_datetime(df["Date"], errors="coerce").notna()]
        df.reset_index(drop=True, inplace=True)

        # Map and reduce to needed columns
        output_df = df.rename(columns={
            "Vendor": "Vendor",
            "Date": "BillDate",
            "Due date": "DueDate",
            "Open balance": "Amount",
            "Num": "RefNumber"
        })[["Vendor", "BillDate", "DueDate", "Amount", "RefNumber"]]

        # Clean Amount
        output_df["Amount"] = output_df["Amount"].replace(",", "", regex=True).astype(float)

        # Convert and format dates
        output_df["BillDate"] = pd.to_datetime(output_df["BillDate"], errors="coerce").dt.strftime("%m/%d/%Y")
        output_df["DueDate"] = pd.to_datetime(output_df["DueDate"], errors="coerce").dt.strftime("%m/%d/%Y")

        # Ensure strings for export
        output_df["BillDate"] = output_df["BillDate"].astype(str)
        output_df["DueDate"] = output_df["DueDate"].astype(str)

        st.success("File cleaned and converted successfully!")
        st.dataframe(output_df)

        # Export CSV with UTF-8 BOM
        csv = output_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Download Converted CSV",
            data=csv,
            file_name="converted_for_qb_import.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error: {e}")
