"""
Configuration and safety parameters for Solana Validator Scheduler Telemetry.
Enforces non-negotiable spend limits, dry-run safety gates, and RPC endpoints.
"""

import os
import sys

DEFAULT_RPC_URLS = [
    os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"),
    "https://solana-rpc.publicnode.com",
    "https://rpc.ankr.com/solana"
]

# Strict spend safety invariant: never exceed 0.05 SOL across an entire run
HARD_SPEND_CAP_SOL = 0.045
DEFAULT_SPEND_LIMIT_SOL = float(os.getenv("SPEND_CAP_SOL", "0.02"))

# Execution safety defaults: DRY RUN BY DEFAULT
DRY_RUN_DEFAULT = os.getenv("DRY_RUN", "true").lower() in ("true", "1", "yes")
LIVE_MODE_ENABLED = os.getenv("SOLANA_LIVE_MODE", "false").lower() in ("true", "1", "yes")

# Key hygiene: never read embedded keys, only external env or volume path
KEYPAIR_PATH = os.getenv("SOLANA_KEYPAIR_PATH", "")

def get_effective_mode():
    """Returns True if live broadcast is permitted, False for dry run."""
    if DRY_RUN_DEFAULT and not LIVE_MODE_ENABLED:
        return "DRY_RUN"
    if LIVE_MODE_ENABLED and not DRY_RUN_DEFAULT:
        if not KEYPAIR_PATH or not os.path.exists(KEYPAIR_PATH):
            raise ValueError(f"Live mode requested but valid keypair not found at: {KEYPAIR_PATH}")
        return "LIVE"
    return "DRY_RUN"

def assert_spend_within_cap(cumulative_lamports_spent: int):
    """Enforces absolute hardware/software cap on transaction fee spend."""
    spent_sol = cumulative_lamports_spent / 1_000_000_000
    if spent_sol >= HARD_SPEND_CAP_SOL:
        raise RuntimeError(
            f"SPEND CAP BREACH: Attempted spend {spent_sol:.4f} SOL exceeds safety invariant {HARD_SPEND_CAP_SOL} SOL."
        )
