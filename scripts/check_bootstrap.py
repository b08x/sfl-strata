#!/usr/bin/env python3
"""Regression checks for the screenshot's naming, bootstrap, and eager-loading failures."""
from pathlib import Path
from copy import deepcopy
import json,tempfile,sys,subprocess,importlib.util
import yaml
from archive_mcp import ArchiveService
from archive_core import ScopeError
from diagnose import diagnose
root=Path(__file__).resolve().parents[1];checks=[]
def reject(label,call):
 try:call()
 except (ValueError,OSError):checks.append(label)
 else:raise AssertionError(label)
contract=json.loads((root/'references/runtime-contract.json').read_text())
config=json.loads((root/'config/workstation.json').read_text())
empty=ArchiveService(config);status=empty.status({})
assert not status['ready'] and not status['collection_performed'] and status['expected_broker_agent']=='sfl-strata-archive-broker'
checks.append('Empty roots produce setup status, not a permission diagnosis or scan')
for name in ['sfl-strata-coordinator','sfl-strata-archive-broker']:
 text=(root/'agents'/f'{name}.md').read_text()
 assert 'STOP that branch' in text and 'sfl-strata-archive-broker' in text
checks.append('Both operative prompts specify exact broker identity and stop-on-binding-error rule (instruction checks, not behavior proof)')
for name,tools in contract['servers'].items():
 entry=json.loads((root/'mcp_config.json').read_text())['mcpServers'][name]
 assert entry['enabledTools']==tools and all(entry['tools'][t]['eager'] for t in tools)
 assert all('*' not in t for t in tools)
checks.append('Enabled MCP names are exact server-local advertised names, eagerly loaded without wildcard pseudo-tools')
with tempfile.TemporaryDirectory() as d:
 t=Path(d);vault=t/'vault';vault.mkdir();(vault/'example.rb').write_text('fixture')
 (vault/'note.md').write_text('fixture');(vault/'.ssh').mkdir();(vault/'.ssh/hidden').write_text('fixture')
 (vault/'escape').symlink_to(t,target_is_directory=True)
 c=deepcopy(config);c['roots']=[str(vault)]
 service=ArchiveService(c)
 result=service.directory({'limit':1});assert result['has_more'] and len(result['entries'])==1
 page=service.directory({'offset':1,'limit':1});assert len(page['entries'])==1
 assert {result['entries'][0]['name'],page['entries'][0]['name']}=={'example.rb','note.md'}
 assert service.snapshot is None and not c['content_enabled']
 checks.append('Directory listing works in metadata mode without inventory scan and includes non-note files')
 reject('Directory traversal rejected',lambda:service.directory({'relative_path':'..'}))
 reject('Symlink directory rejected',lambda:service.directory({'relative_path':'escape'}))
 reject('Unconfigured root index rejected',lambda:service.directory({'root_index':10}))
 cfile=t/'config.json';cfile.write_text(json.dumps(c))
 messages=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26'}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},{'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'archive_status','arguments':{}}},{'jsonrpc':'2.0','id':4,'method':'tools/call','params':{'name':'list_archive_directory','arguments':{}}}]
 r=subprocess.run([sys.executable,str(root/'scripts/archive_mcp.py'),'--config',str(cfile)],input=''.join(json.dumps(x)+'\n' for x in messages),text=True,capture_output=True,timeout=15,check=True)
 replies={x['id']:x for x in map(json.loads,r.stdout.splitlines())}
 assert all(x['_meta']['antigravity/alwaysLoad'] for x in replies[2]['result']['tools'])
 assert json.loads(replies[3]['result']['content'][0]['text'])['ready']
 assert not replies[4]['result']['isError']
 checks.append('Real stdio tools/list advertises eager schemas; status and directory calls succeed')
 # Upgrade preserves exact user scope and backs up modified profiles outside discovery.
 spec=importlib.util.spec_from_file_location('strata_install',root/'references/legacy/project-install.py');installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
 project=t/'project';project.mkdir();installed=installer.install(project,root)
 dest=Path(installed['installed']);(dest/'config/workstation.json').write_text(json.dumps(c))
 old_mcp=json.loads((dest/'mcp_config.json').read_text());old_mcp['mcpServers']['archive']['command']=sys.executable
 (dest/'mcp_config.json').write_text(json.dumps(old_mcp))
 note=dest/'agents/local-change.txt';note.write_text('keep in backup')
 upgraded=installer.install(project,root,True)
 assert json.loads((dest/'config/workstation.json').read_text())==c
 assert json.loads((dest/'mcp_config.json').read_text())['mcpServers']['archive']['command']==sys.executable
 assert (Path(upgraded['backup'])/'agents/local-change.txt').read_text()=='keep in backup'
 checks.append('Legacy project migration preserves scope and Python command (not the native installer)' )
 data_dir=t/'plugin-data';data_dir.mkdir();(data_dir/'workstation.json').write_text(json.dumps(c))
 report=diagnose(dest,project,probe=True,data_dir=data_dir)
 assert report['ok'] and not report['note_scan_performed'] and not report['live_agent_tool_binding_tested']
 checks.append('Installed-copy diagnostic checks direct servers without scanning notes or claiming live binding')
 bad=dest/'agents/sfl-strata-author.md';bad.write_text(bad.read_text().replace('- view_file','- view_file\n- filesystem/*',1))
 assert not diagnose(dest,project,data_dir=data_dir)['ok']
 checks.append('Diagnostic detects wildcard filesystem entries added to agent tools')
print(json.dumps({'checks_passed':True,'count':len(checks),'checks':checks,'live_model_behavior_tested':False},indent=2))
