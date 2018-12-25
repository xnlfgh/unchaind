import os
import json

path = os.path.expanduser("~/.unchaind.json")

if not os.path.exists(path):
    print(f"No config file found at {path}")
    raise SystemExit(1)

with open(path) as f:
    data = json.load(f)

mappers = data["mappers"]
notifiers = data["notifiers"]
