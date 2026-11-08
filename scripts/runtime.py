"""An isolated, user-owned UI runtime; never install into system Python."""
import os,sys,subprocess,venv
from pathlib import Path

def python_path():
 return Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))/'sfl-strata/runtime/bin/python'

def wizard_runtime():
 try:
  import textual,jsonschema,yaml
  if textual.__version__=='8.2.8':return
 except ImportError:pass
 target=python_path()
 if Path(sys.prefix).resolve()==target.parents[1].resolve():
  raise SystemExit('Wizard dependencies are incomplete. Remove the sfl-strata runtime directory and rerun configure.py.')
 if not target.exists():
  print('Preparing the SFL Strata interface in an isolated Python environment…',flush=True)
  venv.EnvBuilder(with_pip=True).create(target.parents[1])
 check=subprocess.run([str(target),'-c',"import textual,jsonschema,yaml; assert textual.__version__=='8.2.8'"],capture_output=True)
 if check.returncode:
  subprocess.run([str(target),'-m','pip','install','textual==8.2.8','jsonschema>=4.18,<5','PyYAML>=6,<7'],check=True)
 os.execv(str(target),[str(target),*sys.argv])
