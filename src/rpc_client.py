"""
JSON-RPC Client for Solana Mainnet with automatic fallback and retry.
"""

import json
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
from .config import DEFAULT_RPC_URLS

class SolanaRpcClient:
    def __init__(self, endpoints: Optional[List[str]] = None):
        self.endpoints = endpoints or DEFAULT_RPC_URLS
        self.current_idx = 0

    def call(self, method: str, params: Optional[List[Any]] = None) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000) % 1000000,
            "method": method,
            "params": params or []
        }
        data = json.dumps(payload).encode("utf-8")

        for attempt in range(len(self.endpoints) * 2):
            endpoint = self.endpoints[self.current_idx]
            req = urllib.request.Request(
                endpoint,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            try:
                res = urllib.request.urlopen(req, timeout=15)
                resp_json = json.loads(res.read().decode("utf-8"))
                if "error" in resp_json:
                    raise RuntimeError(f"RPC Error ({endpoint}): {resp_json['error']}")
                return resp_json.get("result")
            except Exception as e:
                # Rotate endpoint on error
                self.current_idx = (self.current_idx + 1) % len(self.endpoints)
                if attempt == (len(self.endpoints) * 2 - 1):
                    raise RuntimeError(f"All RPC endpoints failed for {method}: {e}")
                time.sleep(0.5)

    def get_slot(self) -> int:
        return self.call("getSlot")

    def get_epoch_info(self) -> Dict[str, Any]:
        return self.call("getEpochInfo")

    def get_slot_leaders(self, start_slot: int, limit: int) -> List[str]:
        return self.call("getSlotLeaders", [start_slot, limit])

    def get_block(self, slot: int, detail: str = "full") -> Optional[Dict[str, Any]]:
        params = [
            slot,
            {
                "encoding": "json",
                "maxSupportedTransactionVersion": 1,
                "transactionDetails": detail,
                "rewards": False
            }
        ]
        try:
            return self.call("getBlock", params)
        except Exception:
            return None
