"""Reading projections from one append-only owner observation; no acceptance reducer."""
import pathlib,json,html,hashlib
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Preformatted
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing,Rect,String,Line
root=pathlib.Path(__file__).parent;r=json.loads((root/'observation.json').read_text())
sections=[('Exact runtime subject',f"Tracera {r['subject']['source_sha']}; clean isolated source. Binary SHA-256 {r['subject']['binary_sha256']}. Observed {r['observed_start']} to {r['observed_end']}. SQLite on owned loopback; stopped after verification."),('Fresh authenticated gates','Readiness 200; anonymous 401; absent baseline 404; missing CSRF 403; malformed batch 422. These are isolated runtime facts, not deployed product qualification.'),('Genuine engineering observation','The actual runtime receipt was hashed and manually assigned to authenticated durable intake. Mounted generic ingest accepted one observation. Readback, exact process restart, retry without duplication, foreign-scope rejection, and immutable-conflict rollback passed.'),('Actual producer bridge',f"Producer source {r['bridge']['producer_source_sha']}; controlled subject {r['bridge']['controlled_subject_sha']}. The real Helios script ran three deliberately trivial print commands. Its original output was ingested through the mounted benchmark route, read back, restarted and replayed. Causal identities matched exactly. This is producer/consumer plumbing proof, not valuable benchmark acceptance."),('Limits and next useful result','Unsigned tenant metadata and a caller-controlled local bearer do not establish external producer ownership. Product/capability assignment was explicit and manual. No actual person accepted a journey. Next: meaningful owned-product workload, authenticated producer binding, source-change reconciliation, and consumer navigation.'),('Four-axis delta','Implementation: unchanged in this observation. Engineering assurance: new exact-patched-subject runtime evidence, unreviewed. Complete user-usable journeys: no accepted increment. Real user validation: not observed. Full-product numerator/denominator remain null; no completion percentage assigned.'),('Integrity and continuity','The existing 31-page PDF and locked snapshot are unchanged. This later append-only observation does not retroactively change their as-of date. Hashes identify bytes, not author authenticity. Requalify when relevant source, dependencies, runtime configuration, Store or evaluator changes.')]
if r.get('substantive_bridge'):
 b=r['substantive_bridge'];sections.insert(4,('Substantive producer workload',b['summary']))
md=['# Tracera runtime delta','',f"Observation `{r['observation_id']}`; generated from `observation.json`.",'','```text','actual producer -> explicit assignment -> authenticated local intake','                -> durable SQLite -> read/findings -> restart/replay','```','', 'Text alternative: producer output is explicitly assigned to a product and capability, submitted through local bearer and CSRF protection, then verified through persistence, readback, restart and idempotent replay.','']
for title,text in sections:md+=['## '+title,'',text,'']
md+=['## Evidence','']+[f"- [{e['path']}]({e['path']}): `{e['sha256']}`" for e in r['evidence']]
(root/'DELTA.md').write_text('\n'.join(md)+'\n')
flow='actual producer -> explicit assignment -> local intake -> durable read -> restart/replay'
(root/'system-flow.mmd').write_text('flowchart LR\n A[Actual producer] --> B[Explicit assignment]\n B --> C[Authenticated local intake]\n C --> D[Durable SQLite]\n D --> E[Read and findings]\n E --> F[Restart and replay]\n')
blocks=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Tracera runtime delta</title><style>body{font:17px/1.55 system-ui;max-width:950px;margin:35px auto;padding:20px;color:#183047}h1,h2{color:#125e66}code{overflow-wrap:anywhere}pre{white-space:pre-wrap}a{color:#126287}</style><h1>Tracera runtime delta</h1><pre>'+html.escape(flow)+'</pre>']
for title,text in sections:blocks+=['<h2>'+html.escape(title)+'</h2><p>'+html.escape(text)+'</p>']
blocks+=['<h2>Evidence</h2><ul>']+['<li><a href="'+e['path']+'">'+e['path']+'</a>: <code>'+e['sha256']+'</code></li>' for e in r['evidence']]+['</ul></html>'];(root/'DELTA.html').write_text('\n'.join(blocks))
styles=getSampleStyleSheet();styles['BodyText'].fontSize=10;styles['BodyText'].leading=14;styles['BodyText'].spaceAfter=12
story=[Paragraph('Tracera runtime delta',styles['Title']),Paragraph('Later observation - existing dossier remains immutable',styles['BodyText'])]
d=Drawing(475,85)
for i,label in enumerate(['Producer','Assignment','Local intake','Persistence','Restart']):
 x=i*95;d.add(Rect(x,30,86,32,fillColor=colors.HexColor('#e1f1f1'),strokeColor=colors.HexColor('#17646c')));d.add(String(x+43,43,label,textAnchor='middle',fontSize=9))
 if i<4:d.add(Line(x+86,46,x+95,46,strokeColor=colors.HexColor('#17646c')))
story +=[d,Paragraph('Text alternative: real output flows through explicit product assignment and authenticated local intake to durable storage, readback and restart/replay.',styles['BodyText'])]
for i,(title,text) in enumerate(sections):
 if i==4:story.append(PageBreak())
 story +=[Paragraph(title,styles['Heading2']),Paragraph(html.escape(text),styles['BodyText'])]
story +=[Paragraph('Evidence and provenance',styles['Heading2'])]
for e in r['evidence']:story.append(Paragraph('<link href="'+e['path']+'">'+e['path']+'</link>',styles['BodyText']))
def footer(c,doc):c.setFont('Helvetica',8);c.drawString(42,25,'Append-only observation | no product acceptance claimed');c.drawRightString(553,25,str(doc.page))
SimpleDocTemplate(str(root/'DELTA.pdf'),pagesize=(595.28,841.89),leftMargin=42,rightMargin=42,topMargin=35,bottomMargin=42,invariant=1).build(story,onFirstPage=footer,onLaterPages=footer)
