#!/usr/bin/env python3
"""CSV schema/quality summary without showing row values or writing files."""
import argparse, json, sys
from kit_utils import csv_audit, InputError

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('file');p.add_argument('--required',default='');p.add_argument('--unique',default='')
a=p.parse_args()
try:
    res=csv_audit(a.file,[x.strip() for x in a.required.split(',') if x.strip()],
                  [x.strip() for x in a.unique.split(',') if x.strip()])
    print(json.dumps(res,indent=2,ensure_ascii=False));sys.exit(0 if res['passed_requested_checks'] else 1)
except (InputError,OSError) as e:
    print(json.dumps({'error':str(e)},ensure_ascii=False));sys.exit(2)

