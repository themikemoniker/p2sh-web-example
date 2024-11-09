from flask import Flask, request, render_template, jsonify
import hashlib

app = Flask(__name__)

@app.route("/preimage", methods=['POST', 'GET'])
def preimage():
    funding_txid_big_endian = None
    error = None

    if request.method == 'POST':
        # Get form data
        preimage_text = request.form.get('preimage')
        sendToAddress = request.form.get('sendToAddress')
        sats = request.form.get('sats')

        if not preimage_text or not sendToAddress or sats is None:
            error = "All fields are required."
        else:
            # Convert preimage text to bytes and calculate hex and lock
            preimage = preimage_text.encode()
            preimage_hex = preimage.hex()
            lock = hashlib.sha256(preimage).digest()
            lock_hex = lock.hex()

            # Create the locking script in hex format
            redeem_script_hex = f'a820{lock_hex}87'

            # Placeholder for transaction logic
            funding_txid_big_endian = '311d0df1af67b2438a7a030f1a11b76708e96fa6393adfddc19f2579034cd03b'

    # Render the form with either the txid or an error
    return render_template('preimage.html', txid=funding_txid_big_endian, error=error)