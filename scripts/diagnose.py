#!/usr/bin/env python3
"""Inspect plugin wiring; optional direct MCP and native CLI checks. No note scan or config edits."""
import argparse,json,subprocess,sys,shutil
from pathlib import Path
from settings_store import default_path
import yaml

def frontmatter(path):return yaml.safe_load(path.read_text()[4:].split('\n---\n',1)[0])
def diagnose(plugin,project,probe=False,native=False,data_dir=None,config_path=None):
 report={'plugin_path':str(plugin),'project':str(project),'checks':[],'live_agent_tool_binding_tested':False,'note_scan_performed':False}
 def check(name,ok,detail):report['checks'].append({'check':name,'ok':bool(ok),'detail':detail})
 manifest=json.loads((plugin/'plugin.json').read_text());contract=json.loads((plugin/'references/runtime-contract.json').read_text())
 check('package version',manifest.get('version')==contract['version'],manifest.get('version'))
 coordinator=frontmatter(plugin/'agents/sfl-strata-coordinator.md')
 roster=[]
 for rel in coordinator.get('agents',[]):
  target=(plugin/'agents'/rel).resolve()
  if not target.is_relative_to(plugin.resolve()) or not target.is_file():check('child path',False,rel);continue
  meta=frontmatter(target);roster.append(meta.get('name'))
  suspicious=[t for t in meta.get('tools',[]) if '*' in t or t.startswith(('filesystem:','filesystem/','file_system/'))]
  check('child tools '+str(meta.get('name')),not suspicious,{'unexpected_filesystem_patterns':suspicious})
 check('exact broker declaration','sfl-strata-archive-broker' in roster,{'expected':'sfl-strata-archive-broker','declared':roster})
 mcp=json.loads((plugin/'mcp_config.json').read_text())['mcpServers']
 for server,names in contract['servers'].items():
  entry=mcp.get(server,{})
  check('MCP enablement '+server,entry.get('enabledTools')==names and all(entry.get('tools',{}).get(n,{}).get('eager') is True for n in names),{'expected_server_local_tool_names':names})
 config_path=Path(config_path) if config_path else Path(data_dir)/'workstation.json' if data_dir else default_path()
 config=json.loads((config_path if config_path.exists() else plugin/'config/workstation.json').read_text())
 check('configured archive roots',bool(config.get('roots')),{'configuration_file':str(config_path),'root_count':len(config.get('roots',[])),'content_enabled':config.get('content_enabled')})
 if probe:
  # Use the actual server command, substituting only the documented plugin root variable.
  for server,tool in [('archive','archive_status'),('review_packets',None)]:
   entry=mcp[server];args=[entry['command']]+[s.replace('${PLUGIN_ROOT}',str(plugin)).replace('${PLUGIN_DATA}',str(data_dir or config_path.parent)) for s in entry['args']]
   if server=='archive':args+=['--config',str(config_path)]
   messages=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'strata-diagnose','version':'0.3.0'}}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}}]
   if tool:messages.append({'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':tool,'arguments':{}}})
   try:
    r=subprocess.run(args,input=''.join(json.dumps(x)+'\n' for x in messages),capture_output=True,text=True,timeout=20,cwd=project)
    replies={x['id']:x for x in map(json.loads,r.stdout.splitlines())}
    advertised=[x['name'] for x in replies[2]['result']['tools']]
    check('direct MCP '+server,r.returncode==0 and set(advertised)==set(contract['servers'][server]),{'exit_code':r.returncode,'advertised_tools':advertised})
    if tool:
     result=replies[3]['result'];data=json.loads(result['content'][0]['text']) if not result.get('isError') else {'error':result['content'][0]['text']}
     check('archive status tool',not result.get('isError'),data)
   except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as error:check('direct MCP '+server,False,{'error':str(error)})
 if native:
  executable=shutil.which('agy');check('agy executable',executable is not None,'available' if executable else 'not on PATH')
  if executable:
   for name,args in [('version',['--version']),('plugin validation',['plugin','validate','--strict',str(plugin)]),('native agent roster',['agents'])]:
    try:
     r=subprocess.run([executable,*args],cwd=project,capture_output=True,text=True,timeout=30)
     ok=r.returncode==0
     if name=='native agent roster':ok=ok and 'sfl-strata-archive-broker' in r.stdout
     check('native '+name,ok,{'exit_code':r.returncode,'stdout':r.stdout[:12000],'stderr':r.stderr[:2000],'note':'Exit zero alone does not prove the expected agent was discovered' if name=='native agent roster' else ''})
    except (OSError,subprocess.TimeoutExpired) as error:check('native '+name,False,{'error':str(error)})
 report['note']='Direct stdio success proves server behavior only; it does not prove Antigravity enabled that tool in the active agent. No credentials, environment variables, global MCP config, note contents or host usage are inspected by this script.'
 report['ok']=all(x['ok'] for x in report['checks']);return report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,default=Path.cwd());p.add_argument('--data-dir',type=Path,help='Legacy explicit settings directory');p.add_argument('--config',type=Path,help='Override the shared workstation.json settings path');p.add_argument('--plugin-dir',type=Path);p.add_argument('--probe',action='store_true');p.add_argument('--native',action='store_true');args=p.parse_args()
 project=args.project.expanduser().resolve(strict=True);plugin=(args.plugin_dir or Path.home()/'.gemini/config/plugins/sfl-strata').expanduser().resolve(strict=True)
 try:report=diagnose(plugin,project,args.probe,args.native,args.data_dir,args.config)
 except (OSError,ValueError,KeyError) as error:p.exit(2,str(error)+'\n')
 print(json.dumps(report,indent=2));raise SystemExit(0 if report['ok'] else 1)
if __name__=='__main__':main()
