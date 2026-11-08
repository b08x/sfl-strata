#!/usr/bin/env python3
"""Install or explicitly upgrade sfl-strata; preserve existing archive scope and a backup."""
import argparse,shutil,json,uuid
from pathlib import Path

def install(project,source,upgrade=False):
 project=project.expanduser().resolve(strict=True);source=source.resolve(strict=True)
 if not project.is_dir() or project.is_relative_to(source):raise ValueError('choose a project outside the plugin source')
 for folder in [project/'.agents',project/'.agents/plugins',project/'.agents/plugin-backups']:
  if folder.is_symlink() or (folder.exists() and not folder.is_dir()):raise ValueError('invalid or symlinked customization directory')
 dest=project/'.agents/plugins/sfl-strata';backup=None;preserved=None;preserved_servers={}
 if dest.is_symlink():raise ValueError('refusing symlinked plugin destination')
 if dest.exists():
  if not upgrade:raise FileExistsError('sfl-strata already exists; use --upgrade for a backed-up replacement')
  if json.loads((dest/'plugin.json').read_text()).get('name')!='sfl-strata':raise ValueError('existing plugin identity mismatch')
  settings=dest/'config/workstation.json'
  if settings.is_symlink():raise ValueError('refusing symlinked archive config')
  if settings.exists():preserved=settings.read_bytes();json.loads(preserved)
  old_mcp=dest/'mcp_config.json'
  if old_mcp.is_symlink():raise ValueError('refusing symlinked MCP config')
  if old_mcp.exists():
   old_servers=json.loads(old_mcp.read_text()).get('mcpServers',{})
   new_servers=json.loads((source/'mcp_config.json').read_text())['mcpServers']
   for name,entry in new_servers.items():
    previous=old_servers.get(name,{})
    if previous.get('args')==entry['args'] and isinstance(previous.get('command'),str) and previous['command']:
     preserved_servers[name]={k:previous[k] for k in ('command','env') if k in previous}
  backup=project/'.agents/plugin-backups'/('sfl-strata-'+uuid.uuid4().hex);backup.parent.mkdir(parents=True,exist_ok=True);dest.rename(backup)
 dest.parent.mkdir(parents=True,exist_ok=True)
 created=False
 try:
  dest.mkdir();created=True
  shutil.copytree(source,dest,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  if preserved is not None:(dest/'config/workstation.json').write_bytes(preserved)
  if preserved_servers:
   mcp_path=dest/'mcp_config.json';mcp=json.loads(mcp_path.read_text())
   for name,values in preserved_servers.items():mcp['mcpServers'][name].update(values)
   mcp_path.write_text(json.dumps(mcp,indent=2)+'\n')
 except Exception:
  if created:shutil.rmtree(dest)
  if backup:backup.rename(dest)
  raise
 return {'installed':str(dest),'backup':str(backup) if backup else None,'existing_archive_config_preserved':preserved is not None,'preserved_server_commands':sorted(preserved_servers)}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--upgrade',action='store_true');args=p.parse_args()
 try:result=install(args.project,Path(__file__).resolve().parent,args.upgrade)
 except (OSError,ValueError) as error:p.exit(1,str(error)+'\n')
 print(json.dumps(result,indent=2));print('Start a fresh session; run scripts/diagnose.py against the installed directory before using R.U.T.H.')
if __name__=='__main__':main()
