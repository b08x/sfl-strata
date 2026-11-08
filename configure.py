#!/usr/bin/env python3
"""Launch the SFL Strata setup wizard, or configure explicitly from a script."""
from pathlib import Path
import argparse,json,sys,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parent/'scripts'))
from settings_store import save_config,default_path,validate

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--config',type=Path,default=default_path(),help='Settings file; defaults to $XDG_CONFIG_HOME/sfl-strata/workstation.json')
 p.add_argument('--wizard',action='store_true',help='Launch interactive setup')
 p.add_argument('--root','--roots',type=Path,action='append',dest='root',help='Archive directory; repeat for multiple roots')
 for flag in ('text','host-usage','git-history'):p.add_argument('--'+flag,action=argparse.BooleanOptionalAction,default=None)
 p.add_argument('--max-files',type=int)
 args=p.parse_args();target=args.config.expanduser().absolute()
 if args.wizard or not any((args.root,args.text is not None,args.host_usage is not None,args.git_history is not None,args.max_files is not None)):
  from runtime import wizard_runtime
  try:wizard_runtime()
  except (OSError,subprocess.CalledProcessError) as error:p.exit(2,f'Unable to prepare the wizard runtime: {error}. Ensure Python venv/pip and internet access are available, or preinstall requirements.txt in a private environment.\n')
  from setup_wizard import StrataWizard
  StrataWizard(target).run();return
 try:
  if target.is_symlink():raise ValueError('Refusing symlinked configuration')
  defaults=Path(__file__).resolve().parent/'config/workstation.json'
  config=json.loads((target if target.exists() else defaults).read_text())
  if args.root is not None:config['roots']=list(dict.fromkeys(str(x.expanduser().resolve(strict=True)) for x in args.root))
  for arg,key in [('text','content_enabled'),('host_usage','host_usage_enabled'),('git_history','git_history_enabled'),('max_files','max_files')]:
   if getattr(args,arg) is not None:config[key]=getattr(args,arg)
  validate(config);save_config(target,config)
 except (ValueError,OSError,KeyError) as error:p.error(str(error))
 print(f'Saved {target}. Running 0.2 workers reload it before the next request. No collection performed.')
if __name__=='__main__':main()
