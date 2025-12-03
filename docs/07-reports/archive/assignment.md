All Applications Generate an entrypoint (lets switch from ./atoms \ ./zen etc to ./platform) this is generically built and hten tailored to each project via each of configuration (e.g. server = infra.service(param tailoring)), composition, or extension ( add features or use with a bigger implementation). The ideal goal is <= 350 line entry points, custom scripts\use cases not accounted for (e.g. atoms has schema sync backfill and other features, other projects similarly will have other specialized commands, tehse must also be wrapped into our generics\primitives and effectively be registered\generated, very little outside of project-domain-specific logic\code should be inth at given project, and even then foresight shoudl identify items that adjacent projects may want. 


# User Develops Simple Application 
##  (API Server of Sorts -- Assume server \ app.py entry point, no other services or resources managed by us directly)
### Registered Services (For Port Assignment, Process Mgmt \ Cleanup, Tunnel \ Proxy Mgmt\Wiring)
#### 1. API Server (Assumed Uvicorn or similar python web server of any kind
#### 2. Reverse Proxy For Domain Wiring for paths, and fallback server alignment
#### 3. Fallback server, is a middleware html layer that shows first in between loading the destination process \ loads on err in place of cloudflare\others so we can know whre the problems lie exactly.
#
#
# User Develops Complex Full Stack Application
## Frontend, Backend Service, Redis\PG\NATS (NATS on native systemctl daemon, redis on docker (both globally tenanted), private Dockered Postgres), further relies on services\items on Neon\Render\Fly.io\Railway\Upstash Redis\Supabase\Vercel, all of these are defined resources.
#
### Registered Services:
#### 1-3 (same as simple example)
#### Frontend is NextJS, is it better to handle as a resource or service? pick the best choice
### Registered Resources
#### 1. Redis daemon (global --- checks if up otherwise starts, then validates data\state if needed (not relevant to a caching service, moreso for shared db tenants)
#### 2. NATS container, same as above just via docker checks 
#### 3. PG Private: same as above, but follows process\srvc logic of kill on close and kill on startup prior to open
#### N: cloud\SAAS resources: has a mix of SDK\API\CLI processes to eitehr perform lifecycle management jsut like other resources, or in cases of items like suapabse\redis that are always on, just status\connection checks etc.
#



for all resources AND services we expect to be ablet o configure 3 layers \ targets of deployment (as a bare minimum, allow creation of new custom targets\layers in addition), these are local, dev=preview, prod, local has a subvariant local-dev for live reloads, and is the local tunneled target, dev\preview\(NONE=no explicit selection) = a partial production deployment, e.g. vercel preview and the equivalent staging production deployment target, prod is a complete produciton deploymetn, our test commands in our primitives similarly offer this AND a hot\dry\cold (hot=live "real" tests, e.g. direct playwright automations \ http calls, cold is in-memory but agains treal auth\srvcs, dry is completely mocked.) 
For all these we implement switches that route canonical vars, e.g. endpoint \ resource targets (local vs other targets etc, the function that provides these canonical urls or acts as ORM\adapter to various resources must automatically handle this on behalf of the project when detecting the target, thereby changing the definition of say mcp_endpoint and pg_endpoint between a .kooshapari.com dev domain for both to a supabase and atoms.tech domain for prod as an example, these would al lbe defined in our service\resource definitions



we must support packaging each service as a daemon srvc, docker container \ kube or other vm\contaienr\cluster rather than just direct execution alone. This means all services rendered are packaged into the appropriate infra and deployed as a managable  cluster (whether this be in kube daemon docker or other technologies that make the most sense for this use case.) 



Generally on Startup for all Local:

Clear & Prepare Tunnel\FallBack\DNS\Proxy\Config in full -> Proceed to Resources -> Proceed to Services (allow setting startup dependencies for all rsrcs\services if applicable for that project, otherwise start each in parallel but rsrcs as a phase first prior to services.)



Wait & Retry Process throughout for all + constant polling\validation using tenacity\httpx\others, then we see a rich non interactive TUI (live output stream)(static tui pinned to bottom) from top to bottom that hsows process\resource\service\tunnel states live as well as the live outputs so we can evaluate errors, 

THese exact steps have been enumerated countless times and should already be present in pheno-sdk, either in incomplete, or disconnected (implemented in different libraries or not consolidated) form, identify and fix

