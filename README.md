# papersmith-ai

> **A scientific paper engineering framework**: ingests reference PDF literature into high-fidelity agent-readable Markdown (LaTeX equations, markdown tables, extracted figures) and conducts formal, invariant-checked paper proposal deliberation and reproducible experimentation.

[![CI](https://github.com/CarlosAndres12/papersmith-ai/actions/workflows/test.yml/badge.svg)](https://github.com/CarlosAndres12/papersmith-ai/actions/workflows/test.yml)
[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D20-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.11-blue.svg)](https://www.python.org/)
[![Documentation](https://img.shields.io/badge/Docs-Espa%C3%B1ol-orange.svg)](README.es.md)

---

## ⚡ Quickstart

### 1. Install CLI & Provision Environment

Install the `papersmith` workspace orchestrator and bootstrap the isolated runtime (Python 3.12, PyTorch, Surya OCR, and `llama-server` C++ binary):

```bash
# 1. Install CLI
pipx install .

# 2. Provision isolated ingestion runtime (CPU or CUDA automatically detected)
python scripts/setup_env.py install

# 3. Setup agent harness symlinks (Claude Code, Pi, OpenCode, Antigravity)
npm run setup:harnesses
```

### 2. Initialize a Research Workspace

Create a standalone, decoupled research workspace:

```bash
papersmith init ~/papers/sparse-ae \
  --title "Sparse Autoencoder Audit" \
  --topic "mechanistic interpretability" \
  --remote kaggle

cd ~/papers/sparse-ae
papersmith status --json
```

### 3. Ingest Literature

Ingest local PDFs or arXiv/OpenReview URLs into structured Markdown:

```bash
# Ingest arXiv paper
papersmith ingest https://arxiv.org/abs/2309.08600

# Ingest local PDF
papersmith ingest ~/Downloads/reference-paper.pdf
```

### 4. Deliberate & Refine Proposals

Deliberate research proposals using the deterministic AST-verified deliberation engine:

```bash
papersmith deliberate . --action status
```

---

## 📟 CLI Command Reference

Every command runs as `papersmith <command> [options] [<dir>]`. `<dir>` defaults to the current directory and must point at an initialized workspace (except `init`). Global flags: `--version`.

| Command | What it does |
|---|---|
| `init` | Create a standalone research workspace |
| `upgrade` | Sync framework files, preserving your research |
| `status` | Show workspace health, proposals, runs, inbox |
| `ingest` | Ingest a PDF or literature URL into Markdown |
| `deliberate` | Talk to the proposal-deliberation engine |
| `implement` | Delegate to the proposal-implementation harness |
| `run` | Execute a compute profile (local / Kaggle / Slurm) |
| `remote` | Pack, submit, and track remote jobs directly |
| `target` | List, select, and check compute targets |
| `audit` | Audit structure and detect generated drift |

### `papersmith init <dir>`

```bash
papersmith init ~/papers/sparse-ae \
  --title "Sparse Autoencoder Audit" \
  --topic "mechanistic interpretability" \
  --remote kaggle
```

| Flag | Effect |
|---|---|
| `--title TEXT` | Paper title written into the workspace docs |
| `--topic TEXT` | Research topic |
| `--tools TEXT` | Comma-separated runtimes to provision |
| `--remote {kaggle,local,slurm}` | Default compute target (default: `kaggle`) |
| `--no-npm` | Skip the best-effort `npm install` (hermetic/offline use) |

Creates `.papersmith/`, `guidance/reference-papers/`, `proposals/{drafts,deliberated,receipts}/`, `implementations/`, `kaggle-inbox/`, `journal/`, plus the kit copy and manifest.

### `papersmith upgrade [<dir>]`

```bash
papersmith upgrade ~/papers/sparse-ae
```

| Flag | Effect |
|---|---|
| `--tools TEXT` | Replace the active runtime generators |
| `--force` | Force framework-file writes |

Only touches framework-managed files — never `guidance/`, `proposals/`, `implementations/`, `kaggle-inbox/`, `journal/`, `DECISIONS.md`, `papersmith.yaml`, `README.md`, or `.env*` files. Against a kit checkout without reinstalling: `PAPERSMITH_KIT_ROOT=/path/to/papersmith-ai papersmith upgrade <dir>`.

### `papersmith status [<dir>]`

```bash
papersmith status --json
```

| Flag | Effect |
|---|---|
| `--json` | Machine-readable snapshot (versions, proposals, runs, inbox) |

Reports drifted files by name; exit code stays `0` while drift is reported (non-zero exit on drift is a known gap).

### `papersmith ingest <file_or_url> [<dir>]`

```bash
papersmith ingest https://arxiv.org/abs/2309.08600
papersmith ingest ~/Downloads/reference-paper.pdf --ocr
```

| Flag | Effect |
|---|---|
| `--ocr` | Balanced OCR-oriented extraction mode (heavier, for scans) |

Downloads/classifies the reference, extracts it to Markdown with LaTeX equations plus figure files (one folder per paper), and refreshes the index. First run downloads ~1.5 GB Surya weights unless the environment is pre-provisioned.

### `papersmith deliberate [<dir>]`

```bash
papersmith deliberate . --action status
papersmith deliberate . --action init
papersmith deliberate . --request-file request.json
```

| Flag | Effect |
|---|---|
| `--action ACTION` | Real engine operation (`status`, `init`, successors…) or alias |
| `--request JSON` / `--request-file FILE` | Raw JSON request object / file containing one |
| `--serve` | Persistent JSON-lines mode |
| `--revision FILE` | Managed source filename the operation applies to |
| `--instruction TEXT`, `--query TEXT` | Instruction / query payloads |
| `--selected-entry-id ID`, `--decisions JSON` | Resolved edit decisions for mutate operations |
| `--accept`, `--acceptance-token TOKEN` | Accept a `CREATE_SUCCESSOR` preview |
| `--withdrawal-operation-id ID`, `--withdrawal-reason TEXT` | Withdraw a published revision |
| `--prior-conclusion TEXT` | Prior conclusion for follow-up operations |

Runs the deterministic AST-verified deliberation engine keylessly and locally (no model call for state operations).

### `papersmith implement [<dir>]`

```bash
papersmith implement . --action verify --target implementations/demo
papersmith implement . --action probe --target implementations/demo
```

`--action` is required. Common actions: `env`, `plan`, `apply` (alias `materialize`), `admit`, `handoff`, `compose`, `probe` (alias `benchmark`), `verify`. Supporting flags: `--target`, `--name`, `--plan`, `--finding`, `--entry-text`, `--python`, `--shards`, `--revision`; anything after the known flags is forwarded as `extra` to `implementation_cli.py`.

### `papersmith run <profile> [<dir>]`

```bash
papersmith run smoke_and_invariants --dry-run
papersmith run full-training --target kaggle-gpu-pool --consent <token>
```

| Flag | Effect |
|---|---|
| `--target NAME` | Override the profile's compute target |
| `--dry-run` | Plan only — records the command, dispatches nothing |
| `--shard VALUE` | Run a single campaign shard |
| `--consent TOKEN` | Consent token for remote submission (forwarded, enforced downstream) |

Dispatches per provider (local subprocess / Kaggle submit / ssh `sbatch`) and appends every job to `.papersmith/runs_ledger.jsonl`.

### `papersmith remote {pack,push,status,pull,sync} [<dir>]`

```bash
papersmith remote pack --target kaggle-gpu-pool --entrypoint train.py
papersmith remote status --job <job-id>
papersmith remote pull --job <job-id> --dest ./results
```

Key flags: `--target`, `--entrypoint`, `--backend`, `--account`, `--job`, `--submission-id`, `--dest`, `--consent`, `--smoke`, `--unit` (campaign scoping, repeatable), `--force`, `--resolve`, plus job-definition flags (`--service`, `--job-name`, `--product`, `--commit`, `--repo-url`, `--repo-ref`, `--run-module`, `--run-function`, `--clone-path`, `--regenerate`). Extra tokens are forwarded to `remote_cli.py`. Live submission spends real quota — prefer `--smoke` / `--dry-run` first.

### `papersmith target {list,set,check}`

```bash
papersmith target list
papersmith target set kaggle-gpu-pool
papersmith target check
papersmith target check slurm-cluster
```

- `list [<dir>]` — configured targets, marking the active one (`*`).
- `set <name> [<dir>]` — persist the default target into `.papersmith/config.json`.
- `check [name] [<dir>]` — connectivity probe: `local` checks for Python, `kaggle` shells to the accounts helper, `remote-ssh` tries `ssh -o BatchMode=yes -o ConnectTimeout=5 <host> true`.

### `papersmith audit [<dir>]`

```bash
papersmith audit --check-drift
```

| Flag | Effect |
|---|---|
| `--check-drift` | Also report generated-file drift as findings (never repairs) |

Audits workspace structure and consistency. Currently bound to the `skill-audit` subject; drift is reported, not fixed.

> **Note:** `kaggle-accounts` (validate/remove/list/discover/materialize) has no `papersmith` subcommand yet — it runs as `python3 skills/kaggle-accounts/scripts/accounts_cli.py …` or indirectly via `target check`.

---

## 🏛️ Architecture & Core Components

```
papersmith-ai/
├── src/papersmith/             # Python CLI workspace orchestrator & runtime bridges
│   ├── core/                   # Init, status, ingest, upgrade, executor, ledger
│   └── bridges/                # Node, Python, Deliberation, Remote execution bridges
├── skills/                     # Canonical skill tree projected into agent harnesses
│   ├── paper-ingestion/        # Marker + Surya OCR + llama-server extraction pipeline
│   ├── proposal-deliberation/  # Formal TypeScript AST verification & state machine
│   ├── proposal-implementation/# Reproducible research code & test generators
│   ├── remote-execution/       # Distributed compute dispatch (Kaggle T4/P100 / local)
│   └── skill-audit/            # Meta-auditor ensuring zero lexicon leaks and surface drift
├── guidance/                   # Reference papers & domain guidelines
├── tests/                      # 1,880+ test suite (Node.js & Python meta-audits)
└── scripts/                    # Environment provisioning and harness setup scripts
```

### Key Engineering Guarantees:
* **AST & Boundary Invariants**: Mathematical equations and sections are tracked by stable IDs and immutable revision chains. No unauthorized deletions, relocations, or hallucinated boundary fusing.
* **Keyless & Local-First**: Literature ingestion runs completely offline and local via Marker and `llama.cpp`.
* **Harness-Agnostic Projection**: The canonical `skills/` tree projects transparently into `.claude/skills`, `.pi/skills`, `.opencode/skills`, and `.antigravity/skills`.

---

## 🧪 Development & Testing

Run the full polyglot test suite:

```bash
# Run Node.js test suite (365 tests)
npm test

# Run Python test suite (1,500+ tests)
pytest

# Run all test suites
npm run test:all
```

---

## 📖 Complete Documentation

* **Spanish Full Manual**: For the complete, detailed specification and runbook in Spanish, see [README.es.md](README.es.md).

---

## 📄 License

Apache-2.0
