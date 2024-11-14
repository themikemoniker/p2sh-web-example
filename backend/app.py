# general web exerternal dependencies
import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify
# btc external dependencies
import hashlib
from cryptos import Bitcoin
from bitcoinlib.transactions import Transaction
# our project modules
from wallet_utils import generate_testnet_account, check_balance_with_bit

# Load environment variables from a .env file if it exists
load_dotenv()

# Retrieve the seed from environment variables
mnemonic = os.getenv('BITCOIN_WALLET_SEED')
if not mnemonic:
    raise Exception("Seed not found in environment variables")

# Import the wallet using the existing seed phrase
try:
    account = generate_testnet_account(mnemonic)
    print("Address:", account["address"])
    print("Private Key (WIF):", account["private_key_wif"])
    print("Balance: ", check_balance_with_bit(account["private_key_wif"]))
except ValueError as e:
    print(e)

coin = Bitcoin(testnet=True)

app = Flask(__name__)

# Route to render the transaction form
@app.route("/", methods=['GET'])
def index():
    print("DELTA: Rendering transaction form")
    return render_template('transaction_form.html')

@app.route("/preimage", methods=['POST'])
def preimage():
    print("ECHO: Entered preimage route")
    funding_txid_big_endian = None
    error = None
    
    if request.method == 'POST':
        # Get form data
        preimage_text = request.form.get('preimage')
        sendto_address = request.form.get('sendToAddress')
        sats = request.form.get('sats')
        print(f'FOXTROT: Form data received - preimage: {preimage_text}, sendto_address: {sendto_address}, sats: {sats}')
        
        if not preimage_text or not sendto_address or sats is None:
            print("GOLF: Missing required fields")
            error = "All fields are required."
        else:
            try:
                # Convert preimage text to bytes and calculate hex and lock
                print("HOTEL: Encoding preimage and calculating hash")
                preimage = preimage_text.encode()
                preimage_hex = preimage.hex()
                lock = hashlib.sha256(preimage).digest()
                lock_hex = lock.hex()

                # Create the locking script in hex format
                print("INDIA: Creating locking script")
                redeem_script_hex = f'a820{lock_hex}87'

                # Create a new transaction object
                print("JULIET: Creating new transaction")
                tx = Transaction(network='testnet')

                # Add an output to the transaction
                print("KILO: Adding output to transaction")
                tx.add_output(int(sats), sendto_address)

                # Set the redeem script
                print("LIMA: Setting redeem script")
                tx.redeem_script = redeem_script_hex

                # Get the private key for the first address
                print("MIKE: Retrieving private key")
                address1 = wallet.new_receiving_address()  # Default address (0th index address)
                private_key1 = wallet.privkey(address1)  # Get the private key for the address

                # Sign the transaction with the private key
                print("NOVEMBER: Signing transaction")
                tx.sign(private_key1)

                # Serialize the transaction to hex format
                print("OSCAR: Serializing transaction")
                tx_hex = tx.as_hex()



                # Broadcast the transaction by sending it through bitcoinlib network
                network = tx.network  # Network set to 'testnet'
                # network.send_raw_transaction(tx_hex)  # This sends the transaction directly
                coin.pushtx(tx_hex)

                # Get the transaction ID
                funding_txid_big_endian = tx.txid()
                print(f"QUEBEC: Transaction completed with txid: {funding_txid_big_endian}")

            except Exception as e:
                error = f"Transaction error: {e}"
                print(f"ROMEO: Error encountered - {error}")

    # Render funding transaction page with error or with new txid
    print("SIERRA: Rendering funding transaction page")
    return render_template('funding_transaction.html', txid=funding_txid_big_endian, error=error)

if __name__ == '__main__':
    print("TANGO: Starting Flask app")
    app.run(debug=True)