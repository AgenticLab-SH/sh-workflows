#!/usr/bin/env python3
"""Validate top-level JSON object and required keys without echoing values."""
import argparse, json, sys
from kit_utils import validate_json, InputError
p=argparse.ArgumentParser(description=__doc__);p.add_argument('file');p.add_argument('--required',default='');a=p.parse_args()
try:
    r=validate_json(a.file,[x.strip() for x in a.required.split(',') if x.strip()])
    print(json.dumps(r,indent=2,ensure_ascii=False));sys.exit(0 if r['valid'] else 1)
except (InputError,OSError) as e:
    print(json.dumps({'error':str(e)},ensure_ascii=False));sys.exit(2)

