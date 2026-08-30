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
