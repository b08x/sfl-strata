#!/usr/bin/env python3
"""Synthetic fixture and real stdio tests; does not scan the user's workstation."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,os,subprocess,sys,tempfile
import yaml
from jsonschema import Draft202012Validator
from archive_core import Archive,ScopeError,map_records,timeline,compare_vectors
root=Path(__file__).resolve().parents[1];checks=[]
def refused(label,call):
 try:call()
 except (ScopeError,ValueError):checks.append(label)
 else:raise AssertionError(label)
def parse(p):
 h,b=p.read_text()[4:].split('\n---\n',1);return yaml.safe_load(h),b
manifest=json.loads((root/'plugin.json').read_text());Draft202012Validator(json.loads((root/'schemas/antigravity-plugin.schema.json').read_text())).validate(manifest)
profiles=list((root/'agents').glob('*.md'));assert len(profiles)==12
names=set()
for p in profiles:
 m,b=parse(p);assert m['name']==p.stem and m['name'] not in names;names.add(m['name'])
 assert m['model']=='inherit' and m['commandExecutionPolicy']=='off' and m['excludeDefaultComponents'] is True
 main=p.stem.endswith('-coordinator');broker=p.stem.endswith('-archive-broker');author=p.stem.endswith('-author')
 for f in ['inheritMcp','inheritCustomizations','enable_mcp_tools']:assert m[f] is (main or broker)
 expected=['invoke_subagent','send_message','manage_subagents'] if main else ['view_file','write_to_file','replace_file_content'] if author else []
 assert m['tools']==expected
 for rel in m.get('agents',[])+m.get('skills',[]):
  target=(p.parent/rel).resolve(strict=True);assert target.is_relative_to(root)
 if main:assert len(m['agents'])==11
for s in (root/'schemas').glob('*.json'):Draft202012Validator.check_schema(json.loads(s.read_text()))
checks.append('Official manifest schema, 12 unique profiles, tools, inheritance and contained dependency paths')
config=json.loads((root/'config/workstation.json').read_text());assert config['roots']==[] and not any(config[k] for k in ['content_enabled','host_usage_enabled','git_history_enabled'])
refused('Empty default roots refuse scanning',lambda:Archive(config).inventory())
refused('Host observation disabled by default',lambda:Archive(config).host())
with tempfile.TemporaryDirectory() as temp:
 t=Path(temp);vault=t/'vault';vault.mkdir();outside=t/'outside.md';outside.write_text('must not read')
 (vault/'2016-04-01-productivity.md').write_text('---\ncreated: 2016-04-01\n---\nProductivity means systems for producing output. [[new]] [[missing]]')
 (vault/'new.md').write_text('---\ncreated: 2026-03-01\n---\nProductivity means systems for choosing useful output. [[2016-04-01-productivity]]')
 (vault/'undated.md').write_text('A fragment about cognition, without a declared date.')
 (vault/'escape.md').symlink_to(outside);(vault/'.ssh').mkdir();(vault/'.ssh/notes.md').write_text('excluded')
 (vault/'credentials.md').write_text('excluded');(vault/'large.md').write_text('x'*1100)
 c=deepcopy(config);c.update(roots=[str(vault)],content_enabled=True,max_file_bytes=1000)
 a=Archive(c);snap=a.inventory();assert len(snap['records'])==3
 assert snap['coverage']['skipped'] and not snap['coverage']['complete_within_policy']
 checks.append('Scoped inventory excludes links, hidden/credential paths and reports oversized content')
 refused('Traversal rejected',lambda:a.read('0:../outside.md'))
 refused('Symlink read rejected',lambda:a.read('0:escape.md'))
 refused('Excluded credential read rejected',lambda:a.read('0:credentials.md'))
 unknown=next(r for r in snap['records'] if r['path']=='undated.md');assert unknown['origin_date'] is None
 assert timeline(snap,'productivity')['hits'][0]['declared_date']=='2016-04-01'
 checks.append('Declared dates ordered with provenance; undated origin stays unknown despite mtime')
 graph=map_records(snap,.1);assert graph['explicit_edges'] and graph['unresolved_links'] and graph['lexical_candidates']
 assert 'not embeddings' in graph['method'];checks.append('Explicit links, unresolved links, lexical candidates and components are labeled distinctly')
 ids=[r['id'] for r in snap['records'][:2]]
 vectors=[{'id':ids[0],'values':[1,0]},{'id':ids[1],'values':[1,0]}]
 assert compare_vectors(snap,'fixture-model',vectors)['candidates'][0]['score']==1
 refused('Mixed vector dimensions rejected',lambda:compare_vectors(snap,'fixture',[vectors[0],{'id':ids[1],'values':[1]}]))
 refused('Non-finite vector rejected',lambda:compare_vectors(snap,'fixture',[{'id':ids[0],'values':[float('nan')]}]))
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in vault.glob('*.md') if not p.is_symlink()}
 cfile=t/'policy.json';cfile.write_text(json.dumps(c))
 msgs=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26'}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/list'},{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'inventory_archive','arguments':{'limit':1}}},{'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'host_snapshot','arguments':{}}},{'jsonrpc':'2.0','id':5,'method':'tools/call','params':{'name':'read_note','arguments':{'note_id':snap['records'][0]['id'],'expected_sha256':snap['records'][0]['content_sha256']}}},{'jsonrpc':'2.0','id':6,'method':'tools/call','params':{'name':'read_note','arguments':{'note_id':snap['records'][0]['id'],'expected_sha256':'0'*64}}}]
 r=subprocess.run([sys.executable,str(root/'scripts/archive_mcp.py'),'--config',str(cfile)],input=''.join(json.dumps(x)+'\n' for x in msgs),capture_output=True,text=True,timeout=15,check=True)
 replies={x['id']:x for x in map(json.loads,r.stdout.splitlines())}
 assert len(replies[2]['result']['tools'])==9
 page=json.loads(replies[3]['result']['content'][0]['text']);assert page['has_more'] and len(page['records'])==1 and 'excerpt' not in page['records'][0]
 assert replies[4]['result']['isError']
 assert replies[5]['result']['isError'] is False and replies[6]['result']['isError'] is True
 checks.append('Actual MCP note reads check captured content hash and reject mismatches')
 checks.append('Real stdio initialization, nine-tool discovery, paginated metadata and denied host request')
 after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in vault.glob('*.md') if not p.is_symlink()};assert before==after
 checks.append('Fixture source contents unchanged after collection and mapping')
 c['git_history_enabled']=True
 git_ok=subprocess.run(['git','--version'],capture_output=True).returncode==0
 assert git_ok
 for command in [['git','init','-q'],['git','add','new.md'],['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','core.hooksPath=/dev/null','-c','commit.gpgsign=false','commit','-qm','fixture']]:
  subprocess.run(command,cwd=vault,check=True,capture_output=True)
 history=Archive(c).history('0:new.md');assert len(history['versions'])==1 and history['versions'][0]['author_date']
 checks.append('Fixed read-only Git history command returns synthetic commit author and committer dates')
 c.update(max_files=1);assert not Archive(c).inventory()['coverage']['complete_within_policy'];checks.append('File cap is reported as incomplete coverage')
print(json.dumps({'checks_passed':True,'count':len(checks),'checks':checks,'actual_host_observation_run':False,'real_user_archive_scanned':False,'agy_runtime_tested':False},indent=2))
