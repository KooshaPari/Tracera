"""Synthetic Tracera EXP-08 configuration/evidence reuse experiment.

Research model only. It does not execute Tracera, prove real compatibility,
or authorize production evidence reuse.
"""
from itertools import product
import json

CONFIGS = [dict(platform=p,browser=b,browser_version=v,feature_flag=f,
 api_schema=a,db_schema=d,dependency_version=dep,environment=e,region=r)
 for p,b,v,f,a,d,dep,e,r in product(
 ["linux","windows"],["chromium","firefox"],[140,141],[False,True],
 [12,13],[18,19],["2.4","2.5"],["staging","prod"],["US","EU"])]

CRITERIA={
 "ui_search":{"platform","browser","browser_version","feature_flag"},
 "api_read":{"api_schema","feature_flag"},
 "db_read":{"db_schema","dependency_version"},
 "auth_flow":{"browser","browser_version","api_schema","environment"},
 "regional_copy":{"region","feature_flag"},
 "deploy_health":{"platform","environment","dependency_version"},
}
DEFAULT={"platform":"linux","browser":"chromium","browser_version":140,"feature_flag":False,
 "api_schema":12,"db_schema":18,"dependency_version":"2.4","environment":"staging","region":"US"}
DOMAINS={"platform":["linux","windows"],"browser":["chromium","firefox"],"browser_version":[140],
 "feature_flag":[False,True],"api_schema":[12],"db_schema":[18],
 "dependency_version":["2.4","2.5"],"environment":["staging","prod"],"region":["US","EU"]}

def seeds():
 out=[]
 for crit,rel in CRITERIA.items():
  keys=sorted(rel)
  for vals in product(*[DOMAINS[k] for k in keys]):
   pred=dict(zip(keys,vals))
   if "browser_version" in pred: pred["browser_version"]=(140,141)
   concrete=DEFAULT.copy()
   for k,v in pred.items(): concrete[k]=v[0] if isinstance(v,tuple) else v
   out.append((crit,pred,concrete))
 return out

def intended(pred,target):
 for k,v in pred.items():
  t=target[k]
  if k=="browser_version":
   if not v[0]<=t<=v[1]: return False
  elif k=="api_schema" and v==12 and t in (12,13): continue
  elif k=="db_schema" and v==18 and t in (18,19): continue
  elif v!=t: return False
 return True

def typed(pred,target,certificates):
 unknown=False
 for k,v in pred.items():
  t=target[k]
  if k=="browser_version":
   if not v[0]<=t<=v[1]: return False
  elif k in ("api_schema","db_schema") and v!=t:
   ok=certificates and ((k=="api_schema" and v==12 and t==13) or
                        (k=="db_schema" and v==18 and t==19))
   if not ok: unknown=True
  elif v!=t: return False
 return None if unknown else True

def evaluate(mode,ev):
 covered=unsafe=unknown=0
 for crit in CRITERIA:
  cev=[x for x in ev if x[0]==crit]
  for target in CONFIGS:
   truth=any(intended(pred,target) for _,pred,_ in cev)
   if mode=="exact":
    decision=any(concrete==target for _,_,concrete in cev)
   else:
    ds=[typed(pred,target,mode=="certified") for _,pred,_ in cev]
    decision=True if True in ds else (None if None in ds else False)
   if decision is True:
    covered+=1
    unsafe += not truth
   elif decision is None: unknown+=1
 return {"targets":len(CRITERIA)*len(CONFIGS),"reused":covered,"unsafe_reuse":unsafe,
         "unknown":unknown,"forced_rechecks":len(CRITERIA)*len(CONFIGS)-covered}

def mutations(ev):
 rows=[]
 for crit,required in CRITERIA.items():
  pred=next(p for c,p,_ in ev if c==crit)
  for missing in sorted(required):
   malformed={k:v for k,v in pred.items() if k!=missing}
   # Correct admission rejects/unknowns this evidence because a required dimension is absent.
   # A missing-as-wildcard mutant evaluates the remaining predicate and would admit these targets.
   accepted=sum(intended(malformed,t) for t in CONFIGS)
   rows.append({"criterion":crit,"omitted_required_dimension":missing,
                "wildcard_mutant_false_admissions":accepted,"detected":accepted>0})
 return rows

ev=seeds()
report={"experiment":"TRC-EXP-08-MATRIX-01","research_only":True,
 "configurations":len(CONFIGS),"criteria":len(CRITERIA),"evidence_seeds":len(ev),
 "models":{m:evaluate(m,ev) for m in ("exact","typed","certified")},
 "mutation_controls":mutations(ev),
 "limitations":["Compatibility truth is constructed, not empirically measured.",
 "Only conjunctive typed dimensions are modeled.","Certificates are assumed admitted/trusted.",
 "No candidate-artifact equivalence or criterion-version compatibility.",
 "No Tracera runtime code is executed."]}
print(json.dumps(report,indent=2,sort_keys=True))
