from flask import Flask, request, render_template, jsonify
import hashlib
from bitcoinlib.wallets import Wallet # Example Bitcoin library (install via pip)

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
        # it might make sense for us to have a "from address" too, 
        # not sure how we are going to handle signing or getting them btc to send from new wallet

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
                
                # Construct the Bitcoin transaction and send it
                wallet = Wallet('MyBitcoinWallet')  # Load your wallet

                tx = wallet.transaction_create(outputs=[(sendto_address, int(sats), 'satoshi')],
                                                script_type='p2sh',
                                                redeem_script=redeem_script_hex)
                
                # Broadcast the transaction and get the txid
                txid = wallet.send(tx)
                funding_txid_big_endian = txid  # Assign the real txid

            except Exception as e:
                error = f"Transaction error: {e}"

    # Render funding transaction page with error or with new txid
    return render_template('funding_transaction.html', txid=funding_txid_big_endian, error=error)