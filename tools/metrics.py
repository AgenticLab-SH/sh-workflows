#!/usr/bin/env python3
"""Binary one-vs-rest classification metrics with explicit positive label."""
import argparse, json, sys
from kit_utils import classification_metrics, InputError
p=argparse.ArgumentParser(description=__doc__);p.add_argument('file');p.add_argument('--actual',required=True);p.add_argument('--pred',required=True);p.add_argument('--positive',required=True);a=p.parse_args()
try:
    print(json.dumps(classification_metrics(a.file,a.actual,a.pred,a.positive),indent=2,ensure_ascii=False))
except (InputError,OSError) as e:
    print(json.dumps({'error':str(e)},ensure_ascii=False));sys.exit(2)

