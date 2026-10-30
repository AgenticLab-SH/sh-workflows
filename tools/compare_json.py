#!/usr/bin/env python3
"""Compare JSON structure and values without printing sensitive field values."""
import argparse, json, sys
from kit_utils import compare_json, InputError
p=argparse.ArgumentParser(description=__doc__);p.add_argument('left');p.add_argument('right');a=p.parse_args()
try:
    r=compare_json(a.left,a.right)
    print(json.dumps(r,indent=2,ensure_ascii=False));sys.exit(0 if r['equal'] else 1)
except (InputError,OSError) as e:
    print(json.dumps({'error':str(e)},ensure_ascii=False));sys.exit(2)

