# Canonical oracle gateway assets

These files are an evidence copy of the gateway configuration from
`origin/releases/stable` at `f8aa0918a`. They are retained in the rich-dashboard
recovery session as deployment inputs; they are not active Compose configuration
and must not be launched on Grapheon's protected port `8080`.

Source paths:

- `deploy/nginx/nginx.conf`
- `deploy/nginx/conf.d/ssl.conf`
- `deploy/nginx/conf.d/tracertm.conf`

The gateway routes Python services (AI/auth) and Go services (items/graph/search)
and assumes service names `python` and `go`. Any local deployment must remap host
ports and isolate container names before use.
