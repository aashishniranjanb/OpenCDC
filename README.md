# OpenCDC — Open-source Clock Domain Crossing analysis

> **Project status**: Initial scaffold complete, demo design + netlist parser in place.

## 1. Problem statement (why this matters)

Modern SoC/FPGA designs routinely span dozens of clock domains. A single missed synchronizer or wrong CDC assumption can cause:
- elusive functional failures that only appear after silicon tapeout
- multi-week debug cycles, at a cost of **$1M+ per respin** in a typical ASIC flow
- latent field failures (soft errors, metastability, deadlocks) that are impossible to reproduce reliably in lab.

**Judging criteria callout:** The core evaluation is not just code, it is the **problem you chose and how clearly you describe it**. The problem we solve is the *real* economic risk in hardware projects: CDC bugs that are expensive and hard to find.

## 2. Why existing tools are not good enough (cost / closed-source / trust)

Many teams rely on proprietary CDC checkers bundled with EDA tools (e.g., Synopsys SpyGlass, Cadence JasperGold, Mentor Calibre CDC). These tools have several limitations:

- **High cost / license fees**: not accessible to open-source hardware teams, academic labs, or early-stage startups.
- **Closed source / black box**: no ability to audit or extend checks, limited visibility into why a violation is reported or suppressed.
- **Opaque heuristics & false positives**: forcing engineers to spend hours tuning rule sets and chasing irrelevant reports.
- **Not designed for rapid iteration**: many checkers expect a full gate-level netlist and are slow to run in a tight CI loop.

OpenCDC aims to be a lightweight, transparent (and auditable) CDC analysis stack that scales with open-source flows.

## 3. Approach (what OpenCDC will do)

This project starts with a minimal, reproducible pipeline that:

1. **Synthesizes a Verilog design with Yosys** to a JSON netlist.
2. **Parses the netlist** to extract storage elements (FFs), nets, and their domain affiliations.
3. **Analyzes clock domain crossings** by building a graph of signals crossing between domains and identifying missing synchronization.

The initial prototype focuses on a common CDC error pattern: a register from a fast clock domain being sampled directly in a slower domain without a proper synchronizer.

## 4. Architecture (what this repo contains)

### 4.1. Core components (Python)

- `opencdc/parser.py` – reads Yosys JSON netlists and extracts hierarchical cell/net information.
- `opencdc/checker.py` – (planned) will build a domain-crossing graph and identify missing synchronization.
- `opencdc/domains.py` – (planned) will contain clock-domain inference heuristics and helper data structures.

### 4.2. Example inputs

- `examples/counter.v` – a two-clock-domain counter with an intentional CDC violation (fast domain value sampled in slow domain without synchronizer).

### 4.3. Tests and CI

- `tests/` – placeholder for unit tests. The first useful test will be: "verify parser extracts N FFs from the example counter netlist."

## 5. Getting started (what to run today)

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Generate a Yosys netlist for the example design:

```bash
cd examples
yosys -p "synth; write_json counter_netlist.json" counter.v
cd ..
```

3. Verify parsing works:

```bash
python opencdc/parser.py examples/counter_netlist.json
```

If you see "Found N flip-flops", the pipeline is working and you can start building checks.

## 6. Roadmap (what comes next)

- **Stage 1:** Add domain inference via clock nets and register clustering.
- **Stage 2:** Build a CDC crossing graph + identify unsynchronized crossings.
- **Stage 3:** Add reporting + visualization (e.g., Graphviz diagrams of domain boundaries and crossing points).
- **Stage 4:** Expand to cover multi-bit buses and pulse-based handshake CDCs.

## 7. AI assistance

OpenCDC is primarily a manual engineering effort, but I used AI (GitHub Copilot / OpenAI models) to help draft documentation and design the initial code structure. All source code is authored by me; any AI usage was limited to writing documentation text, planning, and formatting.

> **Note:** If code is later generated or heavily influenced by an LLM, it will be explicitly documented in this section as required by the hackathon guidelines.
