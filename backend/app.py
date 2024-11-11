import os
import hashlib
from flask import Flask, request, render_template, jsonify
from bitcoinlib.wallets import Wallet
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

app = Flask(__name__)

@app.route("/preimage", methods=['POST', 'GET'])
def preimage():
    funding_txid_big_endian = None
    error = None

    if request.method == 'POST':
        # Get form data
        preimage_text = request.form.get('preimage')
        sendto_address = request.form.get('sendToAddress')
        sats = request.form.get('sats')
        print(f'preimage: {preimage_text}, sendto_address: {sendto_address}, sats: {sats}')
        
        if not preimage_text or not sendto_address or sats is None:
            error = "All fields are required."
        else:
            try:
                # Convert preimage text to bytes and calculate hex and lock
                preimage = preimage_text.encode()
                preimage_hex = preimage.hex()
                lock = hashlib.sha256(preimage).digest()
                lock_hex = lock.hex()

                # Create the locking script in hex format
                redeem_script_hex = f'a820{lock_hex}87'

                # Retrieve the seed from environment variables
                seed = os.getenv('BITCOIN_WALLET_SEED')
                if not seed:
                    raise Exception("Seed not found in environment variables")

                # Load or create a wallet on the testnet
                wallet = Wallet.create(
                    name='MyBitcoinTestnetWallet', 
                    keys=seed, 
                    network='testnet'
                )

                # Create and send the transaction
                tx = wallet.transaction_create(
                    outputs=[(sendto_address, int(sats), 'satoshi')],
                    script_type='p2sh',
                    redeem_script=redeem_script_hex
                )
                
                # Broadcast the transaction and get the txid
                txid = wallet.send(tx)
                funding_txid_big_endian = txid  # Assign the real txid

            except Exception as e:
                error = f"Transaction error: {e}"

    # Render funding transaction page with error or with new txid
    return render_template('funding_transaction.html', txid=funding_txid_big_endian, error=error)

if __name__ == '__main__':
    app.run(debug=True)