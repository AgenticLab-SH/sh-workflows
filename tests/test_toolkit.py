"""Deterministic, offline tests on synthetic fixtures."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from kit_utils import (csv_audit, validate_json, compare_json, classification_metrics,
                       restricted_path, InputError)


class DataChecksTest(unittest.TestCase):
    def setUp(self):
        self.examples = ROOT/'examples'

    def test_audit_detects_duplicate_and_missing(self):
        r=csv_audit(self.examples/'applications.csv', ['id','date','people'],['id'])
        self.assertEqual(r['row_count'],4)
        self.assertEqual(r['missing_values_by_column']['date'],1)
        self.assertEqual(r['duplicate_key_rows'],1)
        self.assertFalse(r['passed_requested_checks'])

    def test_audit_valid_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'a.csv'
            p.write_text('id,date\na,2026-01-01\nb,2026-01-02\n',encoding='utf8')
            r=csv_audit(p,['id','date'],['id'])
            self.assertTrue(r['passed_requested_checks'])

    def test_required_missing_column(self):
        r=csv_audit(self.examples/'applications.csv',['unknown'])
        self.assertEqual(r['required_columns_missing'],['unknown'])

    def test_json_valid_and_missing(self):
        p=self.examples/'config.json'
        self.assertTrue(validate_json(p,['version','name'])['valid'])
        self.assertEqual(validate_json(p,['unknown'])['missing_required_keys'],['unknown'])

    def test_compare_does_not_echo_value(self):
        r=compare_json(self.examples/'before.json',self.examples/'after.json')
        self.assertFalse(r['equal'])
        self.assertGreaterEqual(len(r['changed_paths_sample']),2)
        self.assertNotIn('basic',json.dumps(r))

    def test_metrics(self):
        r=classification_metrics(self.examples/'classification.csv','actual','predicted','yes')
        self.assertEqual([r[k] for k in ('tp','fp','fn','tn')],[2,1,1,1])
        self.assertAlmostEqual(r['precision'],2/3,places=5)
        self.assertAlmostEqual(r['recall'],2/3,places=5)

    def test_zero_denominator_is_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'z.csv';p.write_text('a,b\nno,no\n',encoding='utf8')
            r=classification_metrics(p,'a','b','yes')
            self.assertIsNone(r['precision'])
            self.assertIsNone(r['recall'])

    def test_root_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'root';root.mkdir()
            outside=Path(tmp)/'outside.csv';outside.write_text('a\n1\n',encoding='utf8')
            with self.assertRaises(InputError): restricted_path(outside,root,'.csv')
            link=root/'escape.csv';link.symlink_to(outside)
            with self.assertRaises(InputError): restricted_path(link,root,'.csv')


class MCPSmokeTest(unittest.TestCase):
    def test_protocol_tools_and_denied_path(self):
        reqs=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26'}},
              {'jsonrpc':'2.0','id':2,'method':'tools/list'},
              {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{
                  'name':'audit_csv','arguments':{'path':str(ROOT/'examples'/'applications.csv'),
                  'required_columns':['id','date'],'unique_columns':['id']}}},
              {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{
                  'name':'validate_json','arguments':{'path':'/etc/passwd'}}}]
        env={**os.environ,'MCP_ALLOWED_ROOT':str(ROOT)}
        p=subprocess.run([sys.executable,str(ROOT/'tools'/'mcp_stdio_server.py')],
            input=''.join(json.dumps(r)+'\n' for r in reqs),text=True,capture_output=True,timeout=10,env=env)
        self.assertEqual(p.returncode,0,p.stderr)
        lines=[json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual(len(lines),4)
        self.assertEqual(lines[0]['result']['serverInfo']['name'],'ai-hackathon-prep-kit')
        self.assertEqual(len(lines[1]['result']['tools']),6)
        self.assertIn('row_count',lines[2]['result']['content'][0]['text'])
        self.assertTrue(lines[3]['result']['isError'])

    def test_skills_are_no_placeholder(self):
        for f in (ROOT/'.agents'/'skills').glob('*/SKILL.md'):
            t=f.read_text(encoding='utf8')
            self.assertTrue(t.startswith('---\nname:'))
            self.assertGreater(len(t.splitlines()),15)
            self.assertNotIn('TODO:',t)

if __name__=='__main__': unittest.main()

