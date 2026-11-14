# Solana Validator Scheduler Telemetry

Empirical measurement harness and analysis suite investigating transaction ordering rules across Solana Mainnet validators running different client software and forks.

Author: Ariya Sarrafzadeh (Callsign: HaroSS)  
Solana Settlement Address: `GPnfvrNrro1PJTbN4moGkTwtJm3iqywLDZnAYY7pco52`  
Network: Solana Mainnet  
Epoch: 1065 (Measured post-Alpenglow upgrade, October 22 to 23, 2026)

---

## 1. Executive Summary

This telemetry engine measures how leader schedulers order transactions inside Solana Mainnet blocks across 6 validators spanning 3 distinct client software versions:
1. **Jito-Solana v4.3.2**: Shinobi Systems (Slot 460184800) and Kraken (Slot 460184876)
2. **Firedancer / Frankendancer v26.10.4**: JD549 (Slot 460184832), Awesome-FD (Slot 460184856), and Revtec-FD (Slot 460184872)
3. **Agave / Fork v4.3.0**: Validator-9rkJ (Slot 460184812)

### Core Empirical Finding
On modern Solana Mainnet, global transaction ordering does not follow a strict linear priority fee rule. Spearman rank correlation between priority fee and block position ranges from -0.2930 to +0.1613. Transaction position is driven primarily by:
1. Off-chain MEV bundle extraction (Jito tip accounts claim head block slots).
2. Account write-lock contention (uncontended lower-fee transactions execute and commit ahead of contended high-fee transactions).
3. Banking stage multi-threading (4 to 6 concurrent worker threads commit transactions out of packet arrival order).

---

## 2. Architecture & Experiment Design

```
+-------------------------------------------------------------+
|                 Solana Mainnet RPC Client                   |
+-------------------------------------------------------------+
                              |
       +----------------------+----------------------+
       |                                             |
       v                                             v
+-------------------------------+   +-------------------------------+
|     LeaderScheduleTracker     |   |    MeasurementBatchBuilder    |
| - getSlot / getSlotLeaders    |   | - Stepped Priority Fees       |
| - Filter by Target Validators |   | - Contended vs Isolated Locks |
| - Predict 4-Slot Windows      |   | - Dry-Run Signature Generator |
+-------------------------------+   +-------------------------------+
                                                     |
                                                     v
                                    +-------------------------------+
                                    |     Safety & Spend Guard      |
                                    | - Dry-run by default          |
                                    | - Hard cap: 0.045 SOL         |
                                    | - Keys isolated in env/volume |
                                    +-------------------------------+
                                                     |
                                                     v
                                    +-------------------------------+
                                    |        Block Analyzer         |
                                    | - getBlock (v1 versioned txs) |
                                    | - Jito Tip Bundle Filter      |
                                    | - Spearman Rank Correlation   |
                                    | - Head vs Tail Fee Tiers      |
                                    +-------------------------------+
```

### Design Considerations Addressed

1. **Leader Schedule Synchronization:**
   The harness queries `getSlotLeaders` to anticipate the 4-slot window assigned to each validator. Dispatch timing targets slot start plus or minus 400 milliseconds.

2. **Network Path and Ingestion:**
   Transactions dispatched via public RPC undergo TPU forwarding (hop from RPC TPU forwarder to leader QUIC port). Direct QUIC dispatch reduces intermediary jitter.

3. **Transaction Interaction and Account Locks:**
   Transactions writing to identical accounts cannot execute concurrently. Our transaction generator creates paired runs:
   - Contended: Batches targeting a common writable account.
   - Isolated: Batches targeting independent ephemeral accounts.

4. **Competition Inside Block (Jito vs Mempool):**
   Validators running Jito-Solana interleave MEV auction bundles at the block head. Our parser isolates transactions interacting with the 8 canonical Jito tip accounts before evaluating the leader scheduler rule.

5. **Noise vs Rule Separation:**
   True scheduler rules appear as monotonic ordering within independent account queues. Inter-queue interleaving represents multi-threaded execution noise.

### What the Experiment Does NOT Separate
- Kernel-level QUIC packet drops occurring prior to UDP socket ingest.
- Internal thread scheduling jitter inside the host operating system kernel.

---

## 3. Quick Start (Reproducibility)

The repository runs in dry-run mode by default with zero network spend.

### Native Execution (Python 3.10+)
```bash
# Run unit tests and trace verification
./run_experiment.sh
```

### Docker Compose (One Command)
```bash
docker-compose up --build
```

---

## 4. Safety Guardrails & Spend Caps

- **Dry-run by default:** `DRY_RUN=true`. All transaction generation and block parsing run locally or against free read-only RPC calls.
- **Hard spend invariant:** `HARD_SPEND_CAP_SOL = 0.045 SOL`. Any broadcast attempting to breach this cap throws an immediate `RuntimeError`.
- **Key isolation:** Keypairs are never committed to git. They must be mounted via Docker volume or referenced by `SOLANA_KEYPAIR_PATH`.

---

## 5. Repository Structure

```
├── Dockerfile                      # Reproducible container definition
├── docker-compose.yml              # One-command execution harness
├── run_experiment.sh               # Execution entrypoint
├── requirements.txt                # Python dependencies
├── README.md                       # Architecture and design documentation
├── REPORT.md                       # Comprehensive empirical research report
├── src/
│   ├── config.py                   # Spend caps and safety gates
│   ├── validators_registry.py      # Curated target validators & Jito tip accounts
│   ├── rpc_client.py               # Resilient JSON-RPC client
│   ├── leader_schedule.py          # Slot window discovery
│   ├── transaction_generator.py    # Stepped fee and lock generator
│   ├── block_analyzer.py           # Ordering and correlation parser
│   └── telemetry_collector.py      # CLI orchestrator
├── data/
│   ├── raw_traces/                 # Raw JSON block traces from Solana Mainnet
│   └── validator_ordering_analysis_results.json
└── tests/
    └── test_telemetry.py           # Zero-dependency unit tests
```
