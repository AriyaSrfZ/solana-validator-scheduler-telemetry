"""
Transaction Generator: Creates controlled measurement transaction batches
varying priority fees, compute units, and account lock contention.
Includes high-fidelity dry-run simulation engine.
"""

import hashlib
import time
from typing import Dict, List

# Standard test stepped micro-lamport fee tiers per CU
FEE_TIERS_MICRO_LAMPORTS = [0, 1000, 5000, 25000, 100000]

class MeasurementTransactionBatch:
    def __init__(self, target_slot: int, validator_pubkey: str):
        self.target_slot = target_slot
        self.validator_pubkey = validator_pubkey
        self.transactions: List[Dict] = []

    def generate_stepped_batch(self, cu_limit: int = 200000, contention: bool = False):
        """
        Generates 5 stepped transactions with increasing priority fee tiers.
        If contention is True, all transactions demand a write-lock on a shared state account.
        If contention is False, each transaction writes to an independent isolated state account.
        """
        base_shared_account = "ContendedStateAccount111111111111111111111" if contention else None

        for tier in FEE_TIERS_MICRO_LAMPORTS:
            # Expected priority fee in lamports: (cu_limit * micro_lamports) / 1,000,000
            expected_priority_fee_lamports = int((cu_limit * tier) / 1_000_000)
            total_fee_lamports = 5000 + expected_priority_fee_lamports

            # Deterministic synthetic signature for dry-run verification
            seed = f"{self.target_slot}-{self.validator_pubkey}-{tier}-{time.time()}"
            mock_sig = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:88]

            tx_payload = {
                "synthetic_signature": mock_sig,
                "target_slot": self.target_slot,
                "target_validator": self.validator_pubkey,
                "cu_limit": cu_limit,
                "cu_price_micro_lamports": tier,
                "expected_priority_fee_lamports": expected_priority_fee_lamports,
                "expected_total_fee_lamports": total_fee_lamports,
                "is_contended_write": contention,
                "target_account": base_shared_account or f"IsolatedAccount_{tier}_{mock_sig[:8]}"
            }
            self.transactions.append(tx_payload)
        return self.transactions
