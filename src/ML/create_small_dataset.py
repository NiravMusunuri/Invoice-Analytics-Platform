import pandas as pd

INPUT_FILE = "/Users/niravmusunuri/Downloads/newest_invoices_data.csv"
OUTPUT_FILE = "data/invoices_100.csv"

df = pd.read_csv(INPUT_FILE)

small_df = df.sample(
    n=1000,
    random_state=42
)

small_df.to_csv(
    "data/invoices_1000.csv",
    index=False
)
print(f"Saved {len(small_df)} rows to {OUTPUT_FILE}")