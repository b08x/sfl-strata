#!/usr/bin/env python3
"""Regression checks for blindness, identity, evidence binding, and final review gates."""
from copy import deepcopy
import json
from jsonschema import ValidationError
import review_packets as r

checks=[]
def reject(label,fn):
    try:fn()
    except (r.ContractError,ValidationError):checks.append(label)
    else:raise AssertionError(label+' was accepted')

source={'task_id':'fixture-001','document_revision':'r1','repository_revision':'fixture-commit','draft':'Worker parses JSON into records.','register':{'field':'fixture worker','tenor':'technical peer','mode':'Markdown','genre':'feature-description','dial':'Compressed','template':'Synthetic fixture template, not a production measurement.','task_type':'audit','output_contract':{'format':'JSON'}},'evidence_packet':{'secret':'withhold'},'peer_findings':['withhold'],'editorial_decisions':['withhold']}
blind=r.make_blind(source)
assert not set(blind)&{'evidence_packet','peer_findings','editorial_decisions'}
checks.append('Blind builder strips standalone evidence, peer findings, and editorial decisions')
anchor={k:blind[k] for k in r.IDENTITY}
judgments=[{**anchor,'phase':'blind','judge':j,'evidence_sha256':None,'status':'COMPLETE','verdict':'PROVISIONAL','findings':[],'summary':{'counting_method':'synthetic fixture: one sentence'},'blockers':[]} for j in sorted(r.JUDGES)]
evidence={**anchor,'phase':'evidence','status':'COMPLETE','collection':'fixture','tier':'Verify','snapshot':{'id':'fixture-s1','freshness':'current','source_revision':'fixture-commit','observed_at':'2026-01-01T00:00:00Z'},'scope':['fixture/worker.py'],'queries':[{'tool':'inventory_archive','arguments':{'paths':['fixture/worker.py']},'pages_complete':True,'pagination':{'has_more':False}}],'coverage':{'checked':True,'paths':['fixture/worker.py'],'state':'clean','fallback':[],'unresolved_ranges':[]},'evidence':[{'id':'ev-1','kind':'source','location':'fixture/worker.py:1','excerpt':'Synthetic source fixture, not a runtime observation.','claim_ids':['c-1']}],'claims':[{'claim_id':'c-1','claim_type':'positive','classification':'supported','treatment':'asserted','evidence_refs':['ev-1']}],'assumptions':[],'blockers':[]}
cross=r.make_cross(blind,judgments,evidence)
reviews=[{**j,'phase':'cross_examination','verdict':'PASS','evidence_sha256':cross['evidence_sha256']} for j in judgments]
gates={**anchor,'evidence_sha256':cross['evidence_sha256'],'gates':{k:{'status':'PASS','reason':'Synthetic contract fixture; no empirical review claimed.'} for k in ['process_coverage','modality','cohesion','connectives','negative_capability']}}
assert r.final_gate(cross,reviews,gates)['accepted']
checks.append('Matching three-judge review and five gates accepted structurally')
bad=deepcopy(judgments);bad[0]['verdict']='PASS'
reject('Blind PASS rejected',lambda:r.make_cross(blind,bad,evidence))
bad=deepcopy(judgments);bad[0]['document_revision']='r0'
reject('Stale document review rejected',lambda:r.make_cross(blind,bad,evidence))
bad=deepcopy(judgments);bad[0]['repository_revision']='old-commit'
reject('Stale repository review rejected',lambda:r.make_cross(blind,bad,evidence))
reject('Missing judge rejected',lambda:r.make_cross(blind,judgments[:2],evidence))
reject('Duplicate judge rejected',lambda:r.make_cross(blind,[judgments[0]]*3,evidence))
bad=deepcopy(evidence);bad['coverage']['unresolved_ranges']=['fixture/worker.py:1-3']
reject('Unresolved coverage cannot be COMPLETE',lambda:r.make_cross(blind,judgments,bad))
bad=deepcopy(evidence);bad['queries'][0]['pages_complete']=False
reject('Incomplete pagination cannot be COMPLETE',lambda:r.make_cross(blind,judgments,bad))
bad=deepcopy(evidence);bad['snapshot']['freshness']='unknown'
reject('Unknown archive freshness cannot be COMPLETE',lambda:r.make_cross(blind,judgments,bad))
bad=deepcopy(cross);bad['draft']='Different text'
reject('Changed draft text invalidates its hash',lambda:r.final_gate(bad,reviews,gates))
bad=deepcopy(reviews);bad[0]['evidence_sha256']='0'*64
reject('Cross review of another evidence packet rejected',lambda:r.final_gate(cross,bad,gates))
bad=deepcopy(evidence);bad['claims'][0]['classification']='unsupported';cx=r.make_cross(blind,judgments,bad)
rv=[{**j,'evidence_sha256':cx['evidence_sha256']} for j in reviews];gs={**gates,'evidence_sha256':cx['evidence_sha256']}
assert not r.final_gate(cx,rv,gs)['accepted']
checks.append('Unsupported asserted claim blocks final acceptance')
bad=deepcopy(gates);bad['gates']['modality']['status']='REVISE'
assert not r.final_gate(cross,reviews,bad)['accepted']
checks.append('Open linguistic gate blocks final acceptance')
bad=deepcopy(evidence);bad['status']='BLOCKED';bad['blockers']=['archive source unavailable'];cx=r.make_cross(blind,judgments,bad)
rv=[{**j,'evidence_sha256':cx['evidence_sha256']} for j in reviews];gs={**gates,'evidence_sha256':cx['evidence_sha256']}
assert not r.final_gate(cx,rv,gs)['accepted']
checks.append('Unavailable broker cannot produce final acceptance')
bad=deepcopy(reviews);quote=source['draft'];problem='vague participant';need='Exact worker identity';rewrite='Use the verified worker name.'
bad[0]['findings']=[{'finding_id':'f-1','claim_id':'c-1','position':'sentence 1','claim':quote,'problem_class':problem,'evidence_needed':need,'proposed_rewrite':rewrite,'signature':' -> '.join([quote,problem,need,rewrite]),'disposition':'deadlock','severity':'blocking','evidence_refs':[]}]
reject('Blocking deadlock cannot PASS',lambda:r.final_gate(cross,bad,gates))
bad=deepcopy(evidence);bad['tier']='Scout';cx=r.make_cross(blind,judgments,bad)
rv=[{**j,'evidence_sha256':cx['evidence_sha256']} for j in reviews];gs={**gates,'evidence_sha256':cx['evidence_sha256']}
assert not r.final_gate(cx,rv,gs)['accepted']
checks.append('Scout tier cannot yield final acceptance')
bad=deepcopy(evidence);bad['claims'][0]['claim_type']='negative';cx=r.make_cross(blind,judgments,bad)
rv=[{**j,'evidence_sha256':cx['evidence_sha256']} for j in reviews];gs={**gates,'evidence_sha256':cx['evidence_sha256']}
assert not r.final_gate(cx,rv,gs)['accepted']
checks.append('Retained negative claim needs Auditor tier')
print(json.dumps({'checks_passed':True,'count':len(checks),'checks':checks,'scope':'synthetic packet fixtures; no LLM or archive connection'},indent=2))
