#!/usr/bin/env python

"""
Ownership / sweep flow with 2% service fee applied to withdrawals.

This module expects a wallet-like object with:
    - get_all_addresses(max_gap: int) -> List[str]
    - sweep_to(outputs: List[dict], fee_rate: int) -> List[str]
and a BalanceResult-style object summarizing balances.
"""

from typing import List, Dict, Any, Optional

from fees_config import (
    FEE_BENEFICIARY,
    SERVICE_FEE_RATE,
    validate_fee_config,
)


def _prompt_yes_no(question: str, default: Optional[bool] = None) -> bool:
    while True:
        suffix = " [y/n] " if default is None else (" [Y/n] " if default else " [y/N] ")
        ans = input(question + suffix).strip().lower()
        if not ans and default is not None:
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False


def _select_destination() -> str:
    dest = input("Enter destination address (your new safe wallet): ").strip()
    if not dest:
        raise ValueError("No destination address provided.")
    return dest


def _select_fee_rate() -> int:
    fee_rate_str = input("Enter miner fee rate in sat/vB (default 5): ").strip()
    fee_rate = 5
    if fee_rate_str:
        try:
            fee_rate = int(fee_rate_str)
        except ValueError:
            pass
    return fee_rate


def _collect_utxos_from_balances(balances: Any) -> List[Dict[str, Any]]:
    """
    Flatten UTXOs from a BalanceResult-like object into a simple list:
        [{ 'chain': str, 'address': str, 'value': int, 'txid': str, 'vout': int }, ...]
    """
    utxos: List[Dict[str, Any]] = []
    for chain_balance in balances.chains:
        for addr in chain_balance.addresses:
            for u in addr.utxos:
                utxos.append(
                    {
                        "chain": chain_balance.chain,
                        "address": addr.address,
                        "value": int(u.get("value", 0)),
                        "txid": u.get("txid"),
                        "vout": int(u.get("vout", 0)),
                    }
                )
    return utxos


def ownership_flow_with_fee(event: Any, balances: Any) -> None:
    """
    event: RecoveryEvent-like object with event.wallet, event.candidate, etc.
    balances: BalanceResult-like object with chains / addresses / utxos.
    """
    validate_fee_config()

    total = balances.total_balance_sats
    if not total:
        print("[*] No balance to recover.")
        return

    print("\n=== Recovered balance summary ===")
    for chain_balance in balances.chains:
        if not chain_balance.total_balance_sats:
            continue
        print(f"Chain: {chain_balance.chain}")
        print(f"  Total: {chain_balance.total_balance_sats} sats")
        for addr in chain_balance.addresses:
            if addr.balance_sats:
                print(f"    {addr.address}: {addr.balance_sats} sats")

    print(f"\nTotal balance across all chains: {total} sats")

    utxos = _collect_utxos_from_balances(balances)
    if not utxos:
        print("[*] No explicit UTXOs in balance object; cannot build sweep plan.")
        return

    print("\nYou can choose which UTXOs to sweep.")
    selected: List[Dict[str, Any]] = []
    for u in utxos:
        desc = f"{u['chain']} {u['address']} {u['value']} sats (txid {u['txid']}:{u['vout']})"
        if _prompt_yes_no(f"Sweep this output? {desc}", default=True):
            selected.append(u)

    if not selected:
        print("[*] No UTXOs selected for sweep.")
        return

    sel_total = sum(u["value"] for u in selected)
    fee_service = int(sel_total * SERVICE_FEE_RATE)
    user_amount = sel_total - fee_service

    if user_amount <= 0:
        print("[-] Selected amount too small after 2% service fee.")
        return

    print("\n=== Sweep plan ===")
    print(f"Selected total: {sel_total} sats")
    print(f"Service fee @ {SERVICE_FEE_RATE * 100:.2f}%: {fee_service} sats")
    print(f"User amount: {user_amount} sats")
    print(f"Beneficiary address (service fee): {FEE_BENEFICIARY}")

    if not _prompt_yes_no("Do you accept this plan and want to build the sweep?", default=False):
        print("[*] User cancelled sweep.")
        return

    try:
        dest_user = _select_destination()
    except ValueError as e:
        print(f"[-] {e}")
        return

    fee_rate = _select_fee_rate()

    outputs = [
        {"address": dest_user, "value": user_amount},
        {"address": FEE_BENEFICIARY, "value": fee_service},
    ]

    print("\n[*] Building and broadcasting sweep transactions...")
    try:
        txids: List[str] = event.wallet.sweep_to(outputs=outputs, fee_rate=fee_rate)
    except NotImplementedError:
        print("[-] sweep_to(outputs, fee_rate) not implemented for this wallet type.")
        return
    except Exception as e:
        print(f"[-] Sweep failed: {e}")
        return

    if not txids:
        print("[-] No transactions created for sweep.")
        return

    print("[+] Sweep transactions broadcast:")
    for txid in txids:
        print(f"  {txid}")
