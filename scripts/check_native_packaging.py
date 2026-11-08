#!/usr/bin/env python3
"""Native launch, canonical settings and one-time migration regression checks."""
from pathlib import Path
import json,subprocess,sys,tempfile,os
from settings_store import load_config
root=Path(__file__).resolve().parents[1];checks=[]
assert (root/'plugin.json').is_file() and not (root/'gemini-extension.json').exists() and not (root/'install.py').exists()
checks.append('Antigravity plugin layout retained')
mcp=json.loads((root/'mcp_config.json').read_text())['mcpServers']
assert mcp['archive']['args'][0].endswith('/launch_service.py') and '--legacy-config' in mcp['archive']['args']
with tempfile.TemporaryDirectory() as temporary:
 t=Path(temporary);data=t/'plugin-data';config=t/'xdg/sfl-strata/workstation.json';vault=t/'vault';vault.mkdir()
 env={**os.environ,'XDG_CONFIG_HOME':str(t/'xdg'),'XDG_DATA_HOME':str(t/'data')}
 command=[sys.executable]+[x.replace('${PLUGIN_ROOT}',str(root)).replace('${PLUGIN_DATA}',str(data)) for x in mcp['archive']['args']]
 messages=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26'}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'archive_status','arguments':{}}}]
 def probe():
  r=subprocess.run(command,input=''.join(json.dumps(x)+'\n' for x in messages),capture_output=True,text=True,timeout=15,check=True,env=env)
  replies={x['id']:x for x in map(json.loads,r.stdout.splitlines())};return json.loads(replies[2]['result']['content'][0]['text'])
 status=probe();assert status['configuration_file']==str(config) and not status['ready'] and not status['collection_performed']
 checks.append('Native launcher initializes canonical XDG settings without collection')
 subprocess.run([sys.executable,str(root/'configure.py'),'--root',str(vault),'--text'],check=True,env=env,capture_output=True)
 status=probe();assert status['configured_roots']==[str(vault)] and status['content_enabled'] and status['live_reload']
 checks.append('CLI and native launcher share the same canonical file')
 stored=json.loads(config.read_text());changed=t/'defaults.json';changed.write_text('{}');assert load_config(config,changed)==stored
 checks.append('Package defaults never overwrite retained policy')
 config.unlink();data.mkdir();legacy={**stored,'content_enabled':False};(data/'workstation.json').write_text(json.dumps(legacy))
 status=probe();assert status['configured_roots']==[str(vault)] and not status['content_enabled'] and json.loads(config.read_text())==legacy
 checks.append('Previous native plugin data migrates only when canonical settings are absent')
 alias=t/'link';alias.symlink_to(config)
 try:load_config(alias,changed)
 except ValueError:checks.append('Symlinked settings rejected')
 else:raise AssertionError('Symlink followed')
print(json.dumps({'checks_passed':True,'count':len(checks),'checks':checks,'native_global_installation_tested':False,'authenticated_model_execution_tested':False},indent=2))
