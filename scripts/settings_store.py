"""Durable plugin-data configuration; no archive scan and no source-note writes."""
import json,os,tempfile
from pathlib import Path

def save_config(path,value):
 path=Path(path).expanduser().absolute()
 if path.is_symlink():raise ValueError('Refusing a symlinked configuration file')
 path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 fd,temp=tempfile.mkstemp(prefix='.strata-config-',dir=path.parent)
 try:
  with os.fdopen(fd,'w') as stream:
   json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
  os.replace(temp,path)
 finally:
  if os.path.exists(temp):os.unlink(temp)

def load_config(path,defaults=None):
 path=Path(path).expanduser().absolute()
 if path.is_symlink():raise ValueError('Refusing a symlinked configuration file')
 if path.exists():return json.loads(path.read_text())
 if defaults is None:raise FileNotFoundError(path)
 value=json.loads(Path(defaults).read_text())
 validate(value) # Validate only, no scanning.
 save_config(path,value)
 return value

def default_path():
 return Path(os.environ.get('XDG_CONFIG_HOME',Path.home()/'.config'))/'sfl-strata/workstation.json'

def revision(value):
 import hashlib
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def validate(value):
 from archive_core import Archive
 if not isinstance(value,dict):raise ValueError('Configuration must be a JSON object')
 if not isinstance(value.get('roots'),list) or any(not isinstance(x,str) for x in value['roots']):raise ValueError('roots must be a list of paths')
 for key in ('content_enabled','host_usage_enabled','git_history_enabled'):
  if not isinstance(value.get(key),bool):raise ValueError(key+' must be true or false')
 for key in ('extensions','exclude_names','exclude_globs'):
  if not isinstance(value.get(key),list) or any(not isinstance(x,str) for x in value[key]):raise ValueError(key+' must be a list of strings')
 Archive(value)
 return value
