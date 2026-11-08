#!/usr/bin/env python3
import json,subprocess,sys,runpy,contextlib,io
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source={'task_id':'rpc-fixture','document_revision':'r1','repository_revision':'fixture-commit','draft':'Synthetic fixture.','register':{'field':'fixture','tenor':'peer','mode':'Markdown','genre':'feature-description','dial':'Compressed','template':'Fixture template','task_type':'audit','output_contract':{}},'peer_findings':['must be stripped']}
messages=[
 {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'fixture','version':'1'}}},
 {'jsonrpc':'2.0','method':'notifications/initialized'},
 {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
 {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'prepare_blind','arguments':{'source':source}}},
 {'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'prepare_cross','arguments':{}}},
 {'jsonrpc':'2.0','id':5,'method':'tools/call','params':{'name':'nonexistent','arguments':{}}},
]
with contextlib.redirect_stdout(io.StringIO()):fixtures=runpy.run_path(str(root/'scripts/check_review_packets.py'))
messages += [
 {'jsonrpc':'2.0','id':6,'method':'tools/call','params':{'name':'prepare_cross','arguments':{'blind':fixtures['blind'],'judgments':fixtures['judgments'],'evidence':fixtures['evidence']}}},
 {'jsonrpc':'2.0','id':7,'method':'tools/call','params':{'name':'check_final','arguments':{'cross':fixtures['cross'],'judgments':fixtures['reviews'],'gates':fixtures['gates']}}},
]
checks=[]
for server in [root/'scripts/review_mcp.py']:
 r=subprocess.run([sys.executable,str(server)],input=''.join(json.dumps(x)+'\n' for x in messages),capture_output=True,text=True,timeout=15,check=True)
 replies={m['id']:m for m in map(json.loads,r.stdout.splitlines())}
 assert replies[1]['result']['protocolVersion']=='2025-03-26'
 assert {t['name'] for t in replies[2]['result']['tools']}=={'prepare_blind','prepare_cross','check_final'}
 packet=json.loads(replies[3]['result']['content'][0]['text'])
 assert 'peer_findings' not in packet and len(packet['draft_sha256'])==64
 assert replies[4]['result']['isError'] is True
 assert replies[5]['error']['code']==-32602
 assert json.loads(replies[6]['result']['content'][0]['text'])['evidence_sha256']==fixtures['cross']['evidence_sha256']
 assert json.loads(replies[7]['result']['content'][0]['text'])['accepted'] is True
 checks.append(str(server.relative_to(root))+': real subprocess handshake, discovery, packet hash/stripping, invalid arguments, unknown tool, cross packet and final gate')
print(json.dumps({'checks_passed':True,'checks':checks,'agy_connection_tested':False,'real_user_archive_scanned':False},indent=2))
