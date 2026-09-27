import os
import csv
import requests
import random
import pandas as pd
from datetime import datetime
from flask import Flask, request, render_template, jsonify, redirect, url_for
import joblib

# ===============================
# PATHS
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(LOGS_DIR, exist_ok=True)

# ===============================
# LOAD VECTOR & MODELS
# ===============================
print("INFO: Loading AI models and vectorizer (this may take a moment)...")
vectorizer = joblib.load(os.path.join(MODELS_DIR, "vectorizer.pkl"))

logistic_model = joblib.load(os.path.join(MODELS_DIR, "logistic_multiclass.pkl"))
print("DONE: Logistic Regression loaded.")
svm_model = joblib.load(os.path.join(MODELS_DIR, "svm_multiclass.pkl"))
print("DONE: SVM loaded.")
rf_model = joblib.load(os.path.join(MODELS_DIR, "random_forest_multiclass.pkl"))
print("DONE: Random Forest loaded.")
# ann_model = joblib.load(os.path.join(MODELS_DIR, "ann_multiclass.pkl"))
# print("DONE: ANN loaded.")

MODELS = {
    "Logistic Regression": logistic_model,
    "SVM": svm_model,
    "Random Forest": rf_model
    # "ANN": ann_model
}

LABEL_MAP = {
    0: "SAFE",
    1: "XSS",
    2: "SQL Injection",
    3: "Path Traversal",
    4: "Command Injection"
}

# ===============================
# LOAD ATTACK DATA FOR RANDOM TESTING
# ===============================
print("INFO: Loading testing datasets...")
ATTACK_DATA = {
    "sqli": pd.read_csv(os.path.join(DATA_DIR, "sqli.csv"))["payload"].tolist(),
    "xss": pd.read_csv(os.path.join(DATA_DIR, "xss.csv"))["payload"].tolist(),
    "path_traversal": pd.read_csv(os.path.join(DATA_DIR, "path_traversal.csv"))["payload"].tolist(),
    "command_injection": pd.read_csv(os.path.join(DATA_DIR, "command_injection.csv"))["payload"].tolist(),
    "safe": pd.read_csv(os.path.join(DATA_DIR, "benign.csv"))["payload"].tolist()
}
print("DONE: Datasets loaded.")

# ===============================
# FLASK APP
# ===============================
app = Flask(__name__, template_folder="templates", static_folder="static")

LOG_FILE = os.path.join(LOGS_DIR, "waf_logs.csv")

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "payload", "status", "attack", "confidence"])

def get_payload_count():
    try:
        if not os.path.exists(LOG_FILE):
            return 0
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return sum(1 for line in f) - 1
    except:
        return 0

# ===============================
# CLASSIFICATION
# ===============================
def classify_payload(payload):
    X = vectorizer.transform([payload])

    model_results = []
    final_attack = "SAFE"
    final_conf = 0.0
    final_label = 0

    for name, model in MODELS.items():
        label = int(model.predict(X)[0])
        confidence = float(max(model.predict_proba(X)[0]))

        model_results.append({
            "model": name,
            "label": label,
            "attack": LABEL_MAP.get(label, "UNKNOWN"),
            "confidence": confidence
        })

        if label != 0 and confidence > final_conf:
            final_conf = confidence
            final_label = label
            final_attack = LABEL_MAP.get(label, "UNKNOWN")
        
        if final_label == 0 and confidence > final_conf:
             final_conf = confidence

    status = "BLOCKED" if final_label != 0 else "SAFE"
    return status, final_attack, final_conf, model_results

# ===============================
# ROUTES
# ===============================
@app.route("/", methods=["GET", "POST"])
def index():
    payload_count = get_payload_count()
    if request.method == "POST":
        payload = request.form.get("payload", "").strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        status, attack, confidence, model_results = classify_payload(payload)

        # LOG
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                [timestamp, payload, status, attack, f"{confidence:.4f}"]
            )

        # Current Analyzed Payload Index
        current_index = get_payload_count()

        return render_template(
            "index.html",
            result={
                "status": status,
                "attack": attack,
                "confidence": round(confidence, 2),
                "payload": payload,
                "index": current_index
            },
            model_results=model_results,
            timestamp=timestamp,
            payload_count=current_index
        )

    return render_template("index.html", payload_count=payload_count)

