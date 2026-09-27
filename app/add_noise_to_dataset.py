import os
import random
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILE = os.path.join(DATA_DIR, "all_attacks_multiclass.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "all_attacks_multiclass_noisy.csv")

data = pd.read_csv(INPUT_FILE)

def add_noise(text):
    noise_tokens = [
        "test", "123", "abc", "hello", "user", "data",
        "xyz", "sample", "value"
    ]

    # randomly add junk words
    if random.random() < 0.4:
        text = text + " " + random.choice(noise_tokens)

    # randomly remove symbols
    if random.random() < 0.3:
        text = text.replace("=", "").replace("'", "").replace('"', "")

    return text

data["payload"] = data["payload"].astype(str).apply(add_noise)

# Shuffle again
data = data.sample(frac=1, random_state=99).reset_index(drop=True)

data.to_csv(OUTPUT_FILE, index=False)

print("✅ Noisy dataset created successfully")
