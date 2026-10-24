"""
Unit and invariant tests for Solana Validator Scheduler Telemetry.
Uses Python standard library unittest for zero-dependency execution.
"""

import unittest
import os
from src.config import HARD_SPEND_CAP_SOL, assert_spend_within_cap
from src.block_analyzer import BlockAnalyzer
from src.validators_registry import JITO_TIP_ACCOUNTS

class TestValidatorTelemetry(unittest.TestCase):
    def test_hard_spend_cap_invariant(self):
        """Verify that any spend exceeding 0.045 SOL immediately raises a RuntimeError."""
        # Under limit: 0.02 SOL (20,000,000 lamports)
        assert_spend_within_cap(20_000_000)
        
        # At or above limit: 0.05 SOL (50,000,000 lamports)
        with self.assertRaises(RuntimeError):
            assert_spend_within_cap(50_000_000)

    def test_jito_tip_account_isolation(self):
        """Verify known Jito tip accounts are detected to separate bundles from scheduler."""
        self.assertGreaterEqual(len(JITO_TIP_ACCOUNTS), 8)
        sample_tip = "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5"
        self.assertIn(sample_tip, JITO_TIP_ACCOUNTS)

    def test_block_analyzer_spearman_calculation(self):
        """Verify Spearman correlation correctly reflects fee ordering."""
        mock_block = {
            "parentSlot": 100,
            "blockhash": "MockHash11111111111111111111111111111111111",
            "blockTime": 1700000000,
            "transactions": [
                {
                    "meta": {"fee": 105000, "computeUnitsConsumed": 200000},
                    "transaction": {"signatures": ["sig1"], "message": {"accountKeys": ["acc1"]}}
                },
                {
                    "meta": {"fee": 25000, "computeUnitsConsumed": 200000},
                    "transaction": {"signatures": ["sig2"], "message": {"accountKeys": ["acc2"]}}
                },
                {
                    "meta": {"fee": 5000, "computeUnitsConsumed": 200000},
                    "transaction": {"signatures": ["sig3"], "message": {"accountKeys": ["acc3"]}}
                }
            ]
        }
        meta = {"moniker": "TestValidator", "node_pubkey": "TestPubkey", "client_version": "1.0", "client_family": "Test"}
        result = BlockAnalyzer.analyze_block_dict(mock_block, meta)
        self.assertEqual(result["total_transactions"], 3)
        self.assertEqual(result["scheduler_transactions"], 3)
        self.assertGreater(result["spearman_fee_rank_correlation"], 0.9)

if __name__ == "__main__":
    unittest.main()
