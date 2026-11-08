"""The field notebook: an explicit-scope Antigravity setup interface."""
import asyncio,copy,json,sys,subprocess,shutil
from pathlib import Path
from rich.text import Text
from textual.app import App,ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal,Vertical,VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static,Label,Button,Input,Switch,ListView,ListItem,DirectoryTree,ContentSwitcher,Footer
from settings_store import default_path,save_config,validate,revision
from live_status import observe

ROOT=Path(__file__).resolve().parents[1]
STEPS=[('Orientation','A notebook, before the dig'),('Archive roots','Choose the ground'),('Capabilities','Decide what is observable'),('Boundaries','Keep the excavation bounded'),('Review & connect','Make the policy concrete')]

class Folders(DirectoryTree):
 def filter_paths(self,paths):return [p for p in paths if p.is_dir() and not p.is_symlink() and not p.name.startswith('.')]

class FolderPicker(ModalScreen):
 BINDINGS=[('escape','dismiss(None)','Cancel')]
 def __init__(self,start):super().__init__();self.selected=Path(start)
 def compose(self):
  with Vertical(id='picker'):
   yield Static('CHOOSE AN ARCHIVE DIRECTORY',classes='eyebrow')
   yield Static('Expand a branch, select a directory, then use this folder.',classes='muted')
   yield Folders(self.selected,id='tree')
   yield Static(Text(str(self.selected)),id='selected-path')
   with Horizontal(classes='button-row'):
    yield Button('Cancel',id='cancel-picker');yield Button('Use this folder',id='choose-folder',variant='primary')
 def on_directory_tree_directory_selected(self,event):self.selected=event.path;self.query_one('#selected-path',Static).update(Text(str(event.path)))
 def on_button_pressed(self,event):
  if event.button.id=='choose-folder':self.dismiss(str(self.selected))
  elif event.button.id=='cancel-picker':self.dismiss(None)

