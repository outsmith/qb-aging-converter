import streamlit as st
import pandas as pd

st.title("QuickBooks Aging Report → Bill & Credit Split Converter")

uploaded_file = st.file_uploader("Upload Aging Report CSV", type="csv")

if uploaded_file:
    try:
        # Load CSV with two extra columns for selection and notes
        df = pd.read_csv(uploaded_file, skiprows=2, names=[
            "Date",
            "Transaction type",
            "Num",
            "Vendor display name",
            "Vendor",
            "Due date",
            "Past due",
            "Amount",          # ignored
            "Open balance",
            "Select",          # x = include
            "Notes"            # ignored
        ])

        # Clean header rows and keep only real transactions
        df = df[df["Date"] != "Date"]
        df = df[pd.to_datetime(df["Date"], errors="coerce").notna()]
        df.reset_index(drop=True, inplace=True)

        # Filter to only selected rows
        df = df[df["Select"].str.lower().fillna("") == "x"]

        # Drop unneeded columns
        df = df.drop(columns=["Amount", "Select", "Notes", "Transaction type", "Vendor display name", "Past due"])

        # Convert open balance to numeric
        df["Open balance"] = df["Open balance"].replace(",", "", regex=True).astype(float)

        # Separate bills and vendor credits
        bills_df = df[df["Open balance"] > 0].copy()
        credits_df = df[df["Open balance"] < 0].copy()

        # Rename columns for both
        def format_df(d):
            d = d.rename(columns={
                "Date": "BillDate",
                "Due date": "DueDate",
                "Open balance": "Amount",
                "Num": "RefNumber"
            })[["Vendor", "BillDate", "DueDate", "Amount", "RefNumber"]]
            d["BillDate"] = pd.to_datetime(d["BillDate"], errors="coerce").dt.strftime("%m/%d/%Y")
            d["DueDate"] = pd.to_datetime(d["DueDate"], errors="coerce").dt.strftime("%m/%d/%Y")
            return d

        bills_df = format_df(bills_df)
        credits_df = format_df(credits_df)

        st.success("Selected bills and credits processed!")

        if not bills_df.empty:
            st.subheader("🧾 Bills to Import")
            st.dataframe(bills_df)
            csv_bills = bills_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 Download Bills CSV", data=csv_bills, file_name="converted_for_qb_import.csv", mime="text/csv")

        if not credits_df.empty:
            st.subheader("📘 Vendor Credits to Import")
            st.dataframe(credits_df)
            csv_credits = credits_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 Download Vendor Credits CSV", data=csv_credits, file_name="vendor_credits_for_qb.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error: {e}")
