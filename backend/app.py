import os
import hashlib
from flask import Flask, request, render_template, jsonify
from cryptos import Bitcoin
from dotenv import load_dotenv


# Load environment variables from a .env file if it exists
load_dotenv()

app = Flask(__name__)

# Route to render the transaction form
@app.route("/", methods=['GET'])
def index():
    return render_template('transaction_form.html')

@app.route("/preimage", methods=['POST'])
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
                lock = hashlib.sha256(preimage).digest()
                lock_hex = lock.hex()

                # Create the locking script in hex format
                redeem_script_hex = f'a820{lock_hex}87'

                # Retrieve the seed from environment variables
                seed_phrase = os.getenv('BITCOIN_WALLET_SEED')
                if not seed_phrase:
                    raise Exception("Seed not found in environment variables")

                # Import the wallet using the seed phrase
                bitcoin = Bitcoin(testnet=True)  # Set to testnet
                wallet = bitcoin.electrum_wallet(seed_phrase)

                # Get the private key for the wallet's default address
                private_key = wallet.get_key()  # Get the private key for the first address

                # Create and sign the transaction
                tx = bitcoin.create_p2pkh_transaction(
                    private_key,
                    sendto_address,
                    int(sats),  # Amount in satoshis
                    fee=500  # Specify a transaction fee in satoshis (adjust as needed)
                )

                # Broadcast and get txid
                funding_txid_big_endian = bitcoin.broadcast(tx)

            except Exception as e:
                error = f"Transaction error: {e}"

    # Render funding transaction page with error or with new txid
    return render_template('funding_transaction.html', txid=funding_txid_big_endian, error=error)

if __name__ == '__main__':
    app.run(debug=True)