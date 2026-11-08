"""Bounded read-only archive evidence and one-shot Linux observations. No network."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import fnmatch,hashlib,json,math,os,re,stat,subprocess

STOP=set('the a an and or of to in on is it this that for with as by be are was were i you we my your from at'.split())
def now():return datetime.now(timezone.utc).isoformat()
def sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
class ScopeError(ValueError):pass

class Archive:
 def __init__(self,config):
  self.c=config
  self.roots=[Path(x).expanduser().resolve(strict=True) for x in config['roots']]
  if any(not p.is_dir() for p in self.roots):raise ScopeError('roots must be directories')
  for key,lower,upper in [('max_files',1,10000),('max_dirs',1,20000),('max_file_bytes',1,1048576),('max_total_bytes',1,134217728),('max_excerpt_chars',1,32000)]:
   if not isinstance(config[key],int) or isinstance(config[key],bool) or not lower<=config[key]<=upper:raise ScopeError('invalid collector bound: '+key)
 def excluded(self,relative):
  return any(p.startswith('.') or p in self.c['exclude_names'] for p in relative.parts) or any(fnmatch.fnmatch(relative.name.lower(),pat.lower()) for pat in self.c['exclude_globs'])
 def locate(self,note_id):
  try:idx,rel=note_id.split(':',1);idx=int(idx);relative=Path(rel)
  except (ValueError,TypeError):raise ScopeError('invalid note id')
  if idx<0 or idx>=len(self.roots) or not rel or relative.is_absolute() or '..' in relative.parts:raise ScopeError('outside configured scope')
  root=self.roots[idx];target=root/relative
  if self.excluded(relative):raise ScopeError('excluded path')
  cursor=root
  for part in relative.parts:
   cursor=cursor/part
   if cursor.is_symlink():raise ScopeError('symlinks are not followed')
  if not target.resolve(strict=True).is_relative_to(root):raise ScopeError('outside configured root')
  return target,relative
 def read(self,note_id):
  if not self.c['content_enabled']:raise ScopeError('content mode is disabled')
  path,relative=self.locate(note_id)
  if path.suffix.lower() not in self.c['extensions']:raise ScopeError('unsupported note extension')
  fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0))
  with os.fdopen(fd,'rb') as stream:
   st=os.fstat(stream.fileno())
   if not stat.S_ISREG(st.st_mode):raise ScopeError('not a regular file')
   raw=stream.read(self.c['max_file_bytes']+1)
  if len(raw)>self.c['max_file_bytes']:raise ScopeError('file exceeds content bound')
  if b'\0' in raw:raise ScopeError('binary content is unsupported')
  try:text=raw.decode('utf-8')
  except UnicodeDecodeError:raise ScopeError('only UTF-8 note text is supported')
  return {'id':note_id,'content_sha256':hashlib.sha256(raw).hexdigest(),'text':text,'bytes':len(raw),'stat':{'mtime_ns':st.st_mtime_ns,'size':st.st_size}}
 def inventory(self):
  if not self.roots:raise ScopeError('no roots configured; run configure.py with explicit roots')
  records=[];skipped=[];total=0;dirs=0;exclusions=0;halt=False
  for idx,root in enumerate(self.roots):
   if halt:break
   def walk_error(error):skipped.append({'path':str(error.filename),'reason':'unreadable directory'})
   for directory,subdirs,files in os.walk(root,followlinks=False,onerror=walk_error):
    dirs+=1
    if dirs>self.c['max_dirs']:skipped.append({'path':str(root),'reason':'directory bound reached'});halt=True;break
    parent=Path(directory)
    kept=[]
    for d in sorted(subdirs):
     q=parent/d
     if q.is_symlink() or self.excluded(q.relative_to(root)):exclusions+=1
     else:kept.append(d)
    subdirs[:]=kept
    for name in sorted(files):
     q=parent/name;rel=q.relative_to(root)
     if q.is_symlink() or self.excluded(rel) or q.suffix.lower() not in self.c['extensions']:exclusions+=1;continue
     if len(records)>=self.c['max_files']:skipped.append({'path':str(root),'reason':'file bound reached'});halt=True;break
     note_id=str(idx)+':'+rel.as_posix()
     try:
      st=q.stat(follow_symlinks=False)
      if not stat.S_ISREG(st.st_mode):continue
      rec={'id':note_id,'path':rel.as_posix(),'size':st.st_size,'mtime_observed':datetime.fromtimestamp(st.st_mtime,timezone.utc).isoformat(),'origin_date':None,'date_provenance':'unknown','root':idx}
      if self.c['content_enabled']:
       if total+st.st_size>self.c['max_total_bytes']:skipped.append({'path':note_id,'reason':'total content byte bound reached'});halt=True;break
       data=self.read(note_id);total+=data['bytes'];text=data['text']
       if data['stat']!={'mtime_ns':st.st_mtime_ns,'size':st.st_size}:raise ScopeError('file changed while inventorying')
       rec['content_sha256']=data['content_sha256'];rec['excerpt']=text[:self.c['max_excerpt_chars']];rec['excerpt_truncated']=len(text)>self.c['max_excerpt_chars']
       # Declared dates are evidence of a declaration, not verified authorship dates.
       match=re.search(r'(?mi)^(?:date|created|created_at):\s*["\']?(\d{4}-\d{2}-\d{2})',text[:2048]) if text.startswith('---') else None
       if match:date=match.group(1);provenance='declared note field'
       else:
        match=re.match(r'(\d{4}-\d{2}-\d{2})',rel.name);date=match.group(1) if match else None;provenance='filename declaration'
       if date:
        try:datetime.strptime(date,'%Y-%m-%d');rec.update(origin_date=date,date_provenance=provenance)
        except ValueError:rec['date_provenance']='invalid declared date'
       rec['wiki_links']=re.findall(r'\[\[([^\]|#]+)',text)
       rec['markdown_links']=re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',text)
      else:
       match=re.match(r'(\d{4}-\d{2}-\d{2})',rel.name)
       if match:
        try:datetime.strptime(match[1],'%Y-%m-%d');rec.update(origin_date=match[1],date_provenance='filename declaration')
        except ValueError:pass
      records.append(rec)
     except (OSError,ScopeError) as error:skipped.append({'path':note_id,'reason':str(error)})
    if halt:break
  policy={k:self.c[k] for k in self.c if k!='roots'}
  identity={'roots':[str(x) for x in self.roots],'policy':policy,'records':records,'skipped':skipped}
  return {'snapshot_id':'snapshot:'+sha(identity),'observed_at':now(),'roots':[str(x) for x in self.roots],'records':records,'coverage':{'bounded_scope':True,'complete_within_policy':not skipped,'excluded_count':exclusions,'skipped':skipped,'files':len(records),'content_bytes':total,'content_enabled':self.c['content_enabled']},'policy':policy,'date_warning':'mtime is filesystem observation; declared dates do not establish original creation or belief inception'}
 def host(self):
  if not self.c['host_usage_enabled']:raise ScopeError('host observations are disabled')
  report={'observed_at':now(),'kind':'single current observation','platform':os.name,'history_available':False}
  try:report['load_average_1_5_15']=list(os.getloadavg())
  except (OSError,AttributeError):report['load_average_1_5_15']=None
  if Path('/proc/uptime').exists():report['uptime_seconds']=float(Path('/proc/uptime').read_text().split()[0])
  counts=Counter()
  if Path('/proc').exists():
   for q in Path('/proc').iterdir():
    if q.name.isdigit():
     try:counts[(q/'comm').read_text().strip()]+=1
     except OSError:pass
   report['process_name_counts']=dict(sorted(counts.items()));report['scope']='visible /proc entries, possibly container-scoped'
  report['not_collected']=['command arguments','keystrokes','browser history','screenshots','file access history']
  return report
 def history(self,note_id,limit=30):
  if not self.c['git_history_enabled']:raise ScopeError('Git history reads are disabled')
  path,_=self.locate(note_id)
  if not 1<=limit<=100:raise ScopeError('history limit must be 1..100')
  env=dict(os.environ);env['GIT_TERMINAL_PROMPT']='0';env['GIT_OPTIONAL_LOCKS']='0'
  command=['git','--no-pager','-c','core.hooksPath=/dev/null','log','--follow','--max-count='+str(limit),'--format=%H%x09%aI%x09%cI','--',path.name]
  try:result=subprocess.run(command,cwd=path.parent,env=env,capture_output=True,text=True,timeout=15)
  except (OSError,subprocess.TimeoutExpired):raise ScopeError('Git executable unavailable or read timed out')
  if result.returncode:raise ScopeError('Git history unavailable for selected note')
  return {'note_id':note_id,'versions':[dict(zip(['commit','author_date','committer_date'],line.split('\t'))) for line in result.stdout.splitlines()],'limit':limit,'possibly_truncated':len(result.stdout.splitlines())==limit,'warning':'Commit dates are version evidence, not idea inception; historical file contents are not loaded by this tool'}

def tokens(text):return [x for x in re.findall(r'\b[\w-]{3,}\b',text.casefold()) if x not in STOP]
def map_records(snapshot,threshold=.2,max_documents=300):
 if not 0<=threshold<=1 or not 1<=max_documents<=500:raise ScopeError('invalid map bound')
 records=snapshot['records'][:max_documents]
 if not snapshot['coverage']['content_enabled']:raise ScopeError('text mode is required for lexical mapping')
 docs=[Counter(tokens(r.get('excerpt',''))) for r in records];df=Counter()
 for doc in docs:df.update(doc.keys())
 weights=[]
 for doc in docs:
  w={term:count*(math.log((1+len(docs))/(1+df[term]))+1) for term,count in doc.items()};norm=math.sqrt(sum(x*x for x in w.values())) or 1
  weights.append({t:x/norm for t,x in w.items()})
 edges=[];degree=Counter();aliases=defaultdict(list);broken=[];ambiguous=[]
 for r in records:
  for alias in {Path(r['path']).stem,r['path'],str(Path(r['path']).with_suffix(''))}:aliases[(r['root'],alias)].append(r['id'])
 for r in records:
  links=[('wiki_link',x) for x in r.get('wiki_links',[])]+[('markdown_link',x) for x in r.get('markdown_links',[])]
  for kind,target in links:
   if '://' in target or target.startswith(('#','mailto:')):continue
   target=target.split('#')[0]
   names=[target,str(Path(r['path']).parent/target)]
   hits=set(h for name in names for h in aliases.get((r['root'],name),[]))
   if len(hits)==1:
    dest=next(iter(hits));edges.append({'source':r['id'],'target':dest,'kind':kind});degree[r['id']]+=1;degree[dest]+=1
   elif not hits:broken.append({'source':r['id'],'target':target,'meaning':'unresolved in captured map; may exist outside policy or document cap'})
   else:ambiguous.append({'source':r['id'],'target':target,'candidates':sorted(hits)})
 lexical=[]
 for i in range(len(records)):
  for j in range(i+1,len(records)):
   score=sum(v*weights[j].get(k,0) for k,v in weights[i].items())
   if score>=threshold and score>0:lexical.append({'source':records[i]['id'],'target':records[j]['id'],'kind':'lexical_tfidf_cosine','score':round(score,6)})
 adjacency=defaultdict(set)
 for e in edges+lexical:adjacency[e['source']].add(e['target']);adjacency[e['target']].add(e['source'])
 seen=set();components=[]
 for r in records:
  if r['id'] in seen:continue
  stack=[r['id']];component=[]
  while stack:
   x=stack.pop()
   if x in seen:continue
   seen.add(x);component.append(x);stack.extend(adjacency[x]-seen)
  components.append(sorted(component))
 return {'snapshot_id':snapshot['snapshot_id'],'method':'explicit links plus excerpt-based TF-IDF cosine; not embeddings or validated semantic clusters','threshold':threshold,'documents':len(records),'document_cap_truncated':len(snapshot['records'])>len(records),'excerpt_truncation_present':any(r.get('excerpt_truncated') for r in records),'explicit_edges':edges,'lexical_candidates':sorted(lexical,key=lambda x:-x['score'])[:1000],'lexical_edges_truncated':len(lexical)>1000,'connected_components':components,'explicit_link_isolates':[r['id'] for r in records if not degree[r['id']]],'unresolved_links':broken,'ambiguous_links':ambiguous}

def compare_vectors(snapshot,model,vectors,threshold=.7):
 if not isinstance(model,str) or not model.strip() or not 0<=threshold<=1:raise ScopeError('model provenance and valid threshold required')
 if not isinstance(vectors,list) or not 1<=len(vectors)<=300:raise ScopeError('supply 1..300 vectors')
 known={r['id'] for r in snapshot['records']};seen=set();dim=None;normalized=[]
 for item in vectors:
  if item['id'] not in known or item['id'] in seen:raise ScopeError('unknown or duplicate note id')
  seen.add(item['id']);values=item['values']
  if not isinstance(values,list) or not 1<=len(values)<=8192 or (dim is not None and len(values)!=dim):raise ScopeError('inconsistent vector dimensions')
  if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in values):raise ScopeError('non-finite or nonnumeric vector')
  norm=math.hypot(*values)
  if not norm or not math.isfinite(norm):raise ScopeError('zero or invalid vector norm')
  dim=len(values);normalized.append((item['id'],[x/norm for x in values]))
 edges=[]
 for i,(name,a) in enumerate(normalized):
  for other,b in normalized[i+1:]:
   score=sum(x*y for x,y in zip(a,b))
   if score>=threshold:edges.append({'source':name,'target':other,'score':round(score,6),'kind':'imported_embedding_cosine'})
 return {'snapshot_id':snapshot['snapshot_id'],'model_as_supplied':model,'dimensions':dim,'vectors_generated_here':False,'threshold':threshold,'candidates':sorted(edges,key=lambda x:-x['score'])[:1000],'truncated':len(edges)>1000,'limit':'Similarity is not proof of equivalent meaning; supplied model label and vector provenance are not independently verified.'}

def timeline(snapshot,term):
 if not snapshot['coverage']['content_enabled']:raise ScopeError('text mode is required')
 if not term or len(term)>200:raise ScopeError('invalid term')
 pattern=re.compile(r'(?<!\w)'+re.escape(term)+r'(?!\w)',re.I);hits=[]
 for r in snapshot['records']:
  text=r.get('excerpt','');matches=list(pattern.finditer(text))
  if matches:hits.append({'id':r['id'],'declared_date':r['origin_date'],'date_provenance':r['date_provenance'],'matches_in_excerpt':len(matches),'contexts':[text[max(0,m.start()-120):m.end()+180] for m in matches[:5]],'excerpt_truncated':r.get('excerpt_truncated',False)})
 return {'snapshot_id':snapshot['snapshot_id'],'term':term,'hits':sorted(hits,key=lambda x:(x['declared_date'] is None,x['declared_date'] or '',x['id'])),'limit':'Dated usage contexts, not automatically detected definition changes or original authorship dates.'}
