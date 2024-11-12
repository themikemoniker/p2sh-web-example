import os
import hashlib
from flask import Flask, request, render_template, jsonify
from cryptos import Bitcoin
from bitcoinlib.transactions import Transaction
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
                preimage_hex = preimage.hex()
                lock = hashlib.sha256(preimage).digest()
                lock_hex = lock.hex()

                # Create the locking script in hex format
                redeem_script_hex = f'a820{lock_hex}87'

                # Retrieve the seed from environment variables
                seed = os.getenv('BITCOIN_WALLET_SEED')
                if not seed:
                    raise Exception("Seed not found in environment variables")

                # Replace with your actual Electrum seed phrase
                seed_phrase = "wait make private addict outer jar thunder dial drill crisp hollow kiwi"

                # Import the wallet using the existing seed phrase
                wallet = Bitcoin().electrum_wallet(seed_phrase)

                # Create a new transaction object
                tx = Transaction(network='testnet')

                # Add an output to the transaction
                tx.add_output(int(sats), sendto_address)

                # Set the redeem script
                tx.redeem_script = redeem_script_hex

                # Get the private key for the first address
                address = wallet.get_address()  # Default address (0th index address)
                private_key = wallet.get_private_key(address)  # Get the private key for the address

                # Sign the transaction with the private key
                tx.sign(private_key)

                # Serialize the transaction to hex format
                tx_hex = tx.as_hex()

                # Broadcast the transaction by sending it through bitcoinlib network
                network = tx.network  # Network set to 'testnet'
                network.send_raw_transaction(tx_hex)  # This sends the transaction directly

                # Get the transaction ID
                funding_txid_big_endian = tx.txid()

            except Exception as e:
                error = f"Transaction error: {e}"

    # Render funding transaction page with error or with new txid
    return render_template('funding_transaction.html', txid=funding_txid_big_endian, error=error)

if __name__ == '__main__':
    app.run(debug=True)