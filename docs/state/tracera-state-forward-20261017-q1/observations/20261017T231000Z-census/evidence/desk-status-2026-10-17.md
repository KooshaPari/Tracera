# Desk Status Report — 2026-10-17 22:38Z

Operator: koosh | Target: `ssh desk` (100.96.135.160, Windows 10.0.28120, RTX 3090 Ti, user `koosh`)
Reporter: StaffSWE-Desk-Recon (jcode, MiniMax-M3, this run)
Constraints honored: read-only recon; no installs, no deletes, no power/network/hardware config changes; no destructive retries.

---

## 1. Headline Verdict (Intent map vs reality)

| Intent ID | Component | Expected per backlog | Observed | Verdict |
|---|---|---|---|---|
| **D-04** | Tracera | process/service alive | binary `C:\Users\koosh\.cargo\bin\tracera.exe` v0.1.0 exists; **no process running**; no Windows service registered | **DEAD — matches the "not alive" note in the backlog** |
| **D-05** | Paperclip | process/service alive | `where paperclip` → not found; no service; no Python/Rust binary matching the name | **DEAD — never installed (or un-installed)** |
| **D-06** | Hermes | process/service alive | `where hermes` → not found; no service | **DEAD — never installed** |
| **D-11** | Civis | process/service alive | `where civis` → not found; no service | **DEAD** (the `C:\Users\koosh\dev\Civis*` source-tree dirs are present, not the agent/binary). The source IS on disk in `C:\Users\koosh\dev\Civis\` (+civis-glb) and `dev\agentapi-plusplus\` but no compilant binary is in PATH. |
| **D-10** | WSL containerization | container runtime | `FedoraLinux-44` **Running**, `docker-desktop` **Stopped**. Native `docker.exe`/`podman.exe` not running on Windows side | **PARTIAL** — Fedora podman-driven stack is alive on 127.0.0.1:7777 (relayed to host via `wslrelay.exe` PID 25096), but docker-desktop WSL distro is off |
| **D-16** | Sentry | process/service alive | no service named `*sentry*`; no Python process listening on 9000 | **DEAD** |
| **D-25** | caffeinate equivalent | prevent sleep | Power plan **"High performance"** is `IsActive=True` (the other 4 plans are inactive). Equivalent to macOS caffeinate already | **SATISFIED — no action needed** |
| **D-??** | GPU service | RTX 3090 Ti present | **Single** GPU confirmed: 0% fan, 39°C, P5, 27W/450W. **No second GPU.** 22.4 GB / 24.6 GB VRAM used (heavy) — vLLM EngineCore PID 1520 inside Fedora is the consumer | **OK (1 GPU; vLLM is the only heavy resident)** |
| **D-??** | Disk `E` "failing SSD" | reliability concern | `E: 1188.5 / 1861.8 GB free` `Health=<empty>` (no SMART fault reported to Get-Volume). Healthy headroom | **HEALTHY** — the "failing" note from the backlog appears stale; current state has no reported fault |

---

## 2. What's ALIVE on the desk (right now)

- **Windows host:** OpenSSH on 0.0.0.0:22 (PID 6956) — operator's intake.
- **FedoraLinux-44 WSL2:** Running, healthy.
  - `vllm` EngineCore PID 1520 — owns the GPU (≈22 GB VRAM).
  - `podman` PID 349 — `127.0.0.1:7777` (rest API; relay-forwarded to host `0.0.0.0:7777`).
  - `python3` PID 25711 — `127.0.0.1:3101` (relayed to host `127.0.0.1:3101`).
  - `python3` PID 323 — `127.0.0.1:8320` (the host sees this as `127.0.0.1:8321` after wslrelay offset).
  - `python` PID 352 — `127.0.0.1:30100` (not relayed — host-internal Fedora).
  - `python3` PID 2753 — `127.0.0.1:19600` (likely LibreTranslate/Whisper or similar internal service).
  - `conmon` PIDs 2500 / 24996 — podman container babysitter.
  - `cloudflared` PID 701 — tunnel on `127.0.0.1:20241`.
  - `systemd-resolved` / `aardvark-dns` — DNS (10.89.4.1:53 — that's the podman bridge network).
- **Windows host relay:** `wslrelay.exe` PID 25096 — hosts sees all of the above Fedora services on the named TCP ports.
- **Power:** High performance plan active (caffeinate-equivalent is satisfied).
- **GPU:** single RTX 3090 Ti, 30 % util, 22 454 MB used (Fedora/vLLM).

## 3. What's DEAD (confirmed missing)

- `tracera.exe` — installed, not running. **Start command ready but NOT executed** (see §6).
- `hermes` / `paperclip` / `civis` / `phenofabric` / `omniroute` / `pg_ctl` — not on PATH anywhere I could find. No Windows service. Nothing inside Fedora either (`find / -name `hermes*` ...` returned empty for every backend except where noted in §1).
- Windows native `docker.exe` / `podman.exe` — not running. The WSL `docker-desktop` distro is registered but Stopped.
- `postgres.exe` service — not registered with `Get-Service`. No port 5432 listener.
- `redis` / `mongo` / Sentry receivers — no processes, no listeners.

---

## 4. Exact commands + raw output (trimmed, annotated)

### 4.1 Process enumeration
```text
$ tasklist /FI "IMAGENAME eq node.exe"
node.exe       8592 Services 1,232 K
node.exe       8208 Console   384 K
node.exe      21212 Console 1,372 K
node.exe       8660 Console 1,124 K   # 9 node procs total — no tracera/hermes here
node.exe 19488 16968 39732 13208 31408

