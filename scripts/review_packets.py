#!/usr/bin/env python3
"""Prepare revision-bound review packets; validate structure, never empirical truth."""
import argparse,hashlib,json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
IDENTITY=('task_id','document_revision','repository_revision','draft_sha256')
JUDGES={'ideational','interpersonal','textual'}
CLASSES={
'ideational':{'buried process (nominalization)','vague participant','missing material boundary (input/transform/output)','uncheckable circumstance','unmapped failure propagation','unverified mental speculation'},
'interpersonal':{'unbacked K1 claim (over-modality)','hedged verifiable fact (under-modality)','missing escape hatch','affective leakage / academic hedge','absent negative capability','unconfessed euphemism'},
 'textual':{'orphaned theme / broken New->Given chain','missing quantitative cohesive tie','decorative/unanchored circumstance','unsupported logical connective','genre-staging / register violation'}}
class ContractError(ValueError):pass

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def draft_hash(text):return hashlib.sha256(text.encode()).hexdigest()
def validate(kind,value):
    schema=json.loads((ROOT/f'schemas/{kind}.schema.json').read_text())
    Draft202012Validator(schema).validate(value)
    return value

def same_identity(a,b):
    if any(a[k]!=b[k] for k in IDENTITY):raise ContractError('stale or mismatched task/document/repository/draft identity')

def make_blind(source):
    # Explicit allowlist: standalone evidence, peer findings and decisions are never copied.
    packet={k:source[k] for k in ('task_id','document_revision','repository_revision','draft','register')}
    packet.update(phase='blind',draft_sha256=draft_hash(packet['draft']))
    return validate('blind-packet',packet)

def check_judgment(j,packet,phase):
    validate('judgment',j);same_identity(packet,j)
    if j['phase']!=phase:raise ContractError('wrong judgment phase')
    if phase=='blind':
        if j['verdict'] not in ('PROVISIONAL','BLOCKED') or j['evidence_sha256'] is not None:
            raise ContractError('blind audit cannot approve or bind unseen evidence')
    else:
        if j['evidence_sha256']!=packet['evidence_sha256']:raise ContractError('stale evidence digest')
        if j['verdict']=='PROVISIONAL':raise ContractError('cross verdict cannot be provisional')
    ids=set()
    for f in j['findings']:
        if f['finding_id'] in ids:raise ContractError('duplicate finding ID within a judgment')
        ids.add(f['finding_id'])
        if f['claim'] not in packet['draft']:raise ContractError('finding quote is not in the frozen draft')
        if f['problem_class'] not in CLASSES[j['judge']]:raise ContractError('problem class belongs to another judge')
        expected=' -> '.join([f['claim'],f['problem_class'],f['evidence_needed'],f['proposed_rewrite']])
        if f['signature'].replace(' → ',' -> ')!=expected:raise ContractError('finding signature mismatch')
        if phase=='blind' and (f['disposition']!='raised' or f['evidence_refs']):raise ContractError('blind finding must be raised without broker evidence refs')
        if phase=='cross_examination' and f['disposition']=='raised':raise ContractError('cross finding lacks disposition')
        if j['verdict']=='PASS' and f['severity']=='blocking' and f['disposition'] in ('sustained','deadlock'):
            raise ContractError('PASS with active blocking finding')
    if j['verdict']=='PASS' and (j['status']!='COMPLETE' or j['blockers']):raise ContractError('PASS with blockers')
    return j

def check_roster(judgments,packet,phase):
    if len(judgments)!=3 or {j.get('judge') for j in judgments}!=JUDGES:raise ContractError('exactly three distinct metafunction judges required')
    for j in judgments:check_judgment(j,packet,phase)

