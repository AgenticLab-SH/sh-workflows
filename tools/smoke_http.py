#!/usr/bin/env python3
"""Make one HTTP GET to loopback only; no browser automation, no external URL."""
import argparse, json, sys, http.client
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,required=True);p.add_argument('--path',default='/');p.add_argument('--timeout',type=float,default=3.0);a=p.parse_args()
if not (1<=a.port<=65535) or not a.path.startswith('/') or any(x in a.path for x in ('\r','\n','#')) or not (0<a.timeout<=10):
    print(json.dumps({'error':'invalid port, path or timeout'}));sys.exit(2)
conn=http.client.HTTPConnection('127.0.0.1',a.port,timeout=a.timeout)
try:
    conn.request('GET',a.path)
    response=conn.getresponse()
    response.read(4096)
    result={'status':response.status,'reason':response.reason,'local_only':True}
    print(json.dumps(result));sys.exit(0 if 200<=response.status<400 else 1)
except (OSError,http.client.HTTPException) as exc:
    print(json.dumps({'error':type(exc).__name__,'local_only':True}));sys.exit(2)
finally:
    conn.close()

