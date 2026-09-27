import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "all_attacks_multiclass.csv")

# Load separate datasets
safe = pd.read_csv(os.path.join(DATA_DIR, "benign.csv"), header=None, names=["payload"])
xss = pd.read_csv(os.path.join(DATA_DIR, "xss.csv"), header=None, names=["payload"])
sqli = pd.read_csv(os.path.join(DATA_DIR, "sqli.csv"), header=None, names=["payload"])
path = pd.read_csv(os.path.join(DATA_DIR, "path_traversal.csv"), header=None, names=["payload"])
cmd = pd.read_csv(os.path.join(DATA_DIR, "command_injection.csv"), header=0, names=["payload"])

# Assign labels
safe["label"] = 0
xss["label"] = 1
sqli["label"] = 2
path["label"] = 3
cmd["label"] = 4

# Combine all
data = pd.concat([safe, xss, sqli, path, cmd], ignore_index=True)

# Shuffle for robustness (VERY IMPORTANT)
data = data.sample(frac=1, random_state=42).reset_index(drop=True)

# Save final dataset
# The training script expects 'all_attacks_multiclass_strong_noise.csv'
OUTPUT_FILE_NOISE = os.path.join(DATA_DIR, "all_attacks_multiclass_strong_noise.csv")
data.to_csv(OUTPUT_FILE_NOISE, index=False)
data.to_csv(OUTPUT_FILE, index=False)

print("DONE: Multi-class dataset created successfully")
print(data["label"].value_counts())
