import os
import joblib
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split

# -------------------------------
# PATHS
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUT_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------
# LOAD DATA
# -------------------------------
data = pd.read_csv(
    os.path.join(DATA_DIR, "all_attacks_multiclass_strong_noise.csv")
)

X = data["payload"]
y = data["label"]

# -------------------------------
# LOAD MODELS
# -------------------------------
models = {
    "Logistic Regression": joblib.load(os.path.join(MODELS_DIR, "logistic_multiclass.pkl")),
    "SVM": joblib.load(os.path.join(MODELS_DIR, "svm_multiclass.pkl")),
    "Random Forest": joblib.load(os.path.join(MODELS_DIR, "random_forest_multiclass.pkl"))
}

vectorizer = joblib.load(os.path.join(MODELS_DIR, "vectorizer.pkl"))

# -------------------------------
# TRAIN–TEST SPLIT
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

X_test_vec = vectorizer.transform(X_test)

# -------------------------------
# ACCURACY COMPUTATION
# -------------------------------
accuracies = {}

for name, model in models.items():
    preds = model.predict(X_test_vec)
    acc = accuracy_score(y_test, preds)
    accuracies[name] = acc
    print(f"{name} Accuracy: {acc:.4f}")

# -------------------------------
# ACCURACY BAR CHART
# -------------------------------
plt.figure(figsize=(8, 5))
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]  # blue, orange, green, red
plt.bar(accuracies.keys(), accuracies.values(), color=colors)
for i, v in enumerate(accuracies.values()):
    plt.text(i, v + 0.001, f"{v:.3f}", ha="center", fontsize=9)
plt.ylim(min(accuracies.values()) - 0.005, 1.0)
plt.ylabel("Accuracy")
plt.title("Model Accuracy Comparison")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "accuracy_comparison.png"))
plt.close()

# -------------------------------
# CONFUSION MATRICES
# -------------------------------
labels = [0, 1, 2, 3, 4]
label_names = ["Safe", "XSS", "SQL Injection", "Path Traversal", "Command Injection"]

for name, model in models.items():
    preds = model.predict(X_test_vec)
    cm = confusion_matrix(y_test, preds, labels=labels)

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=label_names
    )

    disp.plot(cmap="Blues", xticks_rotation=45)
    plt.title(f"Confusion Matrix - {name}")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"confusion_matrix_{name}.png"))
    plt.close()

print("DONE: Accuracy chart and confusion matrices generated")
