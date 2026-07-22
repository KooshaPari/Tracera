# Compose safety gate

The approved rich dashboard must be tested in an isolated oracle checkout
before any local launch. `scripts/validate-oracle-compose.py` is a read-only,
dependency-free gate for that step.

It requires `nginx/nginx.conf` and `nginx/conf.d/` in the supplied checkout,
rejects any published host port `8080` (reserved by Grapheon), and reports
fixed `container_name` declarations that could collide with an existing stack.
It does not invoke Docker and never changes files or running services.

```sh
python3 scripts/validate-oracle-compose.py /path/to/oracle
python3 scripts/validate-oracle-compose.py /path/to/oracle --compose compose.local.yml
```

Exit status `0` means the static safety checks pass; `2` means the checkout
must be corrected or explicitly isolated before launch.
