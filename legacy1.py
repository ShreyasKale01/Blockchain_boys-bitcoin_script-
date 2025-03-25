from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation
import time

def rpc_connect():
    """Establish and return an RPC connection."""
    return AuthServiceProxy("http://admin:admin@127.0.0.1:18443")

def prompt_amount(max_funds: Decimal, destination: str) -> Decimal:
    """Prompt the user to enter an amount within allowed limits."""
    while True:
        try:
            amt = Decimal(input(f"\nEnter the amount to send (max {max_funds} BTC) from sender to receiver: "))
            if amt <= Decimal('0'):
                print("Error: Amount must be greater than 0.")
            elif amt > max_funds:
                print(f"Error: Amount cannot exceed {max_funds} BTC.")
            else:
                return amt
        except InvalidOperation:
            print("Error: Invalid amount. Please enter a numeric value.")

def execute_transaction():
    """Perform a Bitcoin transaction using RPC calls."""
    wallet_name = "Synergy_Legacy"
    try:
        conn = rpc_connect()
        # Load or create wallet
        try:
            conn.loadwallet(wallet_name)
            print(f"Loaded wallet: {wallet_name}")
        except JSONRPCException:
            conn.createwallet(wallet_name)
            print(f"Created wallet: {wallet_name}")

        # Generate legacy addresses
        conn = rpc_connect()
        sender_addr = conn.getnewaddress("Sender", "legacy")
        receiver_addr = conn.getnewaddress("Receiver", "legacy")
        change_addr = conn.getnewaddress("Change", "legacy")
        print(f"\nLegacy Addresses:\nSender: {sender_addr}\nReceiver: {receiver_addr}\nChange: {change_addr}")

        # Fund sender address by mining blocks
        print("\nMining some initial blocks to fund sender address ...\n")
        conn.generatetoaddress(101, sender_addr)
        balance = conn.getbalance()
        print(f"Balance of Sender: {balance} BTC")

        # Select UTXO from the sender address
        conn = rpc_connect()
        utxos = conn.listunspent(1, 9999999, [sender_addr])
        utxo = utxos[0]
        print(f"UTXO of Sender: {utxo['amount']} BTC")

        fee = Decimal('0.0001')
        available_amount = utxo["amount"] - fee
        send_amt = prompt_amount(available_amount, receiver_addr)

        # Create raw transaction
        print("\nCreating a raw transaction from Sender to Receiver ...")
        conn = rpc_connect()
        inputs = [{"txid": utxo["txid"], "vout": utxo["vout"]}]
        outputs = {
            receiver_addr: send_amt,
            sender_addr: utxo["amount"] - send_amt - fee
        }
        raw_tx = conn.createrawtransaction(inputs, outputs)
        print(f"\nUnsigned raw transaction hex: \n{raw_tx}")

        # Decode raw transaction and extract script
        print("\nDecoding raw transaction to extract the challenge script ...")
        decoded = conn.decoderawtransaction(raw_tx)
        script_hex = decoded["vout"][0]["scriptPubKey"]["hex"]
        script_size = len(script_hex) // 2
        print(f"\nExtracted ScriptPubKey: {script_hex}")
        print(f"Script size: {script_size} vbytes")

        # Sign the transaction
        print("\nSigning the transaction from Sender to Receiver ...")
        signed_tx = conn.signrawtransactionwithwallet(raw_tx)
        print(f"\nSigned transaction hex: \n{signed_tx['hex']}")

        # Broadcast the transaction
        print("\nBroadcasting the transaction from Sender to Receiver ...")
        tx_id = conn.sendrawtransaction(signed_tx["hex"])
        tx_size = len(signed_tx["hex"]) // 2
        print(f"\nTransaction ID (Sender → Receiver): {tx_id}")
        print(f"Transaction size: {tx_size} vbytes")

    except (JSONRPCException, ConnectionError) as err:
        print(f"Error: {err}. Retrying...")
        time.sleep(1)
        try:
            conn = rpc_connect()
        except Exception as fatal_err:
            print(f"Fatal error: {fatal_err}")

    finally:
        try:
            conn = rpc_connect()
            conn.unloadwallet(wallet_name)
            print(f"\nUnloaded wallet: {wallet_name}")
        except Exception as unload_err:
            print(f"Error unloading wallet: {unload_err}")

if __name__ == "__main__":
    execute_transaction()
