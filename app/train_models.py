import os
import pandas as pd
import joblib

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from scipy.sparse import vstack

# ----------------------------------------
# BASE DIRECTORIES
# ----------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODELS_DIR, exist_ok=True)

# ----------------------------------------
# LOAD DATASETS
# ----------------------------------------
sqli_df = pd.read_csv(os.path.join(DATA_DIR, "sqli.csv"))
xss_df = pd.read_csv(os.path.join(DATA_DIR, "xss.csv"))
path_df = pd.read_csv(os.path.join(DATA_DIR, "path_traversal.csv"))

sqli_payloads = sqli_df["payload"]
xss_payloads = xss_df["payload"]
path_payloads = path_df["payload"]

# ----------------------------------------
# CREATE BENIGN DATA (IMPORTANT FIX)
# ----------------------------------------
benign_payloads = pd.concat([
    xss_payloads.sample(min(200, len(xss_payloads)), random_state=42),
    path_payloads.sample(min(200, len(path_payloads)), random_state=42)
])

# ----------------------------------------
# FIT VECTORIZER ON ALL DATA
# ----------------------------------------
all_payloads = pd.concat([
    sqli_payloads, xss_payloads, path_payloads, benign_payloads
])

vectorizer = CountVectorizer(ngram_range=(1, 2), max_features=5000)
vectorizer.fit(all_payloads)

joblib.dump(vectorizer, os.path.join(MODELS_DIR, "vectorizer.pkl"))

# ----------------------------------------
# TRAIN FUNCTION (FIXED)
# ----------------------------------------
def train_and_save_model(attack_payloads, benign_payloads, model_name):
    X_attack = vectorizer.transform(attack_payloads)
    X_benign = vectorizer.transform(benign_payloads)

    # ✅ CORRECT way to combine sparse matrices
    X = vstack([X_attack, X_benign])
    y = [1] * X_attack.shape[0] + [0] * X_benign.shape[0]

    model = LogisticRegression(
    max_iter=1000,
    solver="liblinear",
    class_weight="balanced"
)

    model.fit(X, y)

    joblib.dump(model, os.path.join(MODELS_DIR, model_name))
    print(f"✅ {model_name} trained successfully")

# ----------------------------------------
# TRAIN ALL MODELS
# ----------------------------------------
train_and_save_model(sqli_payloads, benign_payloads, "sqli_model.pkl")
train_and_save_model(xss_payloads, benign_payloads, "xss_model.pkl")
train_and_save_model(path_payloads, benign_payloads, "path_model.pkl")

print("🎉 All models trained without errors")
