import matplotlib

matplotlib.use("Agg")

import uuid
from pathlib import Path
import matplotlib.pyplot as plt

GRAPH_DIR = Path("src/data/graphs")
GRAPH_DIR.mkdir(parents=True, exist_ok=True)


def create_graph(x_values, y_values, graph_type, title):
    file_name = f"graph_{uuid.uuid4()}.png"
    file_path = GRAPH_DIR / file_name

    plt.figure(figsize=(8, 5))

    if graph_type == "bar":
        plt.bar(x_values, y_values)

    elif graph_type == "line":
        plt.plot(x_values, y_values, marker="o")

    elif graph_type == "pie":
        plt.pie(y_values, labels=x_values, autopct="%1.1f%%")

    else:
        raise ValueError(f"Unsupported graph type: {graph_type}")

    plt.title(title)
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

    return {
        "text": "Graph created successfully.",
        "file_url": f"http://127.0.0.1:8000/static/graphs/{file_name}"
    }