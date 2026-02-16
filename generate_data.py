import pandas as pd

# Income Data
data_income = {
    "cif_id_mask": ["789012", "123456", "345678"],
    "income_cust": [22000, 15000, 30000],
    "income_kyc": [25000, 15000, 28000]
}
df_income = pd.DataFrame(data_income)
df_income.to_excel("data/income_hackathon.xlsx", index=False)

# CC Master Data
data_cc = {
    "cif_id_mask": ["789012", "123456", "345678"],
    "cc_account_open_date": ["2018-01-01", "2019-05-01", "2020-03-15"],
    "embossed_bin_desc": ["Visa Infinite", "Mastercard Titanium", "Visa Signature"],
    "cc_credit_limit": [50000, 10000, 75000],
    "cc_account_closed_date": [None, None, None]
}
df_cc = pd.DataFrame(data_cc)
df_cc.to_excel("data/cc_master_hackathon.xlsx", index=False)

# Customer Data (Adding to previous script logic just to be safe and complete)
data_cust = {
    "cif_id_mask": ["789012", "123456", "345678"],
    "residence_since": ["2010-01-01", "2015-05-20", "2012-08-10"],
    "relationship_start_date": ["2010-02-01", "2015-06-01", "2012-09-01"],
    "employment_status": ["Employed", "Self-Employed", "Employed"],
    "gender": ["Male", "Female", "Male"],
    "marital_status": ["Married", "Single", "Married"],
    "dependents": [2, 0, 3],
    "nationality": ["USA", "UK", "India"]
}
df_cust = pd.DataFrame(data_cust)
df_cust.to_excel("data/customer_master_hackathon.xlsx", index=False)

print("Generated all dummy Excel files.")