@app.route("/get_random_payload/<attack_type>")
def random_payload(attack_type):
    if attack_type in ATTACK_DATA:
        payload = random.choice(ATTACK_DATA[attack_type])
        return jsonify({"payload": str(payload)})
    return jsonify({"error": "Invalid attack type"}), 400

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check Username
        status_u, attack_u, conf_u, _ = classify_payload(username)
        # Check Password
        status_p, attack_p, conf_p, _ = classify_payload(password)

        if status_u == "BLOCKED" or status_p == "BLOCKED":
            # LOG Attack
            culprit = username if status_u == "BLOCKED" else password
            attack = attack_u if status_u == "BLOCKED" else attack_p
            conf = conf_u if status_u == "BLOCKED" else conf_p
            
            with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([timestamp, culprit, "BLOCKED", attack, f"{conf:.4f}"])
            
            return render_template("login.html", message=f"SECURITY ALERT: {attack} detected! Login blocked.")

        # Simulate successful login if no attack detected
        return redirect(url_for("welcome", username=username))

    return render_template("login.html")

@app.route("/welcome")
def welcome():
    username = request.args.get("username", "User")
    return render_template("welcome.html", username=username)

import subprocess

# ===============================
# ADAPTIVE LEARNING ENDPOINTS
# ===============================

@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.json
    payload = data.get("payload")
    label = int(data.get("label"))
    
    csv_map = {
        0: "benign.csv",
        1: "xss.csv",
        2: "sqli.csv",
        3: "path_traversal.csv",
        4: "command_injection.csv"
    }
    
    filename = csv_map.get(label)
    if not filename:
        return jsonify({"error": "Invalid label"}), 400
        
    filepath = os.path.join(DATA_DIR, filename)
    
    # Append to CSV
    try:
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([payload])
        return jsonify({"message": f"Added to {filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/retrain", methods=["POST"])
def retrain():
    try:
        # Get python path from current venv if possible
        python_exe = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")
        if not os.path.exists(python_exe):
             python_exe = "python" # Fallback

        print("INFO: Starting background retraining...")
        
        # 1. Prepare Dataset
        subprocess.run([python_exe, os.path.join(BASE_DIR, "app", "prepare_dataset.py")], check=True)
        
        # 2. Train Models
        subprocess.run([python_exe, os.path.join(BASE_DIR, "app", "train_multiclass_models.py")], check=True)
        
        # 3. Reload Models in memory
        reload_models()
        
        return jsonify({"message": "Retraining complete. Models reloaded."})
    except Exception as e:
        print(f"ERROR: Retraining failed: {e}")
        return jsonify({"error": str(e)}), 500

def reload_models():
    global vectorizer, logistic_model, svm_model, rf_model, ann_model, MODELS
    print("INFO: Reloading models...")
    vectorizer = joblib.load(os.path.join(MODELS_DIR, "vectorizer.pkl"))
    logistic_model = joblib.load(os.path.join(MODELS_DIR, "logistic_multiclass.pkl"))
    svm_model = joblib.load(os.path.join(MODELS_DIR, "svm_multiclass.pkl"))
    rf_model = joblib.load(os.path.join(MODELS_DIR, "random_forest_multiclass.pkl"))
    # ann_model = joblib.load(os.path.join(MODELS_DIR, "ann_multiclass.pkl"))
    
    MODELS = {
        "Logistic Regression": logistic_model,
        "SVM": svm_model,
        "Random Forest": rf_model
        # "ANN": ann_model
    }
    print("DONE: Models reloaded.")

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    print("INFO: Firewall Starting...")
    app.run(debug=True)
