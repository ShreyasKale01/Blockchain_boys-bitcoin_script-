from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation
import os
import shutil

def create_rpc_connection(wallet: str = None):
    """
    Create an RPC connection to the Bitcoin node.
    If a wallet name is provided, connect to that wallet.
    """
    base_url = "http://admin:admin@127.0.0.1:18443"
    if wallet:
        return AuthServiceProxy(f"{base_url}/wallet/{wallet}")
    return AuthServiceProxy(base_url)

def prompt_amount(max_amount: Decimal, tx_pair: tuple) -> Decimal:
    """
    Prompt the user to enter an amount to transfer between two addresses.
    The tx_pair tuple holds the names (or labels) of the sender and receiver.
    """
    while True:
        try:
            amount = Decimal(input(
                f"\nEnter the amount to send from {tx_pair[0]} to {tx_pair[1]} (max {max_amount} BTC): "
            ))
            if amount <= Decimal('0'):
                print("Error: Amount must be greater than 0.")
            elif amount > max_amount:
                print(f"Error: Amount cannot exceed {max_amount} BTC.")
            else:
                return amount
        except InvalidOperation:
            print("Error: Invalid amount. Please enter a numeric value.")

def run_wallet_operations():
    wallet = "Synergy_SegWit"
    root_conn = create_rpc_connection()
    
    try:
        # Load or create the wallet
        if wallet in root_conn.listwallets():
            root_conn.loadwallet(wallet)
            print(f"Loaded wallet: {wallet}")
        else:
            root_conn.createwallet(wallet)
            print(f"Created wallet: {wallet}")

        # Connect directly to the wallet
        conn = create_rpc_connection(wallet)
        
        # Generate SegWit addresses for labels X, Y, Z
        addr_X = conn.getnewaddress("X", "p2sh-segwit")
        addr_Y = conn.getnewaddress("Y", "p2sh-segwit")
        addr_Z = conn.getnewaddress("Z", "p2sh-segwit")
        print(f"\nSegWit Addresses:\nX: {addr_X}\nY: {addr_Y}\nZ: {addr_Z}")

        # Fund address X by mining initial blocks
        print("\nMining initial blocks to fund address X ...")
        create_rpc_connection(wallet).generatetoaddress(101, addr_X)
        
        conn = create_rpc_connection(wallet)
        utxo_X = conn.listunspent(1, 9999999, [addr_X])[0]
        balance_X = conn.getbalance()
        print(f"\nBalance of X: {balance_X} BTC")
        print(f"UTXO of X: {utxo_X['amount']} BTC")

        fee = Decimal('0.0001')
        max_send_XY = utxo_X["amount"] - fee
        send_amt_XY = prompt_amount(max_send_XY, ("X", "Y"))

        # Create and decode raw transaction from X to Y
        print("\nCreating raw transaction from X to Y ...")
        inputs_XY = [{"txid": utxo_X["txid"], "vout": utxo_X["vout"]}]
        outputs_XY = {
            addr_Y: send_amt_XY,
            addr_X: utxo_X["amount"] - send_amt_XY - fee
        }
        raw_tx_XY = conn.createrawtransaction(inputs_XY, outputs_XY)
        
        print("\nDecoding transaction X → Y to extract challenge script ...")
        decoded_XY = conn.decoderawtransaction(raw_tx_XY)
        script_pub_key = decoded_XY["vout"][0]["scriptPubKey"]["hex"]
        script_length = len(script_pub_key) // 2
        print(f"\nExtracted ScriptPubKey: {script_pub_key}")
        print(f"Script size: {script_length} vbytes")

        # Sign and broadcast the transaction from X to Y
        print("\nSigning transaction X → Y ...")
        signed_tx_XY = conn.signrawtransactionwithwallet(raw_tx_XY)
        print("\nBroadcasting transaction X → Y ...")
        txid_XY = conn.sendrawtransaction(signed_tx_XY["hex"])
        decoded_signed_XY = conn.decoderawtransaction(signed_tx_XY["hex"], True)
        tx_vsize_XY = decoded_signed_XY["vsize"]
        print(f"\nTransaction ID (X → Y): {txid_XY}")
        print(f"Transaction size: {tx_vsize_XY} vbytes")
        
        # Mine one more block to confirm the transaction
        create_rpc_connection(wallet).generatetoaddress(1, addr_X)

        # Process transaction from Y to Z
        print("\nFetching UTXO for Y ...")
        utxo_Y = conn.listunspent(1, 9999999, [addr_Y])[0]
        print(f"\nUTXO of Y:\nTXID: {utxo_Y['txid']}\nVout: {utxo_Y['vout']}\nAmount: {utxo_Y['amount']} BTC")

        max_send_YZ = utxo_Y["amount"] - fee
        send_amt_YZ = prompt_amount(max_send_YZ, ("Y", "Z"))

        print("\nCreating raw transaction from Y to Z ...")
        inputs_YZ = [{"txid": utxo_Y["txid"], "vout": utxo_Y["vout"]}]
        outputs_YZ = {
            addr_Z: send_amt_YZ,
            addr_Y: utxo_Y["amount"] - send_amt_YZ - fee
        }
        raw_tx_YZ = conn.createrawtransaction(inputs_YZ, outputs_YZ)
        
        print("\nSigning transaction Y → Z ...")
        signed_tx_YZ = conn.signrawtransactionwithwallet(raw_tx_YZ)
        
        print("\nBroadcasting transaction Y → Z ...")
        txid_YZ = conn.sendrawtransaction(signed_tx_YZ["hex"])
        decoded_signed_YZ = conn.decoderawtransaction(signed_tx_YZ["hex"], True)
        tx_vsize_YZ = decoded_signed_YZ["vsize"]
        print(f"\nTransaction ID (Y → Z): {txid_YZ}")
        print(f"Transaction size: {tx_vsize_YZ} vbytes")
        
        print("\nDecoding transaction Y → Z to extract response script ...")
        decoded_YZ = conn.decoderawtransaction(signed_tx_YZ["hex"])
        script_sig = decoded_YZ["vin"][0]["scriptSig"]["hex"]
        script_sig_length = len(script_sig) // 2
        print(f"\nExtracted ScriptSig: {script_sig}")
        print(f"Script size: {script_sig_length} vbytes")
    
    except JSONRPCException as error:
        print(f"Error: {error}")
    
    finally:
        try:
            root_conn.unloadwallet(wallet)
            print(f"\nUnloaded wallet: {wallet}")
            # Remove wallet files from disk if they exist
            wallet_dir = os.path.join(
                os.getenv('APPDATA'),
                'Bitcoin',
                'regtest',
                'wallets',
                wallet
            )
            if os.path.exists(wallet_dir):
                shutil.rmtree(wallet_dir)
        except Exception:
            print("Cleanup failed.")

if __name__ == "__main__":
    run_wallet_operations()