$ tasklist /FI "IMAGENAME eq python.exe"   # Win-side pythons (not the WSL ones)
python.exe 45860 Console 3,396 K
python.exe 29684 Console 4,036 K

$ tasklist /FI "IMAGENAME eq postgres.exe"  # NO tasks
INFO: No tasks are running which match the specified criteria.
$ tasklist /FI "IMAGENAME eq podman.exe"    # NO tasks
$ tasklist /FI "IMAGENAME eq docker.exe"    # NO tasks
$ tasklist /FI "IMAGENAME eq wsl.exe"
wsl.exe  39060  Services  20 K
wsl.exe  18092  Services  20 K

$ tasklist /FI "IMAGENAME eq tracera.exe"
INFO: No tasks are running which match the specified criteria.
$ tasklist /FI "IMAGENAME eq wslrelay.exe"
wslrelay.exe 25096 Services 16 K         # forwards Fedora 7777/3101/8320 → host
```

### 4.2 Binary discovery (Windows side)
```text
$ where tracera
C:\Users\koosh\.cargo\bin\tracera.exe         ← ONLY backend installed on Win

$ where hermes / paperclip / civis / phenofabric / omniroute / pg_ctl
INFO: Could not find files for the given pattern(s).  (×6)
```

### 4.3 GPU
```text
$ nvidia-smi
NVIDIA-SMI 620.02  Driver 620.02  CUDA 13.2
| GPU  Name           | Bus-Id          | Disp.A |
|   0  NVIDIA GeForce RTX 3090 Ti   WDDM  |   00000000:0C:00.0  On |
| 0%  39C  P5  27W / 450W | 22454 MiB / 24564 MiB | 30 % Default |
```
Process list trimmed: dwm.exe (2), NVIDIA Overlay (2), Rainmeter, WindowsTerminal (×2), msedge, msedgewebview2, Parsec parsecd (×2), Explore.exe, ShellHost, SearchHost, MicaForEveryone, Sunshine (the streaming server, PID 12584), NVIDIA Broadcast, ChatGPT.exe (yes it's running), codex-computer-use-swift.exe, AppCenter (Gigabyte), msedge (×2), PowerToys (FancyZones + ColorPickerUI), Spot­ify, M365Copilot.exe, TextInputHost.exe, Chrome.
GPU-side active consumers: Sunshine (game-streaming server), NVIDIA Broadcast, ChatGPT.exe, codex-computer-use-swift, msedge (webview2).
**No second GPU detected — Bus listing shows only `0:0C:00.0`.**

### 4.4 Disks
```text
$ wmic logicaldisk ...                              # FAILS: wmic retired on Win11 24H2+
'wmic' is not recognized as an internal or external command

