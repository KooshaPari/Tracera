#!/usr/bin/env python3
"""Deterministic projections of frozen canonical records; no product evaluator."""
import pathlib,json,csv,hashlib,html,sys
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Preformatted
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
D=pathlib.Path(__file__).resolve().parents[1]
r=json.loads((D/'owner-records.json').read_text());s=json.loads((D/'snapshot.json').read_text())
md=['# Tracera - State & Forward Docket','',f"Snapshot `{r['snapshot_id']}` | Generated {r['generated_at']}",'',f"Exact candidate `{r['candidate']['candidate_sha']}`; baseline `{r['source_sha']}`.",'','Full product acceptance: NOT ESTABLISHED. The selected-assessment reducer is not full product completion.','']
for x in r['sections']:md+=['## '+x['title'],'',x['text'],'']
md+=['## Goal tree and unfinished obligations','']
for g in r['goals']:
 md+=['### '+g['id']+' '+g['title'],'',g['expected'],'',f"Status: {g['status']} | Review: {g['review']} | Owner: {g['owner']}",'',f"Location: {g['location']}; source baseline {r['source_sha']} unless Q1 receipt states candidate.",'',f"Closure: {g['closure_oracle']}",'',f"Negative control: {g['negative_verification']}",'',f"Dependencies: {', '.join(g['dependencies']) or 'none defined'}; effort: {g['effort']}",'']
