"""A small utility to push keys, previously save in plain files to the key server"""

import sys
import re
import requests
import json
import http

REGEX = re.compile("key= ?([a-z0-9A-Z]+)")
SAVE_KEY_URL = "http://localhost:8000/keys/save"


def main():
    """Open text file, find lines matching regex, report each"""
    fname = sys.argv[1]

    with open( fname, 'rt') as f_in:
        for i, line in enumerate(f_in):
            match = re.search( REGEX, line )
            if match:
                key = match.group(1)
                resp = requests.post( SAVE_KEY_URL, json.dumps( {"key": key} ) )
                print(f"{i:4d} {key} {resp.status_code}" )

if __name__ == "__main__":
    main()

# %%
