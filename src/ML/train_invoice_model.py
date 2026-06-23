from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from src.database import get_connection
from sklearn.model_selection import train_test_split, cross_val_score

MODEL_DIR = Path("src/ml/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = "src/ml/models/invoice_status_model.pkl"


def fetch_invoice_data():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    
                    LOWER(service) AS service,
                    total,
                    discount,
                    tax,
                    balance,
                    LOWER(invoiceStatus) AS invoicestatus
                FROM chat.invoices
                WHERE invoiceStatus IS NOT NULL
                  AND country IS NOT NULL
                  AND service IS NOT NULL
                  AND total IS NOT NULL
                  AND discount IS NOT NULL
                  AND tax IS NOT NULL
                  AND balance IS NOT NULL;
                """
            )

            rows = cur.fetchall()

    return pd.DataFrame(rows)




def train_invoice_status_model():
    df = fetch_invoice_data()

    if df.empty:
        return {
            "error": "No invoice data found for training"
        }

    numeric_columns = [
        "total",
        "discount",
        "tax",
        "balance"
    ]

    for col in numeric_columns:
        df[col] = df[col].astype(float)

    df = df.dropna()

    if len(df) < 1000:
        return {
            "error": f"Expected at least 1000 invoices, found {len(df)}"
        }

    train_df, test_df = train_test_split(
        df,
        train_size=700,
        test_size=300,
        random_state=42,
        stratify=df["invoicestatus"]
    )

    test_df.to_csv(
        "data/test_invoices_300.csv",
        index=False
    )

    feature_columns = [

        "service",
        "total",
        "discount",
        "tax",
        "balance"
    ]



    X_train = train_df[feature_columns]
    y_train = train_df["invoicestatus"]

    categorical_features = [

        "service"
    ]

    numeric_features = [
        "total",
        "discount",
        "tax",
        "balance"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features
            ),
            (
                "numeric",
                "passthrough",
                numeric_features
            )
        ]
    )

    model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "classifier",
                RandomForestClassifier(

                        n_estimators=500,
                        max_depth=None,
                        min_samples_split=2,
                        min_samples_leaf=1,
                        class_weight="balanced",
                        random_state=42

                )
            )
        ]
    )

    cv_scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=5,
        scoring="accuracy"
    )

    print("Cross-validation scores:", cv_scores)
    print("Average CV accuracy:", round(cv_scores.mean() * 100, 2), "%")

    model.fit(X_train, y_train)

    joblib.dump(model, MODEL_PATH)

    return {
        "message": "Invoice status prediction model trained successfully",
        "model_path": str(MODEL_PATH),
        "total_rows": len(df),
        "rows_used_for_training": len(train_df),
        "rows_saved_for_testing": len(test_df),
        "test_file": "data/test_invoices_300.csv"
    }

if __name__ == "__main__":
    print("Training started...")
    result = train_invoice_status_model()
    print(result)