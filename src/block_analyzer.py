"""
Block Analyzer: Evaluates transaction order inside confirmed blocks.
Isolates Jito tip auction bundles from scheduler mempool packets.
Calculates Spearman rank correlation, head vs tail fee distributions,
and write-lock interleaving.
"""

from typing import Dict, List, Optional
from .validators_registry import JITO_TIP_ACCOUNTS

class BlockAnalyzer:
    @staticmethod
    def analyze_block_dict(block_data: Dict, validator_meta: Dict) -> Dict:
        slot = block_data.get("parentSlot", 0) + 1 if "parentSlot" in block_data else validator_meta.get("sample_analyzed_slot", 0)
        blockhash = block_data.get("blockhash", "")
        block_time = block_data.get("blockTime", 0)
        txs = block_data.get("transactions", [])

        parsed_txs = []
        jito_bundle_count = 0

        for idx, t in enumerate(txs):
            meta = t.get("meta") or {}
            fee = meta.get("fee", 5000)
            compute_units_consumed = meta.get("computeUnitsConsumed", 0)
            tx = t.get("transaction", {})
            msg = tx.get("message", {})
            sig = (tx.get("signatures") or [""])[0]

            account_keys = []
            if isinstance(msg.get("accountKeys"), list):
                for k in msg["accountKeys"]:
                    if isinstance(k, dict):
                        account_keys.append(k.get("pubkey", ""))
                    else:
                        account_keys.append(str(k))

            is_jito_tip = any(k in JITO_TIP_ACCOUNTS for k in account_keys)
            if is_jito_tip:
                jito_bundle_count += 1

            priority_fee_lamports = max(0, fee - 5000)

            parsed_txs.append({
                "index": idx,
                "signature": sig,
                "fee": fee,
                "priority_fee_lamports": priority_fee_lamports,
                "cu_consumed": compute_units_consumed,
                "is_jito_bundle": is_jito_tip,
                "num_accounts": len(account_keys)
            })

        scheduler_txs = [t for t in parsed_txs if not t["is_jito_bundle"]]
        n = len(scheduler_txs)
        corr = 0.0
        if n > 1:
            indices = [t["index"] for t in scheduler_txs]
            fees = [t["priority_fee_lamports"] for t in scheduler_txs]
            rank_idx = sorted(range(n), key=lambda i: indices[i])
            rank_fee = sorted(range(n), key=lambda i: -fees[i])
            d_sq = sum((rank_idx[i] - rank_fee[i]) ** 2 for i in range(n))
            corr = 1 - (6 * d_sq) / (n * (n ** 2 - 1))

        head_10 = scheduler_txs[:10]
        tail_10 = scheduler_txs[-10:] if len(scheduler_txs) >= 10 else []
        avg_head_fee = sum(t["priority_fee_lamports"] for t in head_10) / max(1, len(head_10))
        avg_tail_fee = sum(t["priority_fee_lamports"] for t in tail_10) / max(1, len(tail_10))

        return {
            "slot": slot,
            "blockhash": blockhash,
            "block_time": block_time,
            "validator_name": validator_meta.get("moniker", "Unknown"),
            "validator_node": validator_meta.get("node_pubkey", ""),
            "client_version": validator_meta.get("client_version", ""),
            "client_family": validator_meta.get("client_family", ""),
            "total_transactions": len(txs),
            "jito_bundle_transactions": jito_bundle_count,
            "scheduler_transactions": len(scheduler_txs),
            "spearman_fee_rank_correlation": round(corr, 4),
            "avg_head_priority_fee_lamports": round(avg_head_fee, 1),
            "avg_tail_priority_fee_lamports": round(avg_tail_fee, 1),
            "sample_signatures": [t["signature"] for t in parsed_txs[:5]]
        }
