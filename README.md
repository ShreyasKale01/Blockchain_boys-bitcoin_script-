# Bitcoin Transaction Demo

This repository demonstrates Bitcoin transactions using both Legacy and SegWit addresses via Python scripts that interact with a Bitcoin node over RPC. The examples illustrate how to create, sign, and broadcast transactions while handling raw transaction decoding and fee management.

## Repository Structure

- **segwit.py**  
  Demonstrates SegWit transactions. This script:
  - Creates or loads a SegWit wallet.
  - Generates new SegWit addresses (labels X, Y, Z).
  - Mines initial blocks to fund an address.
  - Constructs, signs, and broadcasts transactions from address X to Y and Y to Z.
  - Extracts and displays script details (ScriptPubKey and ScriptSig).

- **legacy1.py**  
  Implements a legacy transaction process by:
  - Creating or loading a wallet named `Synergy_Legacy`.
  - Generating legacy addresses for Sender, Receiver, and Change.
  - Mining blocks to fund the sender’s address.
  - Creating, signing, and broadcasting a transaction.
  - Decoding the raw transaction to extract the challenge script.

- **legacy2.py**  
  Provides an alternative legacy transaction example with:
  - Loading the legacy wallet.
  - Retrieving and using addresses by label (Sender and Receiver).
  - Handling UTXO selection and transaction creation.
  - Signing, broadcasting, and decoding the transaction to display the ScriptSig.

## Requirements

- **Python 3.x**
- **bitcoinrpc** library for interacting with Bitcoin's JSON-RPC interface.
- A running Bitcoin node with RPC enabled (typically on regtest mode for testing).
- Proper configuration of the Bitcoin node to allow wallet operations and block generation.

## Installation

1. Clone the repository:  
   `git clone https://github.com/yourusername/bitcoin-transaction-demo.git`  
   `cd bitcoin-transaction-demo`

2. Install dependencies using pip:  
   `pip install python-bitcoinrpc`

3. Configure your Bitcoin node RPC settings to match the credentials (default in scripts: `admin:admin@127.0.0.1:18443`).

## Usage

### Running SegWit Transactions

1. Ensure your Bitcoin node is running.
2. Run the SegWit script:  
   `python segwit.py`  
   The script will:
   - Load or create a wallet named `Synergy_SegWit`.
   - Generate new SegWit addresses and mine blocks to fund transactions.
   - Prompt for transaction amounts between addresses X, Y, and Z.
   - Create, sign, and broadcast transactions, and display decoded transaction details.

### Running Legacy Transactions

There are two legacy examples provided. You can run either:

1. **Using legacy1.py**:  
   `python legacy1.py`  
   This script will:
   - Load or create a wallet named `Synergy_Legacy`.
   - Generate legacy addresses (Sender, Receiver, Change).
   - Fund the sender via mining, create a raw transaction, decode the transaction for the script, sign it, and then broadcast.

2. **Using legacy2.py**:  
   `python legacy2.py`  
   This script offers an alternative workflow:
   - Loads the legacy wallet and retrieves addresses by label.
   - Handles UTXO retrieval and transaction construction.
   - Signs, broadcasts the transaction, and decodes it to extract the ScriptSig.

## Script Details

- **RPC Connection:**  
  Each script establishes a connection to a local Bitcoin node via RPC. Adjust the URL and credentials as necessary.

- **Transaction Construction:**  
  The scripts use the `createrawtransaction`, `signrawtransactionwithwallet`, and `sendrawtransaction` RPC methods to manage the transaction flow.

- **Fee Management:**  
  A constant fee (e.g., `0.0001 BTC`) is subtracted from the UTXO amount to calculate the maximum transferable amount.

- **User Interaction:**  
  The scripts prompt the user to input transaction amounts, validating inputs against available funds.

## Cleanup

After running transactions, the scripts unload the wallets and attempt to clean up wallet files from disk. Ensure you have backups or are operating in a test environment.
