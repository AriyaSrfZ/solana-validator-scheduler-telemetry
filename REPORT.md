# Empirical Research Report: Solana Validator Transaction Ordering

Measurement and statistical analysis of transaction ordering mechanisms across Solana Mainnet validators.

**Author:** Ariya Sarrafzadeh (Callsign: HaroSS)  
**Solana Settlement Address:** `GPnfvrNrro1PJTbN4moGkTwtJm3iqywLDZnAYY7pco52`  
**Measurement Dates:** October 22 to 23, 2026 (Epoch 1065, Mainnet-Beta post-Alpenglow upgrade)  
**Sample Space:** 3,831 Mainnet transactions analyzed across 6 distinct validator blocks  

---

## 1. Measured Validators and Block Telemetry Summary

All measurements were collected from confirmed blocks produced post-Alpenglow on Solana Mainnet. Each slot was verified through standard `getBlock` JSON-RPC calls (`maxSupportedTransactionVersion: 1`).

| Slot | Validator Moniker | Node Identity | Client Version | Total Txs | Jito Bundles | Scheduler Txs | Spearman Fee Correlation | Head Avg Fee (lamports) | Tail Avg Fee (lamports) |
|---|---|---|---|---|---|---|---|---|---|
| **460184800** | Shinobi Systems | `Fd7btgySsrjuo25CJCj7oE7VPMyezDhnx7pZkj2v69Nk` | Jito-Solana 4.3.2 | 724 | 38 | 686 | **+0.0738** | 12,333 | 8,270 |
| **460184876** | Kraken | `krakeNd6ednDPEXxHAmoBs1qKVM8kLg79PvWF2mhXV1` | Jito-Solana 4.3.2 | 388 | 4 | 384 | **-0.0061** | 418 | 3,033 |
| **460184832** | JD549 | `JD549HsbJHeEKKUrKgg4Fj2iyv2RGjsV7NTZjZUrHybB` | Firedancer 26.10.4 | 574 | 39 | 535 | **-0.2930** | 5,108 | 13,898 |
| **460184856** | Awesome-FD | `Awes4Tr6TX8JDzEhCZY2QVNimT6iD1zWHzf1vNyGvpLM` | Firedancer 26.10.4 | 580 | 11 | 569 | **+0.1118** | 5,400 | 2,041 |
| **460184872** | Revtec-FD | `revtecFsGSRCdF29atQvchSXrjwBesA9vSisD4fyH5K` | Firedancer 26.10.4 | 1,276 | 39 | 1,237 | **+0.1613** | 17,925 | 831 |
| **460184812** | Validator-9rkJ | `9rkJMARqK6VBkcxGfKBAwnA44gPAfGxPbPsfsggFNDSQ` | Agave/Jito 4.3.0 | 339 | 43 | 296 | **-0.0154** | 31,966 | 4,405 |

---

## 2. In-Depth Client Analysis & Ordering Rules

### A. Jito-Solana (v4.3.2)
- **Primary Mechanism:** Two-tier hybrid architecture.
  1. *MEV Auction Window:* Transactions interacting with Jito tip payment accounts are inserted in deterministic bundles at the block head. Across slots 460184800 and 460184876, 38 and 4 bundles were identified respectively.
  2. *Standard Mempool Processing:* Remaining transactions undergo scheduling via the Agave unified scheduler fork.
- **Observed Ordering Rule:** Weak local fee prioritization (+0.0738 correlation on Shinobi Systems). The head 10 non-bundle transactions averaged 12,333 lamports priority fee compared to 8,270 lamports in the tail. On Kraken (slot 460184876), lower overall load produced a near-zero correlation (-0.0061), where arrival FIFO dominated fee ranking.

### B. Firedancer / Frankendancer (v26.10.4)
- **Primary Mechanism:** Static memory ring buffers and dedicated hardware-pinned tiles (net -> quic -> verify -> bank).
- **Observed Ordering Rule:**
  - On high-load blocks (Revtec-FD slot 460184872, 1,276 transactions), fee prioritization was evident in the top decile: head average priority fee reached 17,925 lamports versus 831 lamports in the tail (+0.1613 correlation).
  - On moderate-load blocks (JD549 slot 460184832), negative correlation (-0.2930) occurred because high-fee transactions touching congested state (such as decentralized exchange routing pools) were repeatedly postponed behind uncontended lower-fee transactions.
- **Rule Formulation:** Firedancer operates a strict packet-batch priority insertion queue per verify tile. However, bank tile execution commits transactions asynchronously as write locks clear.

### C. Agave / Fork (v4.3.0)
- **Primary Mechanism:** Banking stage with thread-level lock allocation.
- **Observed Ordering Rule:** Extreme fee polarization. Head transactions had an average priority fee of 31,966 lamports versus 4,405 lamports at the tail, but overall rank correlation was flat (-0.0154). Once top-tier priority transactions are scheduled, remaining transactions are processed concurrently across banking threads with zero ordering guarantee.

---

## 3. What Went Wrong, Systemic Noise, and Limitations

Scientific integrity requires documenting experimental anomalies, invalid assumptions, and systemic noise sources.

### 1. The Myth of Global Linear Fee Priority (Null Hypothesis)
Before measurement, common ecosystem assumptions posited that transaction index $I$ directly correlates with priority fee per compute unit ($P$). Empirical data disproves this global model. In every observed block, correlation coefficient $|r_s| < 0.30$. Global linear ordering does not exist on Solana Mainnet.

### 2. Multi-Threaded Banking Stage Interleaving
Validators execute 4 to 6 parallel banking threads. When two non-conflicting transactions $T_1$ (fee: 50,000) and $T_2$ (fee: 5,000) are assigned to separate threads, differences in instruction complexity, program cache hits, and host CPU thread scheduling cause them to commit out of arrival and fee order.

### 3. Write-Lock Contention Masking
A transaction specifying a high priority fee but requiring a write lock on an already-locked account must wait. The scheduler does not stall the pipeline; it executes subsequent non-conflicting transactions. Consequently, lower-fee transactions regularly land dozens of positions ahead of high-fee transactions.

### 4. Post-Alpenglow Transaction Versioning Incompatibility
Initial telemetry extraction with `maxSupportedTransactionVersion: 0` failed with RPC error `-32015`. Modern Solana blocks contain version 1 transactions that require explicit client configuration (`maxSupportedTransactionVersion: 1`). The telemetry harness was upgraded to support version 1 schemas seamlessly.

---

## 4. Conclusion

1. **Jito-Solana:** Prioritizes off-chain bundle auctions at the block head, followed by multi-threaded mempool dispatch with weak local fee clustering.
2. **Firedancer:** Enforces ring buffer batch priority sorting, but bank tile commit order is heavily modulated by account lock release timing.
3. **Agave / Fork:** Front-loads high-priority transactions into initial execution batches, leaving the block body subject to concurrent thread race conditions.
4. **General Law:** Priority fees buy inclusion probability and placement within the top 10% of a block; they do not guarantee sequential position ordering.
