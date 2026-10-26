"""Self-check for the Instagram webhook integration: python3 tests/test_webhook.py"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MJS_TEST = os.path.join(HERE, "test_webhook.mjs")

r = subprocess.run(["node", "--test", MJS_TEST], capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout)
    print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)

print("webhook ok")
