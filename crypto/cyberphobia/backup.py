from Crypto.Cipher import AES


def encrypt(message, key):
    cipher = AES.new(key, AES.MODE_CTR, nonce=b"ghost123", initial_value=0)
    return cipher.encrypt(message.ljust(64, b" "))
