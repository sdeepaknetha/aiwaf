import pandas as pd
import random
import string
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(BASE_DIR, "benign.csv")

def rand_word(n=6):
    return ''.join(random.choices(string.ascii_lowercase, k=n))

safe_payloads = set()

# login-like inputs
for i in range(1500):
    safe_payloads.add(f"username={rand_word()}&password={rand_word(8)}")

# search queries
for i in range(1500):
    safe_payloads.add(f"search={rand_word()}")

# profile / normal params
for i in range(1000):
    safe_payloads.add(f"id={random.randint(1,10000)}")

# emails & comments
for i in range(1000):
    safe_payloads.add(f"email={rand_word()}@gmail.com")

# simple text inputs
for i in range(1000):
    safe_payloads.add(f"comment=nice product {rand_word()}")

df = pd.DataFrame({"payload": list(safe_payloads)})
df.to_csv(OUTPUT, index=False)

print(f"✅ {len(df)} UNIQUE SAFE payloads generated")
