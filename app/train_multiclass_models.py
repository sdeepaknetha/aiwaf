import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

# ----------------------------------------
# PATHS
# ----------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODELS_DIR, exist_ok=True)

DATA_FILE = os.path.join(
    DATA_DIR,
    "all_attacks_multiclass_strong_noise.csv"
)

# ----------------------------------------
# LOAD DATA
# ----------------------------------------
data = pd.read_csv(DATA_FILE)

X = data["payload"].astype(str)
y = data["label"].astype(int)

# ----------------------------------------
# TRAIN–TEST SPLIT
# ----------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ----------------------------------------
# VECTORIZE (CRITICAL – SAME FOR ALL)
# ----------------------------------------
VECTOR_SIZE = 1500  # 🔒 DO NOT CHANGE unless retraining everything

vectorizer = CountVectorizer(
    max_features=VECTOR_SIZE,
    ngram_range=(1, 2),
    lowercase=True
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# SAVE VECTORIZER (VERY IMPORTANT)
joblib.dump(
    vectorizer,
    os.path.join(MODELS_DIR, "vectorizer.pkl")
)

print(f"\nDONE: Vectorizer trained with {X_train_vec.shape[1]} features")

# ----------------------------------------
# MODELS
# ----------------------------------------
models = {
    "logistic": LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
        n_jobs=-1
    ),

    "svm": SVC(
        kernel="linear",
        probability=True
    ),

    "random_forest": RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    ),

}

# ----------------------------------------
# 5-FOLD CROSS VALIDATION
# ----------------------------------------
print("\nRUNNING: 5-Fold Cross Validation\n")

skf = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

for name, model in models.items():
    fold_accuracies = []

    print(f"\nModel: {name.upper()}")

    for fold, (train_idx, val_idx) in enumerate(
        skf.split(X_train_vec, y_train), 1
    ):
        X_tr, X_val = X_train_vec[train_idx], X_train_vec[val_idx]
        y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

        model.fit(X_tr, y_tr)
        preds = model.predict(X_val)

        acc = accuracy_score(y_val, preds)
        fold_accuracies.append(acc)

        print(f"  Fold {fold} Accuracy: {acc:.4f}")

    avg_acc = sum(fold_accuracies) / len(fold_accuracies)
    print(f"DONE: Average Accuracy ({name.upper()}): {avg_acc:.4f}")

    # ------------------------------------
    # FINAL TRAINING ON FULL TRAIN SET
    # ------------------------------------
    model.fit(X_train_vec, y_train)

    joblib.dump(
        model,
        os.path.join(
            MODELS_DIR,
            f"{name}_multiclass.pkl"
        )
    )

# ----------------------------------------
# FINAL TEST SET EVALUATION (OPTIONAL)
# ----------------------------------------
print("\nINFO: Final Test Set Evaluation\n")

for name, model in models.items():
    preds = model.predict(X_test_vec)
    acc = accuracy_score(y_test, preds)
    print(f"{name.upper()} Test Accuracy: {acc:.4f}")

print("\nDONE: All models trained, validated, and saved successfully")
