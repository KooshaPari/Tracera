# Tracera Electron shell

This is the production-oriented desktop shell for the approved rich dashboard. It
defaults to the local oracle gateway at `http://127.0.0.1:18000`; set
`TRACERA_GATEWAY_URL` (or `TRACERA_URL`) for a controlled deployment and
`TRACERA_DEV_URL` for a running Vite instance. The packaged shell starts the
bundled `tracera` CLI (`up --no-wait`), waits for `/health`, then opens the
dashboard. Set `TRACERA_AUTOSTART=0` when a supervisor owns the stack.

The existing Electrobun app is intentionally retained. This shell is a separate
promotion path until installer signing, update channels, and cross-platform
dogfood gates are green.