class StrataWizard(App):
 ENABLE_COMMAND_PALETTE=False
 TITLE='SFL STRATA · Field notebook'
 SUB_TITLE='Antigravity workspace preparation'
 BINDINGS=[Binding('ctrl+q','quit','Exit'),Binding('ctrl+n','next','Continue'),Binding('ctrl+p','back','Back')]
 CSS='''
 VerticalScroll { scrollbar-background: #E3DBC8; scrollbar-color: #C9B8A0; scrollbar-color-hover: #B5654A; scrollbar-color-active: #B5654A; }
 Screen { background: #EDE6D6; color: #2A2420; }
 #masthead { height: 5; padding: 1 3; background: #2A2420; color: #EDE6D6; }
 #brand { color: #D6A77B; text-style: bold; }
 #subtitle { color: #BEB3A1; }
 #body { height: 1fr; }
 #rail { width: 29; padding: 2 2; background: #E3DBC8; border-right: solid #C9B8A0; }
 .step { height: auto; margin-bottom: 1; padding: 1; color: #7B7162; }
 .step.active { background: #B5654A; color: #FFF7E8; text-style: bold; }
 .step.done { color: #52634C; }
 #rail-note { margin-top: 2; color: #7B7162; height: auto; }
 #workspace { padding: 2 3 0 3; width: 1fr; }
 #folio { color: #B5654A; height: 1; text-style: bold; }
 #title { text-style: bold; height: 2; margin-top: 1; }
 #deck { color: #6A5D4D; height: auto; margin-bottom: 1; }
 ContentSwitcher { height: 1fr; }
 .page { height: 1fr; }
 .eyebrow { color: #A2553E; text-style: bold; height: auto; margin-bottom: 1; }
 .intro { height: auto; margin-bottom: 2; }
 .card { background: #E3DBC8; border: round #C9B8A0; padding: 1 2; height: auto; margin-bottom: 1; }
 .card-title { text-style: bold; height: auto; margin-bottom: 1; }
 .muted { color: #786D5D; height: auto; }
 Input { background: #F8F2E6; color: #2A2420; border: tall #C9B8A0; }
 Input:focus { border: tall #B5654A; }
 .path-row { height: 3; }
 #root-input { width: 1fr; }
 Button { background: #E3DBC8; color: #2A2420; border: tall #C9B8A0; min-width: 12; }
 Button:focus { text-style: bold; border: tall #B5654A; }
 Button.-primary { background: #B5654A; color: #FFF7E8; border: tall #B5654A; }
 Button:hover { background: #D2C7B4; }
 #roots { height: 9; background: #F8F2E6; border: round #C9B8A0; margin-top: 1; }
 ListItem { padding: 0 1; color: #2A2420; }
 ListView:focus > ListItem.--highlight { background: #526B73; color: #FFF7E8; }
 .button-row { height: 3; margin-top: 1; }
 .button-row Button { margin-right: 1; }
 .capability { height: auto; min-height: 6; background: #E3DBC8; border: round #C9B8A0; padding: 1; margin-bottom: 1; }
 .cap-copy { width: 1fr; height: auto; padding-left: 1; }
 Switch { background: #C9B8A0; }
 Switch.-on { background: #52634C; }
 .bound { height: 4; }
 .bound Label { width: 1fr; padding-top: 1; }
 .bound Input { width: 16; }
 #review { height: auto; padding: 1 2; background: #E3DBC8; border: round #C9B8A0; }
 #message { height: auto; min-height: 1; color: #A8453A; margin-top: 1; }
 #message.success { color: #52634C; }
 #navigation { height: 5; padding-top: 1; }
 #progress { width: 1fr; color: #786D5D; padding: 1 0; }
 #navigation Button { margin-left: 1; }
 Footer { background: #2A2420; color: #EDE6D6; }
 Footer > .footer--key { background: #2A2420; color: #D6A77B; }
 #picker { width: 85%; height: 85%; background: #EDE6D6; border: round #B5654A; padding: 1 2; }
 FolderPicker { align: center middle; background: #2A2420 60%; }
 #tree { height: 1fr; background: #F8F2E6; color: #2A2420; }
 #selected-path { height: auto; margin-top: 1; }
 .compact #rail { display: none; }
 .compact #workspace { padding: 1 2 0 2; }
 .compact #masthead { height: 4; padding: 1 2 0 2; }
 .compact #title { margin-top: 0; }
 '''
 def __init__(self,config_path=None):
  super().__init__();self.path=Path(config_path or default_path()).expanduser().absolute();self.step=0;self.saved=False;self.error='';self.verification={}
  self.defaults=json.loads((ROOT/'config/workstation.json').read_text())
  try:
   if self.path.is_symlink():raise ValueError('Symlinked settings file')
   self.config=json.loads(self.path.read_text()) if self.path.exists() else copy.deepcopy(self.defaults)
   validate(self.config)
  except (OSError,ValueError,KeyError,TypeError) as error:
   self.config=copy.deepcopy(self.defaults);self.error=f'Existing settings could not be loaded: {error}. Saving will explicitly replace them.'
  self.roots=list(self.config['roots']);self.initial=copy.deepcopy(self.config)
 def compose(self)->ComposeResult:
  with Vertical(id='masthead'):
   yield Static('S F L   S T R A T A     /     FIELD NOTEBOOK',id='brand')
   yield Static('Records uncertainty. Traces history. Begins with explicit scope.',id='subtitle')
  with Horizontal(id='body'):
   with Vertical(id='rail'):
    yield Static('PREPARE THE EXPEDITION',classes='eyebrow')
    for i,(name,_) in enumerate(STEPS):yield Static(f'{i+1:02}   {name}',id=f'step-{i}',classes='step')
    yield Static('R.U.T.H.\nRecords Uncertainty,\nTraces History\n\nAntigravity CLI plugin\nv0.3.0',id='rail-note')
   with Vertical(id='workspace'):
    yield Static('',id='folio');yield Static('',id='title');yield Static('',id='deck')
    with ContentSwitcher(initial='page-0',id='pages'):
     with VerticalScroll(id='page-0',classes='page'):
      yield Static('Your archive is a landscape.\nStart by marking the ground you want to revisit.',classes='intro')
      with Vertical(classes='card'):
       yield Static('01  Choose the archive',classes='card-title')
       yield Static('Select existing directories. Folder selection does not inventory your files.',classes='muted')
      with Vertical(classes='card'):
       yield Static('02  Set the instruments',classes='card-title')
       yield Static('Metadata is the starting point. Note text, Git dates and a current host observation are separate choices.',classes='muted')
      with Vertical(classes='card'):
       yield Static('03  Verify the connection',classes='card-title')
       yield Static('Review exact settings, save atomically, and compare policy revisions with running workers.',classes='muted')
      yield Static(Text('SETTINGS\n'+str(self.path)),classes='muted')
     with VerticalScroll(id='page-1',classes='page'):
      yield Static('EXPLICIT ROOTS',classes='eyebrow')
      with Horizontal(classes='path-row'):
       yield Input(placeholder='~/Workspace/notes',id='root-input')
       yield Button('Browse…',id='browse');yield Button('Add root',id='add-root')
      yield ListView(*[ListItem(Label(Text(p))) for p in self.roots],id='roots')
      with Horizontal(classes='button-row'):yield Button('Remove selected',id='remove-root')
      yield Static('Add several roots if ideas live in several places. Symlinks inside the archive are not followed. Nothing is collected during setup.',classes='muted')
     with VerticalScroll(id='page-2',classes='page'):
      for ident,title,description,key in [('text','Note text','Read bounded UTF-8 notes and excerpts when requested. Enables lexical mapping and term contexts.','content_enabled'),('git','Git history','Read bounded commit dates for a selected note. Commit dates do not establish when an idea began.','git_history_enabled'),('host','Current host snapshot','One explicit observation of load, uptime and process-name counts. No background monitor or usage history.','host_usage_enabled')]:
       with Horizontal(classes='capability'):
        yield Switch(self.config[key],id=ident)
        with Vertical(classes='cap-copy'):
         yield Static(title,classes='card-title');yield Static(description,classes='muted')
     with VerticalScroll(id='page-3',classes='page'):
      yield Static('COLLECTION BUDGET',classes='eyebrow')
      for key,title in [('max_files','Maximum files · 1–10,000'),('max_dirs','Maximum directories · 1–20,000'),('max_file_bytes','Bytes per file · up to 1 MiB'),('max_total_bytes','Total content bytes · up to 128 MiB'),('max_excerpt_chars','Excerpt characters · up to 32,000')]:
       with Horizontal(classes='bound'):
        yield Label(title);yield Input(str(self.config[key]),type='integer',id=key)
      yield Static('EXCLUSIONS & FORMATS',classes='eyebrow')
      yield Static(Text('Note formats: '+', '.join(self.config['extensions'])+'\nHidden paths are skipped.\nExcluded names: '+', '.join(self.config['exclude_names'])+'\nExcluded patterns: '+', '.join(self.config['exclude_globs'])),classes='muted')
     with VerticalScroll(id='page-4',classes='page'):
      yield Static('POLICY BEFORE COLLECTION',classes='eyebrow')
      yield Static('',id='review')
      yield Static('Save & verify writes settings and requests status only. The archive inventory remains a separate, explicit agent operation.',classes='muted')
    yield Static(self.error,id='message')
    with Horizontal(id='navigation'):
     yield Static('',id='progress');yield Button('Back',id='back');yield Button('Install plugin',id='install');yield Button('Continue →',id='next',variant='primary')
  yield Footer()
 def on_mount(self):self.show_step()
 def on_resize(self,event):self.set_class(event.size.width<100,'compact')
 def show_step(self):
  for i in range(len(STEPS)):
   item=self.query_one(f'#step-{i}');item.set_class(i==self.step,'active');item.set_class(i<self.step,'done')
  name,deck=STEPS[self.step]
  self.query_one('#folio',Static).update(f'PREPARATION  /  {self.step+1:02} OF 05')
  self.query_one('#title',Static).update(name)
  self.query_one('#deck',Static).update(deck)
  self.query_one('#pages',ContentSwitcher).current=f'page-{self.step}'
  self.query_one('#message',Static).set_class(self.saved,'success')
  self.query_one('#progress',Static).update('Saved · verified below' if self.saved else 'Draft · nothing collected')
  self.query_one('#back',Button).disabled=self.step==0 or self.saved
  self.query_one('#install',Button).display=self.saved
  self.query_one('#next',Button).label='Close' if self.saved else 'Save & verify' if self.step==4 else 'Continue →'
  self.query_one('#next',Button).disabled=False
  if self.step==4:self.review()
 def message(self,value):self.query_one('#message',Static).update(Text(value))
 def draft(self):
  value=copy.deepcopy(self.config);value['roots']=self.roots.copy()
  for ident,key in [('text','content_enabled'),('git','git_history_enabled'),('host','host_usage_enabled')]:value[key]=self.query_one('#'+ident,Switch).value
  for key in ('max_files','max_dirs','max_file_bytes','max_total_bytes','max_excerpt_chars'):
   try:value[key]=int(self.query_one('#'+key,Input).value)
   except ValueError:raise ValueError(key+' requires a whole number')
  validate(value);return value
 def review(self):
  value=self.draft();changed=[k for k in value if value[k]!=self.initial.get(k)]
  modes='\n'.join(f"  {label}: {'enabled' if value[key] else 'off'}" for label,key in [('Note text','content_enabled'),('Git history','git_history_enabled'),('Host snapshot','host_usage_enabled')])
  text=(self.error+'\n\n' if self.error else '')+'SETTINGS FILE\n'+str(self.path)+'\n\nARCHIVE ROOTS\n'+'\n'.join('  '+p for p in self.roots)+'\n\nCAPABILITIES\n'+modes+f"\n\nBOUNDS\n  {value['max_files']:,} files · {value['max_dirs']:,} directories\n  {value['max_file_bytes']:,} bytes/file · {value['max_total_bytes']:,} bytes total\n  {value['max_excerpt_chars']:,} excerpt characters\n\nChanged fields: "+(', '.join(changed) or 'none')
  self.query_one('#review',Static).update(Text(text))
 async def add_root(self,path=None):
  raw=path or self.query_one('#root-input',Input).value
  try:
   if not raw.strip():raise ValueError('Choose or enter a directory first.')
   selected=Path(raw).expanduser().resolve(strict=True)
   if not selected.is_dir():raise ValueError('Archive roots must be directories.')
   if str(selected) in self.roots:raise ValueError('That directory is already selected.')
   self.roots.append(str(selected));await self.query_one('#roots',ListView).append(ListItem(Label(Text(str(selected)))))
   self.query_one('#root-input',Input).value='';self.message('Root added. No files read.')
  except (OSError,ValueError) as error:self.message(str(error))
 async def chosen(self,path):
  if path:await self.add_root(path)
 async def on_input_submitted(self,event):
  if event.input.id=='root-input':await self.add_root()
 async def on_button_pressed(self,event):
  ident=event.button.id
  if ident=='next':await self.action_next()
  elif ident=='install':
   executable=shutil.which('agy')
   if not executable:self.message('agy is not on PATH. Install Antigravity CLI, then use the command shown above.');return
   try:
    with self.suspend():result=subprocess.run([executable,'plugin','install',str(ROOT)])
    self.message('Plugin installed. Start a new session: agy --agent sfl-strata-coordinator' if result.returncode==0 else f'Antigravity installer exited {result.returncode}; settings remain saved.')
   except OSError as error:self.message(str(error))
  elif ident=='back':self.action_back()
  elif ident=='add-root':await self.add_root()
  elif ident=='browse':self.push_screen(FolderPicker(Path.home()),self.chosen)
  elif ident=='remove-root':
   view=self.query_one('#roots',ListView)
   if view.index is not None and self.roots:
    index=view.index;self.roots.pop(index);await view.children[index].remove();self.message('Root removed from draft.')
 async def action_next(self):
  if self.saved:self.exit();return
  try:
   if self.step==1 and not self.roots:raise ValueError('Select at least one existing archive directory.')
   if self.step>=3:self.draft()
   if self.step==4:
    self.query_one('#next',Button).disabled=True;self.message('Saving policy and checking worker revisions…')
    value=self.draft();result=await asyncio.to_thread(self.save_and_verify,value)
    self.saved=True;self.verification=result
    lines=['SAVED  '+str(self.path),'Revision  '+result['revision'][:16],'Read-back verified · no archive collection performed.']
    if result['fresh']:lines.append('FRESH WORKER  Status verified; configured roots loaded.')
    else:lines.append('FRESH WORKER  Unverified: '+result['fresh_error'])
    if result['live']:
     for item in result['live']:lines.append(f"LIVE WORKER  PID {item['pid']} · "+('policy revision matches' if item.get('configuration_revision')==result['revision'] else 'revision mismatch or invalid settings'))
    else:lines.append('LIVE SESSION  Not observed. Reconnect Antigravity once if upgrading an older worker.')
    lines.extend(['','NEXT','agy plugin install '+str(ROOT),'agy --agent sfl-strata-coordinator','','Ask R.U.T.H. to check archive_status, then explicitly inventory the configured roots.'])
    self.show_step();self.query_one('#review',Static).update(Text('\n'.join(lines)));self.message('Settings saved. Connection results are shown above.');return
   self.step+=1;self.message('');self.show_step()
  except (OSError,ValueError,KeyError,TypeError) as error:
   self.message(str(error));self.query_one('#next',Button).disabled=False
 def action_back(self):
  if self.saved:return
  self.step=max(0,self.step-1);self.message('');self.show_step()
 def save_and_verify(self,value):
  validate(value);save_config(self.path,value);readback=json.loads(self.path.read_text())
  if revision(readback)!=revision(value):raise ValueError('Settings changed during read-back; reopen setup.')
  result={'revision':revision(value),'live':[],'fresh':False,'fresh_error':''}
  try:result['live']=observe(self.path)
  except (OSError,ValueError):pass
  requests=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26'}},{'jsonrpc':'2.0','method':'notifications/initialized'},{'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'archive_status','arguments':{}}}]
  try:
   process=subprocess.run([sys.executable,str(ROOT/'scripts/archive_mcp.py'),'--config',str(self.path)],input=''.join(json.dumps(r)+'\n' for r in requests),capture_output=True,text=True,timeout=10,check=True)
   replies=[json.loads(line) for line in process.stdout.splitlines()];reply=next(r for r in replies if r.get('id')==2)
   if reply['result'].get('isError'):raise ValueError(reply['result']['content'][0]['text'])
   status=json.loads(reply['result']['content'][0]['text']);result['fresh']=status['configuration_revision']==result['revision'] and status['ready'] and not status['collection_performed']
  except (OSError,ValueError,KeyError,StopIteration,subprocess.SubprocessError) as error:result['fresh_error']=str(error)
  return result