md+=['## Publication receipt','',json.dumps(r['publication'],indent=2),'','## Integrity limits','','Input hashes identify bytes, not truth or authorship. Inputs, canonical records and renderer are pinned in views/build.json; that receipt excludes itself to avoid a hash cycle. Output PDF and Markdown derive from these same records. Historical audit input records remain immutable.','']
(D/'ASSESSMENT.md').write_text('\n'.join(md))
# Offline HTML uses same paragraphs and goal fields.
blocks=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Tracera State & Forward Docket</title><style>body{font:17px/1.55 system-ui;max-width:1000px;margin:40px auto;padding:0 25px;color:#183047}h1,h2{color:#145e66}article{border-top:1px solid #bbc;padding:20px 0}pre{white-space:pre-wrap}a{color:#135e8d}</style><h1>Tracera State & Forward Docket</h1>']
for line in md:
 if line.startswith('### '):blocks.append('<h3>'+html.escape(line[4:])+'</h3>')
 elif line.startswith('## '):blocks.append('<h2>'+html.escape(line[3:])+'</h2>')
 elif line and not line.startswith('# '):blocks.append('<p>'+html.escape(line)+'</p>')
blocks.append('</html>');(D/'ASSESSMENT.html').write_text('\n'.join(blocks))
with (D/'UNFINISHED.csv').open('w',newline='') as f:
 fields=list(r['goals'][0]);w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(r['goals'])
(D/'views/records.jsonl').write_text('\n'.join(json.dumps(x) for x in r['goals']+r['delta_events'])+'\n')
(D/'system-flow.mmd').write_text('flowchart TD\n A[Real session and source] --> B[Authenticated local API]\n B --> C[Canonical IDs and atomic Store]\n C --> D[SQLite or PostgreSQL]\n D --> E[Trace dependencies and observations]\n E --> F[Discrepancy explanation]\n E --> G[Attributable memory]\n F --> H[Actual beneficiary validation]\n G --> H\n')
styles=getSampleStyleSheet();styles['BodyText'].fontSize=10;styles['BodyText'].leading=15;styles['BodyText'].spaceAfter=10;styles['Heading1'].textColor=colors.HexColor('#145e66');styles['Heading2'].textColor=colors.HexColor('#145e66')
def p(t,style='BodyText'):return Paragraph(html.escape(t),styles[style])
story=[p('TRACERA','Title'),p('State & Forward Docket','Title'),p(r['snapshot_id']),p('Evidence-bound full-state baseline and forward execution path'),p('Unified intent accepted; full product acceptance NOT ESTABLISHED.'),p('Candidate '+r['candidate']['candidate_sha']),p('Baseline '+r['source_sha']),p('Generated '+r['generated_at']),p('Owner: Instinct / Tracera. Source PR1157 is open and unmerged. No production promotion. Screenshots and recordings were not used.'),Spacer(1,18)]
flow='REAL SESSION + SOURCE\n          |\n AUTHENTICATED LOCAL API\n          |\n CANONICAL IDs / ATOMIC STORE\n          |\n   SQLITE or POSTGRESQL\n          |\n TRACE + PRODUCT OBSERVATIONS\n       /       \\\n DISCREPANCY   MEMORY\n       \\       /\n   REAL USER VALIDATION (NOT RUN)'
story+=[Preformatted(flow,styles['Code']),PageBreak()]
for idx,x in enumerate(r['sections']):
 story+=[p(x['title'],'Heading1'),p(x['text'])]
 if idx==0:
  data=[['Axis','Current qualified statement'],['Implementation','3 narrow Q1 checkpoints implemented'],['Engineering','Selected tests and review passed'],['Usable journey','1 synthetic local API/restart journey'],['User validation','No actual acceptance receipt']]
  t=Table(data,colWidths=[105,360]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dceeee')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),.3,colors.lightgrey)]));story+=[t,Spacer(1,15),p('NEXT: connect an actual producer/session to the durable semantic model, then qualify trace-to-discrepancy-to-memory with restart, foreign-product negatives and a real beneficiary.')]
 if idx%2==1:story.append(PageBreak())
story+=[PageBreak(),p('Goal and obligation drill-down','Title'),p('25 reconstructed branches; no claim that all historical intent or all implementation paths have been inspected. Each source location is bound to the baseline unless the Q1 receipt explicitly names the candidate.'),PageBreak()]
for n,g in enumerate(r['goals']):
 story+=[p(g['id']+' '+g['title'],'Heading1'),p(g['expected']),p('Present state: '+g['status']+'; review '+g['review']),p('Exact source: '+g['location']),p('Consequence: beneficiary cannot rely on this full goal until its closure oracle is exercised.'),p('Closure / positive oracle: '+g['closure_oracle']),p('Negative oracle: '+g['negative_verification']),p('Owner: '+g['owner']+'; dependencies: '+(', '.join(g['dependencies']) or 'none defined')+'; effort: '+g['effort'])]
 if n%2==1:story.append(PageBreak())
story+=[PageBreak(),p('Source coverage and limits','Heading1')]
for x in json.loads((D/'input-manifest.json').read_text())['inputs']:
 story+=[p(x['path'],'Heading3'),p('Revision: '+str(x['revision'])+'; SHA256: '+x['sha256']),p(x['authority'])]
story+=[PageBreak(),p('Integrity and publication','Heading1'),p('All projections derive from owner-records.json and snapshot.json. tools/render.py is the pinned evaluator-free renderer. views/build.json records input/output hashes and versions. No circular self-hash is claimed. Actual deployment, installed release, user feedback and acceptance remain independent gates.'),p(json.dumps(r['publication']))]
def footer(c,d):
 c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#526775'));c.drawString(42,24,'Tracera | '+r['snapshot_id']+' | source-bound assessment');c.drawRightString(553,24,str(d.page))
SimpleDocTemplate(str(D/'TRACERA-STATE-FORWARD.pdf'),pagesize=(595,842),rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=43,title='Tracera State & Forward Docket',author='Instinct',invariant=1).build(story,onFirstPage=footer,onLaterPages=footer)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ins=['owner-records.json','snapshot.json','input-manifest.json','tools/render.py'];outs=['ASSESSMENT.md','ASSESSMENT.html','UNFINISHED.csv','views/records.jsonl','system-flow.mmd','TRACERA-STATE-FORWARD.pdf']
receipt={'snapshot_id':r['snapshot_id'],'source_sha':r['candidate']['candidate_sha'],'renderer':'tools/render.py','renderer_version':'1.0','reportlab_version':__import__('reportlab').Version,'canonical_inputs':{x:h(D/x) for x in ins},'outputs':{x:h(D/x) for x in outs},'self_hash':'excluded to avoid cycle','product_acceptance':False}
(D/'views/build.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'outputs':len(outs),'pdf_sha256':h(D/'TRACERA-STATE-FORWARD.pdf')}))
