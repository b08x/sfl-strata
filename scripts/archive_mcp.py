#!/usr/bin/env python3
"""Lazy, local stdio MCP archive collector. Startup reads policy but does not scan."""
import argparse,json,threading
from settings_store import default_path,load_config,validate,revision
from pathlib import Path
import review_mcp as rpc
from archive_core import Archive,map_records,compare_vectors,timeline

def schema(properties={},required=[]):return {'type':'object','properties':properties,'required':required,'additionalProperties':False}
class ArchiveService:
 def __init__(self,config):self.archive=Archive(config);self.snapshot=None
 def status(self,a):
  return {'plugin':'sfl-strata','version':'0.2.0','configured_roots':[str(x) for x in self.archive.roots],'ready':bool(self.archive.roots),'content_enabled':self.archive.c['content_enabled'],'host_usage_enabled':self.archive.c['host_usage_enabled'],'git_history_enabled':self.archive.c['git_history_enabled'],'collection_performed':self.snapshot is not None,'filesystem_server_required':False,'expected_broker_agent':'sfl-strata-archive-broker','next_action':'inventory_archive or list_archive_directory' if self.archive.roots else 'Set explicit roots in configuration_file using configure.py --config; do not edit installed defaults or request filesystem permissions'}
 def directory(self,a):
  from archive_core import ScopeError
  from datetime import datetime,timezone
  import stat
  idx=a.get('root_index',0);relative=Path(a.get('relative_path','.'))
  if idx<0 or idx>=len(self.archive.roots):raise ScopeError('No such configured archive root; call archive_status')
  if relative.is_absolute() or '..' in relative.parts:raise ScopeError('relative_path must stay inside the selected configured root')
  root=self.archive.roots[idx];target=root/relative;cursor=root
  for part in relative.parts:
   cursor=cursor/part
   if cursor.is_symlink():raise ScopeError('Symlink directories are not followed')
  if relative.parts and self.archive.excluded(relative):raise ScopeError('Excluded directory')
  if not target.resolve(strict=True).is_relative_to(root) or not target.is_dir():raise ScopeError('Not an in-scope directory')
  entries=[];excluded=0;errors=0;truncated=False;examined=0
  import os
  with os.scandir(target) as iterator:
   for item in iterator:
    examined+=1
    if examined>5000:truncated=True;break
    rel=(target/item.name).relative_to(root)
    if item.is_symlink() or self.archive.excluded(rel):excluded+=1;continue
    try:
     st=item.stat(follow_symlinks=False)
     kind='directory' if stat.S_ISDIR(st.st_mode) else 'file' if stat.S_ISREG(st.st_mode) else 'other'
     entries.append({'name':item.name,'relative_path':rel.as_posix(),'kind':kind,'size':st.st_size,'mtime_observed':datetime.fromtimestamp(st.st_mtime,timezone.utc).isoformat()})
    except OSError:errors+=1
  entries.sort(key=lambda x:x['name']);offset=a.get('offset',0);limit=a.get('limit',50)
  more=offset+limit<len(entries)
  return {'root_index':idx,'relative_path':relative.as_posix(),'entries':entries[offset:offset+limit],'has_more':more,'next_offset':offset+limit if more else None,'excluded_count':excluded,'unreadable_count':errors,'enumeration_truncated':truncated,'scope':'one configured directory; nonrecursive metadata; no file contents','ordering_limit':'directory contents can change between requests; no snapshot completeness claimed'}
 def inventory(self,a):
  if self.snapshot is None or a.get('refresh',False):self.snapshot=self.archive.inventory()
  s=self.snapshot;offset=a.get('offset',0);limit=a.get('limit',20)
  records=s['records'][offset:offset+limit]
  if not a.get('include_excerpts',False):records=[{k:v for k,v in r.items() if k not in ('excerpt','wiki_links','markdown_links')} for r in records]
  more=offset+limit<len(s['records'])
  return {**{k:v for k,v in s.items() if k!='records'},'records':records,'offset':offset,'has_more':more,'next_offset':offset+limit if more else None,'snapshot_cached':True,'freshness':'captured; refresh and compare before final review'}
 def captured(self):
  if self.snapshot is None:raise ValueError('Call inventory_archive before using snapshot operations')
  return self.snapshot
 def read(self,a):
  known={r['id']:r for r in self.captured()['records']}
  if a['note_id'] not in known:raise ValueError('Note is outside the captured inventory')
  r=self.archive.read(a['note_id'])
  if a['expected_sha256']!=r['content_sha256']:raise ValueError('Source changed or expected hash is incorrect; refresh inventory')
  return {**r,'snapshot_id':self.snapshot['snapshot_id']}
 def history(self,a):
  if a['note_id'] not in {r['id'] for r in self.captured()['records']}:raise ValueError('Note is outside the captured inventory')
  return self.archive.history(a['note_id'],a.get('limit',30))

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=default_path());p.add_argument('--legacy-config',type=Path);p.add_argument('--defaults',type=Path);args=p.parse_args()
 # One-time migration; installed defaults never overwrite configured policy.
 defaults=args.legacy_config if args.legacy_config and args.legacy_config.is_file() else args.defaults
 service=ArchiveService(validate(load_config(args.config,defaults)))
 lock=threading.RLock();active_revision=revision(service.archive.c)
 def reload_status():
  nonlocal active_revision
  with lock:
   value=validate(load_config(args.config))
   digest=revision(value)
   if digest!=active_revision:
    service.archive=Archive(value);service.snapshot=None;active_revision=digest
   return {**service.status({}),'configuration_file':str(args.config.expanduser().absolute()),'configuration_revision':digest,'live_reload':True}
 from live_status import serve
 def live():
  try:return reload_status()
  except (OSError,ValueError,KeyError,TypeError) as error:return {'configuration_file':str(args.config.expanduser().absolute()),'ready':False,'configuration_error':str(error)}
 try:serve(live)
 except (OSError,ValueError) as error:
  import sys
  print('Live-status endpoint unavailable: '+str(error),file=sys.stderr)
 tools=[
 {'name':'archive_status','description':'Check this plugin version, configured roots and enabled collection modes without scanning or reading note content. Use before tool or permission speculation.','inputSchema':schema()},
 {'name':'list_archive_directory','description':'List one directory inside an explicitly configured archive root. Does not require a generic filesystem MCP server and reads no file contents.','inputSchema':schema({'root_index':{'type':'integer','minimum':0},'relative_path':{'type':'string'},'offset':{'type':'integer','minimum':0},'limit':{'type':'integer','minimum':1,'maximum':200}})},
 {'name':'inventory_archive','description':'Capture approved roots lazily or return a cached snapshot page. Metadata-only response by default. Paginate all relevant records and refresh/compare before final evidence binding.','inputSchema':schema({'refresh':{'type':'boolean'},'offset':{'type':'integer','minimum':0},'limit':{'type':'integer','minimum':1,'maximum':50},'include_excerpts':{'type':'boolean'}})},
 {'name':'read_note','description':'Read a captured UTF-8 note, bounded by policy and verified against its expected content hash. Requires enabled content mode.','inputSchema':schema({'note_id':{'type':'string'},'expected_sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}},['note_id','expected_sha256'])},
 {'name':'host_snapshot','description':'One current observation of load, uptime and visible process-name counts, if enabled. No command arguments or usage history.','inputSchema':schema()},
 {'name':'git_history','description':'Read bounded Git commit/author dates for a selected in-scope note, if enabled. Does not load historical contents or infer idea inception.','inputSchema':schema({'note_id':{'type':'string'},'limit':{'type':'integer','minimum':1,'maximum':100}},['note_id'])},
 {'name':'map_archive','description':'Map explicit links and excerpt TF-IDF cosine in a bounded captured corpus. Does not generate embeddings or prove semantic communities.','inputSchema':schema({'threshold':{'type':'number','minimum':0,'maximum':1},'max_documents':{'type':'integer','minimum':1,'maximum':500}})},
 {'name':'term_timeline','description':'Find exact term contexts with declared note/filename dates in captured excerpts. Not automatic proof of definition drift.','inputSchema':schema({'term':{'type':'string','minLength':1,'maxLength':200}},['term'])},
 {'name':'compare_vectors','description':'Compare supplied embeddings for captured note IDs, with one declared model and consistent finite dimensions. No embedding generation or network calls.','inputSchema':schema({'model':{'type':'string','minLength':1},'vectors':{'type':'array','minItems':1,'maxItems':300,'items':{'type':'object','properties':{'id':{'type':'string'},'values':{'type':'array','minItems':1,'maxItems':8192,'items':{'type':'number'}}},'required':['id','values'],'additionalProperties':False}},'threshold':{'type':'number','minimum':0,'maximum':1}},['model','vectors'])}]
 for tool in tools:tool['_meta']={'antigravity/alwaysLoad':True}
 rpc.TOOLS=tools;rpc.BY_NAME={x['name']:x for x in tools}
 rpc.FUNCTIONS={'archive_status':service.status,'list_archive_directory':service.directory,'inventory_archive':service.inventory,'read_note':service.read,'host_snapshot':lambda a:service.archive.host(),'git_history':service.history,'map_archive':lambda a:map_records(service.captured(),a.get('threshold',.2),a.get('max_documents',300)),'term_timeline':lambda a:timeline(service.captured(),a['term']),'compare_vectors':lambda a:compare_vectors(service.captured(),a['model'],a['vectors'],a.get('threshold',.7))}
 original=rpc.Server.handle
 def handle(self,request):
  with lock:
   if isinstance(request,dict) and request.get('method')=='tools/call':
    try:reload_status()
    except (OSError,ValueError,KeyError,TypeError) as error:
     return {'jsonrpc':'2.0','id':request.get('id'),'result':{'isError':True,'content':[{'type':'text','text':'Configuration invalid; collection blocked: '+str(error)}]}}
   response=original(self,request)
  if isinstance(request,dict) and request.get('method')=='initialize' and response and 'result' in response:response['result']['serverInfo']={'name':'sfl-strata-archive','version':'0.2.0'}
  if isinstance(request,dict) and request.get('method')=='tools/call' and request.get('params',{}).get('name')=='archive_status' and response and 'result' in response and not response['result'].get('isError'):
   result=response['result'];status=json.loads(result['content'][0]['text']);status['configuration_file']=str(args.config.expanduser().absolute());status['configuration_revision']=active_revision;status['live_reload']=True;result['content'][0]['text']=json.dumps(status,separators=(',',':'))
  return response
 rpc.Server.handle=handle
 rpc.main()
if __name__=='__main__':main()
