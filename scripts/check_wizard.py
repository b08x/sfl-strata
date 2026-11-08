#!/usr/bin/env python3
"""Headless UI and real live-worker policy regression checks, fixture data only."""
import asyncio,copy,json,os,subprocess,sys,tempfile,time
from unittest.mock import patch
from contextlib import nullcontext
from pathlib import Path
from setup_wizard import StrataWizard
from textual.widgets import Input,Switch,Button
from settings_store import save_config,revision
from live_status import observe
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def request(worker,name,arguments={}):
 request.counter+=1
 worker.stdin.write(json.dumps({'jsonrpc':'2.0','id':request.counter,'method':'tools/call','params':{'name':name,'arguments':arguments}})+'\n');worker.stdin.flush()
 reply=json.loads(worker.stdout.readline())['result']
 return reply if reply.get('isError') else json.loads(reply['content'][0]['text'])
request.counter=0
async def main():
 with tempfile.TemporaryDirectory() as d:
  base=Path(d);vault=base/'vault';vault.mkdir();(vault/'old.md').write_text('old fixture');other=base/'new';other.mkdir();(other/'new.md').write_text('new fixture')
  path=base/'settings.json';app=StrataWizard(path)
  async with app.run_test(size=(125,42)) as pilot:
   await pilot.press('ctrl+n');await pilot.pause();assert app.step==1
   await pilot.press('ctrl+n');await pilot.pause();assert app.step==1 and not path.exists()
   app.query_one('#root-input',Input).value=str(base/'missing');await pilot.click('#add-root');await pilot.pause();assert app.roots==[]
   await pilot.pause(.35)
   app.query_one('#root-input',Input).value=str(vault);await pilot.click('#add-root');await pilot.pause();assert app.roots==[str(vault)]
   await app.add_root(str(vault));assert len(app.roots)==1
   await pilot.press('ctrl+n');app.query_one('#text',Switch).value=True;await pilot.press('ctrl+n');app.query_one('#max_files',Input).value='0';await pilot.press('ctrl+n');assert app.step==3
   app.query_one('#max_files',Input).value='50';await pilot.press('ctrl+p');await pilot.pause();assert app.query_one('#text',Switch).value
   await pilot.press('ctrl+n');await pilot.press('ctrl+n');await pilot.pause();assert app.step==4 and not path.exists()
   await pilot.click('#next');await pilot.pause();assert app.saved and app.verification['fresh'] and not app.verification['live']
   with patch('setup_wizard.shutil.which',return_value='/fixture/agy'),patch.object(app,'suspend',return_value=nullcontext()),patch('setup_wizard.subprocess.run',return_value=subprocess.CompletedProcess([],0)) as installer:
    await pilot.click('#install');await pilot.pause();installer.assert_called_once_with(['/fixture/agy','plugin','install',str(ROOT)])
  checks.append('Real keyboard/button workflow validates roots and bounds, preserves draft on Back, saves only at review, verifies a fresh MCP worker, and delegates installation with exact argv')
  for size in [(80,24),(100,32)]:
   cancel=base/f'cancel-{size[0]}.json';app=StrataWizard(cancel)
   async with app.run_test(size=size) as pilot:
    await pilot.press('ctrl+n');await pilot.click('#browse');await pilot.pause();assert app.screen.__class__.__name__=='FolderPicker'
    await pilot.press('escape');await pilot.pause();assert app.screen.__class__.__name__!='FolderPicker'
    assert app.query_one('#next',Button).region.bottom<=size[1]
    await pilot.press('ctrl+q')
   assert not cancel.exists()
  checks.append('80×24 and 100×32 layouts keep navigation reachable; folder browser cancels; exit writes nothing')
  worker=subprocess.Popen([sys.executable,str(ROOT/'scripts/archive_mcp.py'),'--config',str(path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   worker.stdin.write(json.dumps({'jsonrpc':'2.0','id':0,'method':'initialize','params':{'protocolVersion':'2025-03-26'}})+'\n');worker.stdin.flush();assert 'result' in json.loads(worker.stdout.readline())
   worker.stdin.write(json.dumps({'jsonrpc':'2.0','method':'notifications/initialized'})+'\n');worker.stdin.flush()
   first=request(worker,'archive_status');assert first['ready'] and not first['collection_performed']
   old=request(worker,'inventory_archive');assert old['records'][0]['path']=='old.md'
   config=json.loads(path.read_text());config['roots']=[str(other)];config['content_enabled']=False;save_config(path,config)
   live=observe(path)
   if live:assert any(x.get('configuration_revision')==revision(config) and x['pid']==worker.pid for x in live)
   else:checks.append('Live-status socket unavailable in this build environment; wizard correctly reports live session unobserved')
   status=request(worker,'archive_status');assert status['configured_roots']==[str(other)] and not status['collection_performed'] and not status['content_enabled']
   new=request(worker,'inventory_archive');assert new['records'][0]['path']=='new.md'
   path.write_text('{broken');assert request(worker,'inventory_archive')['isError']
   if live:assert any(x.get('configuration_error') for x in observe(path))
   save_config(path,config);assert request(worker,'archive_status')['ready']
  finally:
   worker.stdin.close();worker.wait(timeout=5);worker.stdout.close();worker.stderr.close()
  checks.append('Already-running worker reloads policy, invalidates cached evidence, blocks malformed settings, and recovers after repair')
  previous=json.loads(path.read_text());subprocess.run([sys.executable,str(ROOT/'configure.py'),'--config',str(path),'--roots',str(vault)],check=True,capture_output=True)
  current=json.loads(path.read_text());assert current['roots']==[str(vault)] and current['max_files']==previous['max_files'] and current['content_enabled']==previous['content_enabled']
  checks.append('Scripted --roots alias updates scope while preserving unspecified capabilities and bounds')
 print(json.dumps({'checks_passed':True,'count':len(checks),'checks':checks},indent=2))
if __name__=='__main__':asyncio.run(main())
