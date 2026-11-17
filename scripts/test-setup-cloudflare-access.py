import pathlib,tempfile,subprocess,os,json,stat,sys
SCRIPT=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path(__file__).with_name('setup-cloudflare-access.sh')
CASES=['missing-id','null-id','empty-id','wrong-id','malformed','success-false','bad-client','bad-secret','newline','post-fail','write-fail','fsync-fail','inode','symlink','delete-transport','delete-api','valid','reuse','ci-refuse','null-result','list-result','null-client','empty-client','null-secret','empty-secret','unsafe-id','existing-output']
with tempfile.TemporaryDirectory() as d:
 root=pathlib.Path(d);root.chmod(0o700);bin=root/'bin';bin.mkdir()
 mock=bin/'curl';mock.write_text('''#!/usr/bin/env python3
import os,sys,json,pathlib
args=sys.argv[1:];u=args[-1];case=os.environ['CASE'];out=pathlib.Path(os.environ['OUT']);method='DELETE' if 'DELETE' in args else 'POST' if 'POST' in args else 'GET'
with open(os.environ['LOG'],'a') as f:f.write(method+' '+u+'\\n')
if u.endswith('/user/tokens/verify'):print('{"success":true}')
elif '/access/apps?' in u:print('{"result":[{"domain":"t.tracera.pheno.studio","id":"app"}]}')
elif '/service_tokens?' in u:print(json.dumps({'result':[{'name':'tracera-ci-smoke','id':'existing'}] if case=='reuse' else []}))
elif method=='DELETE':
 if case=='delete-transport':sys.exit(22)
 print(json.dumps({'success':case!='delete-api'}))
elif method=='POST' and u.endswith('/service_tokens'):
 if case=='post-fail':sys.exit(22)
 if case=='malformed':print('{invalid');sys.exit()
 r={'id':'mock-id','client_id':'mock-client','client_secret':'SENTINEL_SECRET_789'}
 if case=='missing-id':del r['id']
 if case=='null-id':r['id']=None
 if case=='empty-id':r['id']=''
 if case=='wrong-id':r['id']=123
 if case=='bad-client':r['client_id']=[]
 if case in ['bad-secret','delete-transport','delete-api']:del r['client_secret']
 if case=='null-client':r['client_id']=None
 if case=='empty-client':r['client_id']=''
 if case=='null-secret':r['client_secret']=None
 if case=='empty-secret':r['client_secret']=''
 if case=='unsafe-id':r['id']='../bad'
 if case=='null-result':r=None
 if case=='list-result':r=[]
 if case=='newline':r['client_secret']='SENTINEL_SECRET_789\\ninject'
 if case in ['inode','symlink']:
  out.rename(str(out)+'.reserved');foreign=out.parent/'foreign';foreign.write_text('FOREIGN')
  if case=='inode':out.write_text('FOREIGN')
  else:out.symlink_to(foreign)
 print(json.dumps({'success':case!='success-false','result':r}))
elif '/policies?' in u:print('{"result":[]}')
else:print('{"success":true}')
''');mock.write_text(mock.read_text().replace('#!/usr/bin/env python3', '#!'+sys.executable));mock.chmod(0o755)
 py=bin/'python3';py.write_text('''#!/usr/bin/env python3
import os,sys
real=os.environ['REAL_PY'];args=sys.argv[1:]
if len(args)>1 and args[0]=='-c' and 'os.ftruncate(fd, 0)' in args[1] and os.environ['CASE'] in ['write-fail','fsync-fail']:
 fn='write' if os.environ['CASE']=='write-fail' else 'fsync'
 args[1]='import os\\ndef fail(*a,**k): raise OSError("injected")\\nos.'+fn+'=fail\\n'+args[1]
os.execv(real,[real]+args)
''');py.write_text(py.read_text().replace('#!/usr/bin/env python3', '#!'+sys.executable));py.chmod(0o755)
 for case in CASES:
  p=root/case;p.mkdir(mode=0o700);out=p/'token';log=p/'calls';env={**os.environ,'PATH':str(bin)+':'+os.environ['PATH'],'REAL_PY':sys.executable,'CASE':case,'OUT':str(out),'LOG':str(log),'TOKEN_OUTPUT_FILE':str(out),'CLOUDFLARE_API_TOKEN':'mock','CLOUDFLARE_ACCOUNT_ID':'mock'}
  if case=='ci-refuse':env.pop('TOKEN_OUTPUT_FILE')
  if case=='existing-output':out.write_text('FOREIGN')
  r=subprocess.run(['bash',str(SCRIPT)],env=env,capture_output=True,text=True);calls=log.read_text();text=r.stdout+r.stderr;assert 'SENTINEL_SECRET_789' not in text,(case,text)
  if case in ['valid','reuse']:
   assert r.returncode==0,(case,text)
   if case=='valid':assert stat.S_IMODE(out.stat().st_mode)==0o600 and 'SENTINEL_SECRET_789' in out.read_text()
   assert calls.count('POST ')==(2 if case=='valid' else 1)
  else:
   assert r.returncode!=0,(case,text);assert not any(l.startswith('POST ') and '/policies' in l for l in calls.splitlines()),case
   if case in ['inode','symlink','existing-output']:
    assert out.read_text()=='FOREIGN',case
    if case!='existing-output':assert (p/'foreign').read_text()=='FOREIGN'
   else:assert not out.exists(),(case,text)
   known=case in ['success-false','bad-client','bad-secret','newline','write-fail','fsync-fail','inode','symlink','delete-transport','delete-api','null-client','empty-client','null-secret','empty-secret']
   assert calls.count('DELETE ')==int(known),(case,calls)
   if case in ['delete-transport','delete-api']:assert 'manually revoke token id=mock-id' in text
  print('PASS',case)
