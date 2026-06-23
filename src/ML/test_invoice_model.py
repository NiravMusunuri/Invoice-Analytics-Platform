import joblib
import pandas as pd

from sklearn.metrics import accuracy_score, precision_score, classification_report, confusion_matrix

MODEL_PATH = "src/ml/models/invoice_status_model.pkl"
TEST_FILE = "data/test_invoices_300.csv"


def test_invoice_model():
    model = joblib.load(MODEL_PATH)

    df = pd.read_csv(TEST_FILE)

    df = df.replace([float("inf"), -float("inf")], 0)
    df = df.fillna(0)

    X_test = df[
    [

        "service",
        "total",
        "discount",
        "tax",
        "balance",

    ]
]

    y_test = df["invoicestatus"]

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    precision = precision_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    print("Accuracy:", round(accuracy * 100, 2), "%")
    print("Precision:", round(precision * 100, 2), "%")

    print("\nClassification Report:")
    print(classification_report(y_test, predictions, zero_division=0))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))
    print(df["invoicestatus"].value_counts(normalize=True))
    print(pd.crosstab(df["service"], df["invoicestatus"], normalize="index"))

    results = df.copy()
    results["predicted_status"] = predictions
    results["correct"] = results["invoicestatus"] == results["predicted_status"]

    results.to_csv("data/prediction_results.csv", index=False)

    print("\nSaved prediction results to data/prediction_results.csv")


if __name__ == "__main__":
    test_invoice_model()


