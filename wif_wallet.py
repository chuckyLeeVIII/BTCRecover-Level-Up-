#!/usr/bin/env python

"""
Minimal BTC WIF wallet adapter for BTCRecover-Level-Up.

Requirements:
  - BLOCKBOOK_ENDPOINTS["BTC"] set to a working Blockbook-like API.
  - WIF is a standard mainnet BTC key (5, K, or L prefix).

Provides:
  - get_all_addresses(max_gap=1) -> [address]
  - sweep_to(outputs, fee_rate) -> [txid]
"""

import json
import sys
from typing import List, Dict, Any

from blockbook_balance import (
    get_balances_for_addresses,
    BlockbookError,
)
from blockbook_config import BLOCKBOOK_ENDPOINTS

# You can swap this for your own EC/addr lib or PyKryptonite.
from bitcoin import (
    decode_privkey,
    encode_pubkey,
    privkey_to_pubkey,
    pubkey_to_address,
)
from bitcoin import decode_privkey
from bitcoin.wallet import CBitcoinSecret


class WIFWallet:
    def __init__(self, wif: str):
        self.wif = wif
        try:
            self._secret = CBitcoinSecret(wif)
        except Exception as e:
            raise ValueError(f"Invalid WIF: {e}")

    def get_all_addresses(self, max_gap: int = 1) -> List[str]:
        """
        For a single WIF, we just return its one P2PKH address.
        """
        addr = str(self._secret.pub.key.GetAddress())
        return [addr]

    def _fetch_utxos(self) -> List[Dict[str, Any]]:
        """
        Use Blockbook to fetch UTXOs for this WIF's address.
        """
        if "BTC" not in BLOCKBOOK_ENDPOINTS:
            raise RuntimeError("BLOCKBOOK_ENDPOINTS['BTC'] not configured")

        addrs = self.get_all_addresses()
        info = get_balances_for_addresses("BTC", addrs)
        utxos: List[Dict[str, Any]] = []

        for a in info.get("addresses", []):
            raw = a.get("raw", {})
            # Blockbook v2 format: raw["txids"] etc. You may need to
            # adjust this depending on your actual instance.
            # For now we assume there is a "transactions" / "utxo" field:
            for u in raw.get("utxo", []):
                utxos.append(
                    {
                        "txid": u.get("txid"),
                        "vout": int(u.get("vout", 0)),
                        "value": int(u.get("value", 0)),
                        "address": a["address"],
                    }
                )

        return utxos

    def sweep_to(self, outputs: List[Dict[str, Any]], fee_rate: int) -> List[str]:
        """
        Build a single sweep transaction on BTC mainnet:

        - Inputs: all UTXOs for this WIF.
        - Outputs: as provided (user + service fee).
        - fee_rate: sat/vB, approximate.

        Returns list of txids broadcast via Blockbook API.
        """
        utxos = self._fetch_utxos()
        if not utxos:
            print("[*] No UTXOs found for this WIF.", file=sys.stderr)
            return []

        total_in = sum(u["value"] for u in utxos)
        total_out = sum(o["value"] for o in outputs)

        # crude fee estimate: assume 148 bytes per input, 34 per output + 10
        est_vbytes = 148 * len(utxos) + 34 * len(outputs) + 10
        fee = fee_rate * est_vbytes

        if total_out + fee > total_in:
            raise RuntimeError(
                f"Not enough funds: in={total_in} out={total_out} fee~{fee}"
            )

        change = total_in - total_out - fee
        if change > 0:
            # Optional: send change back to user or to fee address.
            # For simplicity, add to user output 0:
            outputs[0]["value"] += change

        # Build raw tx (using python-bitcoinlib or bitcoinlib, adjust to your stack)
        from bitcoin.core import (
            COutPoint,
            CTxIn,
            CTxOut,
            CMutableTransaction,
            lx,
        )
        from bitcoin.wallet import P2PKHBitcoinAddress

        txins = []
        for u in utxos:
            outpoint = COutPoint(lx(u["txid"]), u["vout"])
            txins.append(CTxIn(outpoint))

        txouts = []
        for o in outputs:
            addr = P2PKHBitcoinAddress(o["address"])
            txouts.append(CTxOut(o["value"], addr.to_scriptPubKey()))

        tx = CMutableTransaction(txins, txouts)

        # Sign each input with our WIF
        from bitcoin.core import b2x
        from bitcoin.core.script import SIGHASH_ALL
        from bitcoin.wallet import CBitcoinSecret

        seckey = self._secret
        for i in range(len(txins)):
            # assume all inputs are P2PKH to our address
            from bitcoin.core import Hash160
            from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG

            pubkey = seckey.pub
            script_pubkey = CScript(
                [OP_DUP, OP_HASH160, Hash160(pubkey), OP_EQUALVERIFY, OP_CHECKSIG]
            )

            from bitcoin.core import SignatureHash

            sighash = SignatureHash(script_pubkey, tx, i, SIGHASH_ALL)
            sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])
            txins[i].scriptSig = CScript([sig, pubkey])

        raw_hex = b2x(tx.serialize())

        # Broadcast via Blockbook
        base = BLOCKBOOK_ENDPOINTS["BTC"].rstrip("/")
        url = base + "/api/v2/sendtx/"
        import urllib.request

        data = json.dumps({"hex": raw_hex}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_data = resp.read().decode("utf-8")
                resp_json = json.loads(resp_data)
        except Exception as e:
            raise RuntimeError(f"Broadcast failed: {e}")

        txid = resp_json.get("result") or resp_json.get("txid") or ""
        if not txid:
            raise RuntimeError(f"Unexpected broadcast response: {resp_json}")

        return [txid]
