"""Private status-only sockets for already-running MCP workers. No collection."""
import os,socket,threading,json,tempfile,stat,atexit
from pathlib import Path

def directory():
 base=Path(os.environ.get('XDG_RUNTIME_DIR',tempfile.gettempdir()))/f'sfl-strata-{os.getuid()}'
 base.mkdir(mode=0o700,exist_ok=True)
 info=base.lstat()
 if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o077:raise ValueError('Status directory must be a private, user-owned directory')
 return base

def serve(callback):
 path=directory()/f'worker-{os.getpid()}.sock'
 server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(str(path));os.chmod(path,0o600);server.listen(4)
 def cleanup():
  server.close();path.unlink(missing_ok=True)
 atexit.register(cleanup)
 def loop():
  while True:
   try:
    client,_=server.accept()
    with client:
     client.settimeout(.5)
     if client.recv(64).strip()==b'status':
      client.sendall(json.dumps({'pid':os.getpid(),**callback()}).encode()+b'\n')
   except (OSError,ValueError):continue
 threading.Thread(target=loop,daemon=True,name='strata-status').start()
 return path

def observe(config_path):
 found=[]
 for path in directory().glob('worker-*.sock'):
  try:
   with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
    client.settimeout(.3);client.connect(str(path));client.sendall(b'status\n');chunks=b''
    while b'\n' not in chunks and len(chunks)<262144:
     data=client.recv(8192)
     if not data:break
     chunks+=data
   result=json.loads(chunks)
   if result.get('configuration_file')==str(Path(config_path).expanduser().absolute()):found.append(result)
  except (OSError,ValueError):pass
 return found