def check_evidence(e,packet):
    validate('evidence-packet',e);same_identity(packet,e)
    claim_ids=[c['claim_id'] for c in e['claims']]
    if len(claim_ids)!=len(set(claim_ids)):raise ContractError('duplicate evidence claim ID')
    ids=[x['id'] for x in e['evidence']]
    if len(ids)!=len(set(ids)):raise ContractError('duplicate evidence IDs')
    for claim in e['claims']:
        if not set(claim['evidence_refs'])<=set(ids):raise ContractError('unknown claim evidence reference')
        if claim['classification']=='supported' and not claim['evidence_refs']:raise ContractError('supported claim has no evidence reference')
    if e['status']=='COMPLETE':
        if e['blockers'] or not e['coverage']['checked'] or e['coverage']['unresolved_ranges']:
            raise ContractError('complete evidence packet has coverage blockers')
        if e['snapshot']['freshness']!='current' or e['snapshot']['source_revision']!=e['repository_revision'] or e['snapshot']['id'].lower() in ('unknown','pending','stale'):
            raise ContractError('complete evidence packet lacks current archive snapshot identity')
        if not all(q['pages_complete'] for q in e['queries']):raise ContractError('complete evidence packet has unfinished pagination')
        if not e['queries'] or not e['evidence']:raise ContractError('complete evidence packet is empty')
        if not any(q['tool'].split('__')[-1].split('/')[-1]=='inventory_archive' or q['tool'].endswith('inventory_archive') for q in e['queries']):raise ContractError('coverage call is missing from query log')
        if e['coverage']['state']!='clean' and not e['coverage']['fallback']:raise ContractError('coverage gap lacks source fallback')
    return e

def make_cross(blind,judgments,evidence):
    validate('blind-packet',blind)
    if draft_hash(blind['draft'])!=blind['draft_sha256']:raise ContractError('draft hash mismatch')
    check_roster(judgments,blind,'blind');check_evidence(evidence,blind)
    packet={**blind,'phase':'cross_examination','blind_judgments':judgments,'evidence_packet':evidence,'evidence_sha256':digest(evidence)}
    return validate('cross-packet',packet)

def final_gate(packet,judgments,gates):
    validate('cross-packet',packet)
    # Reconstruct to check all original bindings rather than trusting an edited cross packet.
    blind={k:v for k,v in packet.items() if k not in ('blind_judgments','evidence_packet','evidence_sha256')};blind['phase']='blind'
    rebuilt=make_cross(blind,packet['blind_judgments'],packet['evidence_packet'])
    if rebuilt['evidence_sha256']!=packet['evidence_sha256']:raise ContractError('cross packet evidence changed')
    check_roster(judgments,packet,'cross_examination')
    ids={e['id'] for e in packet['evidence_packet']['evidence']}
    for j in judgments:
        for f in j['findings']:
            if not set(f['evidence_refs'])<=ids:raise ContractError('judge cites unknown evidence')
    validate('gates',gates);same_identity(packet,gates)
    if gates['evidence_sha256']!=packet['evidence_sha256']:raise ContractError('gate evidence mismatch')
    reasons=[]
    e=packet['evidence_packet']
    if e['tier']=='Scout':reasons.append('Scout evidence is provisional')
    if any(c['claim_type'] in ('negative','exhaustive') and c['treatment']!='omitted' for c in e['claims']) and e['tier']!='Auditor':reasons.append('negative or exhaustive retained claim requires Auditor tier')
    if packet['evidence_packet']['status']!='COMPLETE':reasons.append('evidence broker is blocked')
    if any(j['verdict']!='PASS' or j['status']!='COMPLETE' for j in judgments):reasons.append('one or more judges did not pass')
    if any(g['status'] not in ('PASS','NOT_APPLICABLE') for g in gates['gates'].values()):reasons.append('one or more linguistic gates remain open')
    if any(c['treatment']=='asserted' and c['classification']!='supported' for c in packet['evidence_packet']['claims']):reasons.append('unsupported assertion remains')
    return {'accepted':not reasons,'identity':{k:packet[k] for k in IDENTITY},'evidence_sha256':packet['evidence_sha256'],'reasons':reasons,'scope':'packet consistency and declared gate state; not empirical truth or runtime permission enforcement'}

def read(p):return json.loads(Path(p).read_text())
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='mode',required=True)
    b=sub.add_parser('blind');b.add_argument('input')
    c=sub.add_parser('cross');c.add_argument('blind');c.add_argument('evidence');c.add_argument('judgments',nargs=3)
    f=sub.add_parser('final');f.add_argument('cross');f.add_argument('gates');f.add_argument('judgments',nargs=3)
    args=parser.parse_args()
    try:
        if args.mode=='blind':result=make_blind(read(args.input))
        elif args.mode=='cross':result=make_cross(read(args.blind),[read(p) for p in args.judgments],read(args.evidence))
        else:result=final_gate(read(args.cross),[read(p) for p in args.judgments],read(args.gates))
    except (ValueError,KeyError) as error:parser.exit(2,str(error)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if args.mode=='final' and not result['accepted']:raise SystemExit(1)
if __name__=='__main__':main()
