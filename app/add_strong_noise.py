import os
import random
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_FILE = os.path.join(DATA_DIR, "all_attacks_multiclass.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "all_attacks_multiclass_strong_noise.csv")

data = pd.read_csv(INPUT_FILE)

# ------------- TEXT NOISE -------------
def text_noise(text):
    if random.random() < 0.5:
        text = text.replace("=", "").replace("'", "").replace('"', "")
    if random.random() < 0.3:
        text += " param" + str(random.randint(1, 999))
    return text

data["payload"] = data["payload"].astype(str).apply(text_noise)

# ------------- LABEL NOISE (KEY PART) -------------
# Only among attack classes (1,2,3)
attack_indices = data[data["label"].isin([1,2,3])].index.tolist()

num_to_flip = int(0.03 * len(attack_indices))  # 3% noise
flip_indices = random.sample(attack_indices, num_to_flip)

for idx in flip_indices:
    current = data.at[idx, "label"]
    data.at[idx, "label"] = random.choice([x for x in [1,2,3] if x != current])

# Shuffle
data = data.sample(frac=1, random_state=123).reset_index(drop=True)

data.to_csv(OUTPUT_FILE, index=False)

print("✅ Strong noisy dataset created")
print(data["label"].value_counts())
