from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation
import time

def create_rpc_connection():
    return AuthServiceProxy("http://admin:admin@127.0.0.1:18443")

def get_transfer_amount(limit: Decimal, dest_addr: str) -> Decimal:
    while True:
        try:
            user_input = Decimal(input(f"\nEnter the amount to send from sender to receiver (max {limit} BTC): "))
            if user_input <= Decimal('0'):
                print("Error: Amount must be greater than 0.")
            elif user_input > limit:
                print(f"Error: Amount cannot exceed {limit} BTC.")
            else:
                return user_input
        except InvalidOperation:
            print("Error: Invalid amount. Please enter a numeric value.")

def perform_transfer():
    wallet = "Synergy_Legacy"
    try:
        conn = create_rpc_connection()
        loaded = conn.listwallets()
        if wallet not in loaded:
            conn.loadwallet(wallet)
            print(f"Loaded wallet: {wallet}")
        else:
            print(f"Wallet '{wallet}' is already loaded.")

        conn = create_rpc_connection()
        sender_info = conn.getaddressesbylabel("Sender")
        receiver_info = conn.getaddressesbylabel("Receiver")

        if sender_info:
            sender_addr = list(sender_info.keys())[0]
        else:
            sender_addr = conn.getnewaddress("Sender", "legacy")

        if receiver_info:
            receiver_addr = list(receiver_info.keys())[0]
        else:
            receiver_addr = conn.getnewaddress("Receiver", "legacy")

        print(f"\nSender Address: {sender_addr}\nReceiver Address: {receiver_addr}")

        conn = create_rpc_connection()
        print("\nRetrieving UTXOs for the sender...")
        utxos = conn.listunspent(0, 9999999, [sender_addr])
        if not utxos:
            print(f"No UTXO available for sender address: {sender_addr}")
            return

        utxo = utxos[0]
        print(f"\nSender UTXO details:\nTXID: {utxo['txid']}\nVout: {utxo['vout']}\nAmount: {utxo['amount']} BTC")

        fee = Decimal('0.0001')
        available_funds = utxo["amount"] - fee
        transfer_amount = get_transfer_amount(available_funds, receiver_addr)

        conn = create_rpc_connection()
        print("\nConstructing the transaction from Sender to Receiver ...")
        inputs = [{"txid": utxo["txid"], "vout": utxo["vout"]}]
        outputs = {
            receiver_addr: transfer_amount,
            sender_addr: utxo["amount"] - transfer_amount - fee
        }
        raw_tx = conn.createrawtransaction(inputs, outputs)
        print(f"\nUnsigned raw transaction hex:\n{raw_tx}")

        print("\nSigning the transaction (Sender → Receiver) ...")
        signed_tx = conn.signrawtransactionwithwallet(raw_tx)
        print(f"\nSigned transaction hex:\n{signed_tx['hex']}")

        print("\nBroadcasting the transaction (Sender → Receiver) ...")
        txid = conn.sendrawtransaction(signed_tx["hex"])
        tx_size = len(signed_tx["hex"]) // 2
        print(f"\nTransaction ID (Sender → Receiver): {txid}")
        print(f"Transaction size: {tx_size} vbytes")

        conn = create_rpc_connection()
        print("\nDecoding the signed transaction to retrieve the script...")
        decoded_tx = conn.decoderawtransaction(signed_tx["hex"])
        script_sig = decoded_tx["vin"][0]["scriptSig"]["hex"]
        script_length = len(script_sig) // 2
        print(f"\nExtracted ScriptSig:\n{script_sig}")
        print(f"Script size: {script_length} vbytes")

    except (JSONRPCException, ConnectionError) as exc:
        print(f"Error: {exc}. Retrying...")
        time.sleep(1)
        try:
            conn = create_rpc_connection()
        except Exception as fatal_exc:
            print(f"Fatal error: {fatal_exc}")
    finally:
        try:
            conn = create_rpc_connection()
            conn.unloadwallet(wallet)
            print(f"\nUnloaded wallet: {wallet}")
        except Exception as unload_err:
            print(f"Error unloading wallet: {unload_err}")

if __name__ == "__main__":
    perform_transfer()
