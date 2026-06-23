from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path("src/ml/models/invoice_status_model.pkl")


def predict_invoice_status(
    service: str,
    total: float,
    discount: float,
    tax: float,
    balance: float
):
    if not MODEL_PATH.exists():
        return {
            "error": "Model not found. Train the model first."
        }

    model = joblib.load(MODEL_PATH)

    input_data = pd.DataFrame([
        {
            "service": service.lower(),
            "total": float(total),
            "discount": float(discount),
            "tax": float(tax),
            "balance": float(balance)
        }
    ])

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]
    classes = model.classes_

    confidence_scores = {
        str(classes[i]): round(float(probabilities[i]) * 100, 2)
        for i in range(len(classes))
    }

    return {
        "predicted_status": str(prediction),
        "confidence_scores": confidence_scores
    }