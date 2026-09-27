import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "benign.csv")

payloads = []

pages = ["home", "login", "profile", "search", "products", "contact"]
params = ["id", "page", "user", "q", "category"]

for i in range(5000):
    payloads.append(f"{pages[i % 6]}?{params[i % 5]}={i}")

pd.DataFrame({"payload": payloads}).to_csv(OUTPUT_PATH, index=False)

print("5000 BENIGN payloads generated in data/benign.csv")
