import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/invoices_1000.csv")
OUTPUT_FILE = Path("data/invoices_1000_learnable.csv")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def assign_status(row):
    total = float(row["total"])
    balance = float(row["balance"])

    if total == 0:
        return "paid"

    balance_ratio = balance / total

    if balance_ratio > 0.75:
        return "overdue"
    elif balance_ratio > 0.25:
        return "pending"
    else:
        return "paid"


def make_dataset():
    df = pd.read_csv(INPUT_FILE)

    df["invoiceStatus"] = df.apply(assign_status, axis=1)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Created learnable dataset: {OUTPUT_FILE}")
    print(df["invoiceStatus"].value_counts())


if __name__ == "__main__":
    make_dataset()