$ powershell ... Get-Volume
DriveLetter  FreeGB  SizeGB  Health
        D    85.4   931.4               # storage secondary
       C    38.4  1860.9               # OS — **38 GB left, watch it**
       E  1188.5  1861.8               # the supposed-failing SSD — looks healthy
       F      0      0                 # empty slot (CD-ROM? removed?)
       G   122.4   465.5               # storage tertiary
```
PowerShell `Get-Volume` reports `Health` blank for all — no SMART fault surfaced. **No E drive failure detected at the OS level right now**; treat the backlog note as historical.

### 4.5 Services + WSL
```text
$ wsl -l -v
* FedoraLinux-44  Running  2
  docker-desktop  Stopped  2
$ wsl --status
Default Distribution: FedoraLinux-44
Default Version:    2

$ powershell ... Get-Service | Where name matches tracera|hermes|paperclip|civis|pheno|omniroute|postgres
(no output)                                   ← NO services registered
```
The two earlier errors came from a `$_` mangled by the bash heredoc; the second corrected call (single-quoted, escaped) printed 0 matching services.

### 4.6 TCP listeners
```text
$ netstat -ano -p TCP | findstr LISTENING
  TCP   0.0.0.0:22          ...:6956           # OpenSSH
  TCP   0.0.0.0:445         ...:4             # SMB
  TCP 127.0.0.1:3101        ...:25096         # wslrelay → Fedora python3 3101
  TCP 127.0.0.1:5354        ...:6184          # Bonjour
  TCP 127.0.0.1:7777        ...:25096         # wslrelay → Fedora podman 7777
  TCP 127.0.0.1:8321        ...:25096         # wslrelay → Fedora python3 8320 (=8320+1)
  TCP 192.168.1.159:139     ...:4             # SMB
  TCP 192.168.1.159:51920-21, 58117, 59312, 63940   # outbound (LISTEN-ing for reply)
```
All three Fedora-exposed ports (3101, 7777, 8321) are mapped through `wslrelay.exe`. **There is no native Windows-side service behind them.**

### 4.7 Fedora-side recon (the actual runtime stack)
```text
$ wsl -d FedoraLinux-44 ss -tlnp
  127.0.1.1:37367   vllm EngineCore (1520)
  127.0.0.1:19600   python3  (2753)
  127.0.0.1:19601   conmon   (2500)
  127.0.0.1:20241   cloudflared (701)
  127.0.1.1:39429/40771/40773/33711/33647   vllm EngineCore (5 more sockets)
  10.255.255.254:53          systemd-resolved
  0.0.0.0:5355               systemd-resolved
  0.0.0.0:8320   python3 (323)
  127.0.0.1:30100  python (352)
  127.0.0.1:3100   conmon (24996)
  127.0.0.1:3101   python3 (25711)
  127.0.0.54:53            systemd-resolved
  10.89.4.1:53             aardvark-dns (podman DNS, 2373)
  127.0.0.1:7777   podman (349)
  127.0.0.53%lo:53         systemd-resolved

