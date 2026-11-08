#!/usr/bin/env python3
"""Local stdio MCP server: pure packet preparation/validation, no network or document writes."""
import json,sys
from jsonschema import ValidationError,validate
from review_packets import make_blind,make_cross,final_gate,ContractError

OBJECT={'type':'object'}
def arguments(properties):return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
TOOLS=[
 {'name':'prepare_blind','description':'Create a blind audit packet, compute the draft hash, and exclude standalone evidence/peer/editorial fields. Register must include the selected template and judge output contract.','inputSchema':arguments({'source':OBJECT})},
 {'name':'prepare_cross','description':'Require three distinct frozen blind judgments and revision-matched evidence, then compute the shared evidence digest and return the cross-examination packet.','inputSchema':arguments({'blind':OBJECT,'judgments':{'type':'array','items':OBJECT},'evidence':OBJECT})},
 {'name':'check_final','description':'Validate three cross judgments, matching draft/evidence identities, declared factual support, and five gate results. Returns accepted and reasons; does not prove empirical truth.','inputSchema':arguments({'cross':OBJECT,'judgments':{'type':'array','items':OBJECT},'gates':OBJECT})}]
FUNCTIONS={'prepare_blind':lambda a:make_blind(a['source']),'prepare_cross':lambda a:make_cross(a['blind'],a['judgments'],a['evidence']),'check_final':lambda a:final_gate(a['cross'],a['judgments'],a['gates'])}
for tool in TOOLS:tool['_meta']={'antigravity/alwaysLoad':True}
BY_NAME={t['name']:t for t in TOOLS}

class Server:
 def __init__(self):self.initialized=False;self.ready=False
 def handle(self,request):
  if not isinstance(request,dict) or request.get('jsonrpc')!='2.0' or not isinstance(request.get('method'),str):
   return {'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'Invalid request'}}
  method=request['method'];rid=request.get('id');params=request.get('params',{})
  def result(value):return {'jsonrpc':'2.0','id':rid,'result':value}
  def error(code,message):return {'jsonrpc':'2.0','id':rid,'error':{'code':code,'message':message}}
  if method=='notifications/initialized' and 'id' not in request:
   if self.initialized:self.ready=True
   return None
  if 'id' not in request:return None
  if not isinstance(params,dict):return error(-32602,'params must be an object')
  if method=='ping':return result({})
  if method=='initialize':
   if self.initialized:return error(-32600,'Already initialized')
   version=params.get('protocolVersion')
   version=version if version in ('2024-11-05','2025-03-26') else '2025-03-26'
   self.initialized=True
   return result({'protocolVersion':version,'capabilities':{'tools':{'listChanged':False}},'serverInfo':{'name':'ruth-review-packets','version':'0.3.0'}})
  if not self.ready:return error(-32000,'Initialize and send notifications/initialized first')
  if method=='tools/list':
   if params.get('cursor'):return error(-32602,'No cursor pages exist')
   return result({'tools':TOOLS})
  if method=='tools/call':
   name=params.get('name')
   if name not in BY_NAME:return error(-32602,'Unknown tool')
   try:
    args=params.get('arguments',{});validate(args,BY_NAME[name]['inputSchema'])
    value=FUNCTIONS[name](args)
    return result({'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False,separators=(',',':'))}],'isError':False})
   except (ValidationError,ContractError,KeyError,TypeError,ValueError,OSError) as exc:
    message=exc.message if isinstance(exc,ValidationError) else str(exc)
    return result({'content':[{'type':'text','text':'Packet validation failed: '+message}],'isError':True})
  return error(-32601,'Method not found')

 def dispatch(self,message):
  if isinstance(message,list):
   if not message:return {'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'Empty batch'}}
   if any(isinstance(x,dict) and x.get('method')=='initialize' for x in message):return {'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'initialize must not be batched'}}
   replies=[self.handle(x) for x in message];return [x for x in replies if x is not None] or None
  return self.handle(message)

def main():
 server=Server()
 for line in sys.stdin:
  try:response=server.dispatch(json.loads(line))
  except json.JSONDecodeError:response={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Parse error'}}
  if response is not None:sys.stdout.write(json.dumps(response,ensure_ascii=False,separators=(',',':'))+'\n');sys.stdout.flush()
if __name__=='__main__':main()
