from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip39MnemonicValidator, Bip44Changes
from bit import PrivateKeyTestnet

def check_balance_with_bit(private_key_wif):
    """
    Fetch the balance of a Bitcoin Testnet address using the bit library.

    Args:
        private_key_wif (str): Private key in WIF format.

    Returns:
        float: Balance in BTC.
    """
    key = PrivateKeyTestnet(private_key_wif)
    return key.get_balance('btc')

def generate_testnet_account(mnemonic):
    """
    Generates a Bitcoin Testnet account from a BIP39 mnemonic.

    Args:
        mnemonic (str): The 12/24-word BIP39 mnemonic.

    Returns:
        dict: A dictionary containing the derived address and private key.
    """
    # Validate the mnemonic
    if not Bip39MnemonicValidator().IsValid(mnemonic):
        raise ValueError("Invalid BIP39 mnemonic. Please provide a valid one.")

    # Generate seed from mnemonic
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    # Initialize the BIP44 HD wallet for Bitcoin Testnet
    bip44_wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN_TESTNET)

    # Derive the first external account (m/44'/1'/0'/0/0)
    account = bip44_wallet.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

    # Return the account details
    return {
        "address": account.PublicKey().ToAddress(),
        "private_key_wif": account.PrivateKey().ToWif()
    }