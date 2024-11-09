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


#                #                           #                       #


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



#                       #                       #                           #




    # Render the form with either the txid or an error
    return render_template('preimage.html', txid=funding_txid_big_endian, error=error)