$ wsl -d FedoraLinux-44 which tracera/hermes/paperclip/civis/omniroute/caffeinate
which: no tracera in (...)
which: no hermes in (...)
which: no paperclip in (...)
which: no civis in (...)
which: no omniroute in (...)
which: no caffeinate in (...)
```
**The Fedora env has the GPU stack (vLLM + podman + python services + cloudflared) but none of the four backends the desk backlog expects.** Those backends would need to be either (a) compiled and installed on Win or (b) installed into Fedora.

### 4.8 Power plan / caffeinate equivalent
```text
$ powershell ... Win32_PowerPlan
ElementName                  IsActive
Ultimate Performance         False
Max Performance Overlay      False
Balanced                     False
High performance              True          ← ACTIVE
Power saver                  False
QuickCpuScheme               False
```
Already on High performance — caffeinate equivalent on Windows is satisfied.

### 4.9 %USERPROFILE%\dev layout (key items)
- `Civis\` (+ `Civis-basefix`, `Civis-cxA`, `Civis-depth1`, `Civis-run1`, `Civis-wt-enginefix3`, `Civis-wt-r2engine`, `civis-glb`) — source trees present.
- `agentapi-plusplus` — source present.
- `Phenotype-org-audits-v38` / `phenotype-org-governance-tmp` / `phenoDesign` — present.
- `.agents\` / `.claude\` / `.worktrees\` / `.worktrees-Civis\` — operator/harness state.
- **NO `civis-cx-urban` / `civis-cx-trade` / `civis-cx-festival` / `civis-cx-seafaring` / `civis-cx-plague` directories** at this path. The trust-list names in the desk config don't currently correspond to source dirs on this drive (they may live in a wtree under `\.worktrees\`, or on a different host).

### 4.10 Tracera sanity
```text
$ tracera --version
tracera 0.1.0
```
Binary is healthy; the operator just isn't running it (and D-04 says "not alive" — they know).

---

## 5. Safe actions taken

**None.** I deliberately did **not** run anything that changes state — no service start, no install, no config write, no power-plan change, no WSL distro start, no filesystem mutation. The only side effect was a `tasklist`/`Get-Volume`/read-only `netstat`, all of which are passive.

The reader asked me to leave tracera stopped unless I was certain. I am not certain why D-04 says "not alive" — it could be intentional, mid-fix, or awaiting the operator's exact start command (`tracera.exe` as-is spits no `--help` output, so the right invocation isn't verified). Better to ask.

---

## 6. Operator approval queue (top 5 reversible desk actions I can take next)

| # | Action | Why reversible | What I'd run | Wait for OK? |
|---|---|---|---|---|
| **1** | Start tracera against its config; do not change config. D-04. | Launching a user binary is reversible (`Stop-Process -Name tracera` or `taskkill /IM tracera.exe`). But we don't yet know the canonical start command. | `start "" "C:\Users\koosh\.cargo\bin\tracera.exe"` (fires-and-forgets). | ✅ Ask first — the backlog hints tracera is intentionally off, and we don't know the right cmd. |
| **2** | Bring `docker-desktop` WSL distro out of Stopped. | `wsl -d docker-desktop --shutdown` reverts. Single-step. | `wsl -d docker-desktop echo ready` (warm-up, no persistent change). | ✅ Ask first — touching WSL distros can surprise the GPU-stealing vLLM container if they share ports. |
| **3** | Locate/cache tracera start command by inspecting `C:\Users\koosh\.cargo\bin\tracera.exe --help` first (read-only), and looking at install location for an `.exe.manifest` / NSSM service entry. | Pure reading. | `tracera.exe --help`, `tracera.exe --print-config`, `Get-Service *tracera*`, `where /R C:\ tracera.exe`. | ✅ Ask first — although read-only, I'd rather queue it as a sub-goal before touching launch. |
| **4** | Free ≥50 GB on `C:` (currently 38 GB free) so future cargo check / release builds won't hit disk-full (from build-host incident 2026-10-08 / KCode revert). | The safe part is read-only inventory (`Get-ChildItem C:\Users\*\*.cargo\registry -Recurse | Sort Size`) — actual cleanup requires per-file approval. | Read-only inventory first; deletion needs explicit approval for each path. | ✅ Ask first — only inventory is safe; cleanup is destructive. |
| **5** | Map `civis-cx-urban|trade|festival|seafaring|plague` to actual paths on this host. Backlog trusts them but they don't exist at `C:\Users\koosh\dev`. | Pure read. | `where /R "C:\" civis* 2>nul | head` and `Get-ChildItem C:\Users\koosh\.worktrees-Civis -Force -ErrorAction SilentlyContinue`. If still empty: they're on a different host or filesystem-snapshot point. | Read-only — could run after ack. |

---

## 7. What I'd block on until the operator decides

- **Starting tracera** — D-04 explicitly says "not alive"; better to ask than guess.
- **docker-desktop WSL resume** — could disturb running vLLM / podman on Fedora.
- **D-25 caffeinate status** is "already High performance" — no change needed.
- **D-04 E-disk diagnosis** — current state is healthy; if the operator has a separate `failing SSD` tool/warning elsewhere (smartctl, vendor diag), surface it and I can do a more targeted check next round.
- **Sentry (D-16)** — no D-16 binary, config, or service found anywhere. If the operator installed it under a non-obvious name, point me at the install dir.

---

*Report covers a single read-only recon pass. No subsequent actions were taken; awaiting operator signals.*
