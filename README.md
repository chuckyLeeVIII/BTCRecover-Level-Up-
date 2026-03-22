# BTCRecover-Level-Up!

> **Trustless by design. Adversarial engineering.**  
> On-chain royalties, off-chain penalties, innocent till inconvenient.

BTCRecover-Level-Up! is the only btcrecover-derived engine that:

- proves ownership before moving funds,
- verifies balances across BTC and compatible chains,
- asks you, UTXO by UTXO, before building a deposit,
- and actually **sends** the funds with smart fee management it it didnt go threw *IT WOULDNT HAVE*.

BTCRecover-Level-up! is a fork of the original
[btcrecover](https://btcrecover.readthedocs.io/) tool, extended and
maintained by **chuckyLeeVIII**. It keeps all of the original wallet
password and seed recovery features and adds a new, opinionated
orchestrator for cross‑chain key discovery and automated recovery.

## Guaranteed Non‑Fail Recovery Design

BTCRecover-Level-Up is designed to be used **together** with my
[AUTO-RBF-BTC-ETH](https://github.com/chuckyLeeVIII/AUTO-RBF-BTC-ETH)
toolchain to create a recovery flow that is engineered not to fail,
under realistic network conditions.

In this combined architecture:

- BTCRecover-lEVEL-uP handles:
  - seed / passphrase / wallet password recovery across supported chains,
  - automated local discovery of wallet, key, and cipher files
    (`wallet.dat`, Electrum wallets, keystores, `.sc`, `.zowe`, etc.),
  - post‑recovery orchestration and logging (`recovered.log`).
- AUTO-RBF-BTC-ETH handles:
  - automated Replace‑By‑Fee (RBF) management for Bitcoin and Ethereum,
  - intelligent fee bumping and rebroadcasting,
  - protection against stuck or under‑funded recovery transactions.

The goal of this integration is simple: **once a valid key or seed is
recovered, the funds will move**, using robust fee management and
rebroadcast logic, not just a single best‑effort transaction attempt.

## What BTCRecover-lEVEL-uP Adds

On top of the original BTCRecover features, this fork adds:

- Automatic local discovery of wallet / key / cipher artifacts.
- A triggerable orchestrator that runs **after a successful recovery**
  to:
  - scan disk for additional key material and wallet files,
  - classify and log potential secrets,
  - (work in progress) query Blockbook / compatible indexers for
    balances.
- Cross‑chain awareness design:
  - given a single key or seed, derive **equivalent accounts** on
    multiple supported chains and check for natural balances there.
- Per‑address interactive recovery:
  - for each address with coins the orchestrator can ask:
    “Do you want to deposit/sweep this one?” and build a plan.
- Integration point for AUTO‑RBF so that properly funded recovery
  transactions confirm.

These advanced features are experimental and specific to this fork; they
are **not** part of the original BTCRecover documented at
https://btcrecover.readthedocs.io/.

## Service and Support Addresses

All automated service fees and support tips for BTCRecover-Advance and
AUTO-RBF-BTC-ETH are sent to:

`1PRQwKHJ4gsZ5Mou3xNkSMrHjBgNbD2E8A`

This is the only address for this fork’s **service fee logic**. It is
declared here and in a dedicated configuration module, and is **not**
hidden deep in the recovery code.

When the advanced orchestrator and AUTO-RBF stack are enabled, a 2%
service fee can be applied to successful recovery withdrawals and paid
to the address above, on top of miner/network fees. You may change or
disable this in your own fork if you do not wish to use the default
service fee behaviour.

## Original BTCRecover Features

BTCRecover-Advance inherits all of the original features from upstream
btcrecover, including:

- Seed/Passphrase Recovery when for: (Recovery without a known address
  requires an [Address Database](docs/Creating_and_Using_AddressDB.md))
  - Avalanche
  - Bitcoin
  - Bitcoin Cash
  - Cardano (Shelley Era Addresses)
  - Dash
  - DigiByte
  - Dogecoin
  - Ethereum
  - Groestlcoin
  - Helium
  - Litecoin
  - Monacoin
  - Ripple
  - Solana
  - Tron
  - Vertcoin
  - Zilliqa
  - And many other “Bitcoin like” cryptos
- [Descrambling 12 word seeds](docs/BIP39_descrambling_seedlists.md)
  (Using Tokenlist feature for BIP39 seeds via `seedrecover.py`)

Wallet File password recovery for a range of wallets

Seed Phrase (Mnemonic) Recovery for the following wallets:

- [Electrum](https://electrum.org/) (1.x, 2.x, 3.x and 4.x)  
  (For Legacy and Segwit Wallets. Set `--bip32-path "m/0'/0"` for a
  Segwit wallet, leave `--bip32-path` blank for Legacy. No support
  for 2FA wallets.)
- [Electron-Cash](https://www.electroncash.org/) (2.x, 3.x and 4.x)
- BIP-32/39 compliant wallets ([bitcoinj](https://bitcoinj.github.io/)),
  including:
  - [MultiBit HD](https://multibit.org/)
  - [Bitcoin Wallet for Android/BlackBerry](https://play.google.com/store/apps/details?id=de.schildbach.wallet)
    (with seeds previously extracted by
    [decrypt_bitcoinj_seeds](https://github.com/gurnec/decrypt_bitcoinj_seed))
  - [Hive for Android](https://play.google.com/store/apps/details?id=com.hivewallet.hive.cordova),
    [for iOS](https://github.com/hivewallet/hive-ios), and
    [Hive Web](https://hivewallet.com/)
  - [Breadwallet](https://brd.com/)
- BIP-32/39/44 Bitcoin & Ethereum compliant wallets, including:
  - [Mycelium for Android](https://wallet.mycelium.com/)
  - [TREZOR](https://www.bitcointrezor.com/)
  - [Ledger](https://www.ledgerwallet.com/)
  - [Keepkey](https://shapeshift.io/keepkey/)
  - [ColdCard](https://coldcardwallet.com/)
  - [Jaxx](https://jaxx.io/)
  - [Coinomi](https://www.coinomi.com/)
  - [Exodus](https://www.exodus.io/)
  - [MyEtherWallet](https://www.myetherwallet.com/)
  - [Bither](https://bither.net/)
  - [Blockchain.com](https://blockchain.com/wallet)

Bitcoin wallet password recovery support for:

- [Bitcoin Core](https://bitcoincore.org/)
- [MultiBit HD](https://multibit.org/) and
  [MultiBit Classic](https://multibit.org/help/v0.5/help_contents.html)
- [Electrum](https://electrum.org/) (1.x, 2.x, 3.x and 4.x)  
  (For Legacy and Segwit Wallets. Set `--bip32-path "m/0'/0"` for a
  Segwit wallet, leave bip32-path blank for Legacy. No support for
  2FA wallets.)
- Most wallets based on [bitcoinj](https://bitcoinj.github.io/),
  including [Hive for OS X](https://github.com/hivewallet/hive-mac/wiki/FAQ)
- BIP-39 passphrases (Also supports all cryptos supported for seed
  recovery, as well as recovering “Extra Words” for Electrum seeds)
- [mSIGNA (CoinVault)](https://ciphrex.com/products/)
- [Blockchain.com](https://blockchain.com/wallet)
- [pywallet --dumpwallet](https://github.com/jackjack-jj/pywallet) of
  Bitcoin Unlimited/Classic/XT/Core wallets
- [Bitcoin Wallet for Android/BlackBerry](https://play.google.com/store/apps/details?id=de.schildbach.wallet)
  spending PINs and encrypted backups
- [KnC Wallet for Android](https://github.com/kncgroup/bitcoin-wallet)
  encrypted backups
- [Bither](https://bither.net/)

Altcoin password recovery support for most wallets derived from one of
those above, including:

- [Coinomi](https://www.coinomi.com/en/) (Only supports password
  protected wallets)
- [Metamask](https://metamask.io/) (And Metamask clones like Binance
  Chain Wallet, Ronin Wallet, etc.)
- [Litecoin Core](https://litecoin.org/)
- [Electrum-LTC](https://electrum-ltc.org/) (For Legacy and Segwit
  Wallets. Set `--bip32-path "m/0'/0"` for a Segwit wallet, leave
  bip32-path blank for Legacy. No support for 2FA wallets.)
- [Electron-Cash](https://www.electroncash.org/) (2.x, 3.x and 4.x)
- [Litecoin Wallet for Android](https://litecoin.org/) encrypted backups
- [Dogecoin Core](http://dogecoin.com/)
- [MultiDoge](http://multidoge.org/)
- [Dogechain.info](https://dogechain.info/)
- [Dogecoin Wallet for Android](http://dogecoin.com/) encrypted backups
- [Yoroi Wallet for Cardano](https://yoroi-wallet.com/#/)
  Master_Passwords extracted from the wallet data (In browser or on
  rooted/jailbroken phones)
- [Encrypted (BIP-38) Paper Wallet Support (Eg: From Bitaddress.org)](https://bitaddress.org)
  Also works with altcoin forks like liteaddress.org, paper.dash.org,
  etc…
- Brainwallets
- Sha256(Passphrase) brainwallets (eg: Bitaddress.org, liteaddress.org,
  paper.dash.org)
- sCrypt Secured Brainwallets (Eg: Warpwallet, Memwallet)
- [Ethereum UTC Keystore Files](https://myetherwallet.com/) Ethereum
  Keystore files, typically used by wallets like MyEtherWallet,
  MyCrypto, etc. (Also often used by Eth clones like Theta, etc)

Other capabilities:

- [Free and Open Source](http://en.wikipedia.org/wiki/Free_and_open-source_software)
  – anyone can download, inspect, use, and redistribute this software
- Supported on Windows, Linux, and OS X
- Support for Unicode passwords and seeds
- Multithreaded searches, with user-selectable thread count
- Ability to spread search workload over multiple devices
- [GPU acceleration](docs/GPU_Acceleration.md) for Bitcoin Core
  Passwords, Blockchain.com (Main and Second Password), Electrum
  Passwords + BIP39 and Electrum Seeds
- Wildcard expansion for passwords
- Typo simulation for passwords and seeds
- Progress bar and ETA display (at the command line)
- Optional autosave – interrupt and continue password recoveries
  without losing progress
- Automated seed recovery with a simple graphical user interface
- Ability to search multiple derivation paths simultaneously for a
  given seed via `--pathlist` command (example pathlist files in the
  docs)

“Offline” mode for nearly all supported wallets – use one of the
[extract scripts (click for more information)](docs/Extract_Scripts.md)
to extract just enough information to attempt password recovery, without
giving btcrecover or whoever runs it access to any of the addresses or
private keys in your Bitcoin wallet.

## Setup and Usage Tutorials

BTCRecover is a Python (3.6, 3.7, 3.8, 3.9) script so will run on
Windows, Linux and Mac environments.
[See the installation guide for more info](docs/INSTALL.md).

[I have created a growing playlist](https://www.youtube.com/watch?v=kMUx_uFDHYM&t=15s)
that covers a number of usage examples for using this tool to recover
seed phrases, BIP39 passphrases, etc.

This repository also includes some example commands and file templates
in the `./docs/` folder of the repository.

My suggestion is that you find a scenario that is most-like your
situation and try to replicate my examples to ensure that you have the
tool set up and running correctly. If you have a specific situation that
isn't covered in these tutorials, let me know and I can look into
creating a video for that.

If you don't know an address in the wallet that you are searching for,
you can create and use an
[Address Database (click here for guide)](docs/Creating_and_Using_AddressDB.md).

*There is no real performance penalty for doing this, it just takes a
bit more work to set up.*

## Quick Start

To try recovering your password or a BIP39 passphrase, please start with
the **[Password Recovery Quick Start](docs/TUTORIAL.md#btcrecover-tutorial)**.

If you mostly know your recovery seed/mnemonic (12–24 recovery words),
but think there may be a mistake in it, please see the
**[Seed Recovery Quick Start](docs/Seedrecover_Quick_Start_Guide.md)**.

## Thanks to Gurnec

This tool builds on the original work of Gurnec who created it and
maintained it until late 2017. If you find *btcrecover* helpful, please
consider a small donation to them too. (I will also be passing on a
portion of any tips I receive at the addys above to them too.)

![Donate Bitcoin](docs/Images/gurnec-donate-btc-qr.png)  
BTC: `3Au8ZodNHPei7MQiSVAWb7NB2yqsb48GW4`

**Thank You!**
