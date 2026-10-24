"""
Leader Schedule Mapper: Detects validator leader slots and predicts
dispatch timing windows for targeted measurement.
"""

from typing import Dict, List, Optional
from .rpc_client import SolanaRpcClient
from .validators_registry import TARGET_VALIDATORS

class LeaderScheduleTracker:
    def __init__(self, rpc_client: SolanaRpcClient):
        self.rpc = rpc_client

    def find_upcoming_target_slots(self, lookahead_slots: int = 200) -> List[Dict]:
        """
        Scans upcoming slot leaders from the current slot to identify
        arrival windows for the target validators.
        """
        current_slot = self.rpc.get_slot()
        leaders = self.rpc.get_slot_leaders(current_slot, lookahead_slots)
        target_map = {v["node_pubkey"]: v for v in TARGET_VALIDATORS}

        upcoming = []
        for offset, leader_pubkey in enumerate(leaders):
            if leader_pubkey in target_map:
                slot = current_slot + offset
                val_info = target_map[leader_pubkey]
                upcoming.append({
                    "slot": slot,
                    "relative_slot_offset": offset,
                    "estimated_seconds_away": offset * 0.4,
                    "validator": val_info["moniker"],
                    "node_pubkey": leader_pubkey,
                    "client_family": val_info["client_family"],
                    "client_version": val_info["client_version"]
                })
        return upcoming
