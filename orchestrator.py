#!/usr/bin/env python

import os
import re
import sys
from datetime import datetime
from typing import List, Dict, Any


# --- file-type filters: wallet / key / cipher files ------------------

# Extensions / names that look like wallets or key/cipher material
WALLET_KEY_FILENAMES = {
    "wallet.dat",
    "wallet.dat.bak",
    "wallet.bak",
    "electrum.dat",
    "electrum_wallet.dat",
    "keystore",
}

WALLET_KEY_EXTS = {
    ".wallet",
    ".key",
    ".keys",
    ".pem",
    ".pk8",
    ".p12",
    ".pfx",
    ".json",   # keystore jsons
    ".asc",    # armored keys
    ".seed",
    ".sec",
    ".enc",
    ".sc",     # your .sc key files
    ".zowe",   # your zowe-style files
}

# --- regex filters for raw key strings -------------------------------

_WIF_RE = re.compile(r"\b[5KL][1-9A-HJ-NP-Za-km-z]{50,51}\b")
_HEX_PRIV_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")
_XPRV_RE = re.compile(r"\bxprv[1-9A-HJ-NP-Za-km-z]{100,}\b")
_XPUB_RE = re.compile(r"\bxpub[1-9A-HJ-NP-Za-km-z]{100,}\b")


def _scan_text_for_keys(text: str) -> Dict[str, List[str]]:
    found: Dict[str, List[str]] = {
        "wif": [],
        "hex_priv": [],
        "xprv": [],
        "xpub": [],
    }

    for m in _WIF_RE.finditer(text):
        found["wif"].append(m.group(0))

    for m in _HEX_PRIV_RE.finditer(text):
        found["hex_priv"].append(m.group(0))

    for m in _XPRV_RE.finditer(text):
        found["xprv"].append(m.group(0))

    for m in _XPUB_RE.finditer(text):
        found["xpub"].append(m.group(0))

    return found


def _is_wallet_key_file(path: str) -> bool:
    """
    Decide if a file should be treated as a wallet/key/cipher candidate
    based on name or extension.
    """
    base = os.path.basename(path)
    lower = base.lower()
    if lower in WALLET_KEY_FILENAMES:
        return True

    _, ext = os.path.splitext(lower)
    if ext in WALLET_KEY_EXTS:
        return True

    return False


def _walk_filesystem(start_paths: List[str]) -> List[str]:
    """
    Return a list of file paths we want to scan as search filters.
    - ANY wallet/key-like file (by name/ext) is always included.
    - Text-ish files also get scanned for embedded key strings.
    """
    paths: List[str] = []

    for base in start_paths:
        base = os.path.abspath(os.path.expanduser(base))
        if os.path.isfile(base):
            paths.append(base)
            continue
        if not os.path.isdir(base):
            continue

        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", ".venv")]
            for fname in files:
                full = os.path.join(root, fname)
                paths.append(full)

    return paths


def _gather_search_filters() -> Dict[str, List[str]]:
    """
    This is the search engine:
      - find ALL wallet/key/cipher-like files
      - scan text-like stuff for WIF / hexpriv / xprv / xpub
    """
    home = os.path.expanduser("~")
    roots = [os.getcwd(), home]

    files = _walk_filesystem(roots)

    aggregate: Dict[str, List[str]] = {
        "wallet_files": [],
        "key_files": [],
        "wif": [],
        "hex_priv": [],
        "xprv": [],
        "xpub": [],
    }

    for path in files:
        base = os.path.basename(path)

        # Mark every wallet/key/cipher-like file explicitly
        if _is_wallet_key_file(path):
            aggregate["wallet_files"].append(path)

        # Try to scan for embedded keys in text-ish files
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read()
        except Exception:
            # Binary or unreadable, skip text scan but still keep in wallet_files
            continue

        found = _scan_text_for_keys(data)
        for k, v in found.items():
            aggregate[k].extend(v)

    # Deduplicate
    for k in aggregate:
        aggregate[k] = sorted(set(aggregate[k]))

    return aggregate


# --- Blockbook / RICKEY stub (to be wired) ---------------------------

def _check_balance_for_keys(filters: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Here is where Blockbook / RICKEY / PyKryptonite will plug in.

    For now:
      - just echo back counts so you see the pipeline
    """
    summary = {
        "wallet_file_count": len(filters.get("wallet_files", [])),
        "key_file_count": len(filters.get("key_files", [])),
        "wif_count": len(filters.get("wif", [])),
        "hex_priv_count": len(filters.get("hex_priv", [])),
        "xprv_count": len(filters.get("xprv", [])),
        "xpub_count": len(filters.get("xpub", [])),
        "chains": {},
    }
    return summary


def _log_event(password: str, filters: Dict[str, List[str]], balances: Dict[str, Any]):
    timestamp = datetime.utcnow().isoformat() + "Z"
    line = {
        "ts": timestamp,
        "secret_len": len(password),
        "wallet_files": len(filters.get("wallet_files", [])),
        "wif": len(filters.get("wif", [])),
        "hex_priv": len(filters.get("hex_priv", [])),
        "xprv": len(filters.get("xprv", [])),
        "xpub": len(filters.get("xpub", [])),
        "balances": balances,
    }

    try:
        import json

        with open("recovered.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(line) + "\n")
    except Exception:
        pass


# --- entry from btcrecover.py ----------------------------------------

def handle_recovered(password: str) -> None:
    """
    Triggered every time btcrpass.main() finds a password/key.
    """
    print(
        "[*] Trigger fired from btcrecover, building search filters...",
        file=sys.stderr,
    )

    filters = _gather_search_filters()

    print(
        f"[*] Wallet/key-like files: {len(filters['wallet_files'])}",
        file=sys.stderr,
    )
    print(
        f"[*] Raw keys in text: "
        f"{len(filters['wif'])} WIF, "
        f"{len(filters['hex_priv'])} hex priv, "
        f"{len(filters['xprv'])} xprv, "
        f"{len(filters['xpub'])} xpub",
        file=sys.stderr,
    )

    balances = _check_balance_for_keys(filters)
    _log_event(password, filters, balances)

    print(
        f"[+] Event logged. "
        f"WALLET_FILES={balances['wallet_file_count']} "
        f"WIF={balances['wif_count']} "
        f"HEX={balances['hex_priv_count']} "
        f"XPRV={balances['xprv_count']} "
        f"XPUB={balances['xpub_count']}",
        file=sys.stderr,
    )
