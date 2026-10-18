import base64,subprocess,pathlib,json
script=r'''
$ProgressPreference='SilentlyContinue'
$projects=Invoke-RestMethod -TimeoutSec 10 -Uri 'http://127.0.0.1:8080/api/v1/projects'
$rows=@()
foreach($project in $projects.items){
 $ids=@{};$types=@{};$offset=0;$pages=0;$errorMessage=$null;$complete=$false;$stub=$false;$reported=$null
 try{
  do{
   $url='http://127.0.0.1:8080/api/v1/items?project_id='+$project.id+'&limit=100&offset='+$offset
   $response=Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 -Uri $url; if($response.Headers['Content-Type'] -notmatch 'json'){throw ('non_json_response:'+ $response.Headers['Content-Type'])};$page=$response.Content|ConvertFrom-Json;if($null -eq $page.items){throw 'missing_items_array'}
   $pages++;if($page.stub -eq $true){$stub=$true;break};$reported=$page.total
   foreach($item in $page.items){if($ids.ContainsKey($item.id)){throw 'duplicate_item_id'};$ids[$item.id]=$true;$kind=$item.itemType;if(!$kind){$kind=$item.item_type};if(!$kind){$kind=$item.type};if(!$kind){$kind=$item.kind};if(!$kind){$kind='<missing-type>'};if(!$types.ContainsKey($kind)){$types[$kind]=0};$types[$kind]++}
   $count=@($page.items).Count;$offset+=$count
   if($null -ne $page.total -and $offset -ge $page.total){$complete=$true;break}
   if($page.has_more -eq $false){$complete=$true;break}
   if($count -eq 0){$errorMessage='empty_page_before_complete';break}
  }while($pages -lt 100)
 }catch{$errorMessage=$_.Exception.Message}
 $rows += [pscustomobject]@{project=$project.name;id=$project.id;items=$ids.Count;types=$types;pages=$pages;reported_total=$reported;complete=$complete;stub=$stub;error=$errorMessage}
}
[pscustomobject]@{observed_at=(Get-Date).ToUniversalTime().ToString('o');origin='Windows desk loopback8080';authentication='No additional credential required by observed GET surface';project_count=@($projects.items).Count;rows=$rows}|ConvertTo-Json -Depth 6 -Compress
'''
cmd=['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','koosh@100.96.135.160','powershell -NoProfile -EncodedCommand '+base64.b64encode(script.encode('utf-16le')).decode()]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=90);pathlib.Path('/tmp/tracera-backend-census-8dd/live-counts-final.json').write_text(r.stdout);print(r.stdout);print(r.stderr[:500]);print('exit',r.returncode)
