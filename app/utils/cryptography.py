from cryptography.fernet import Fernet
from flask import jsonify


def generate_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    try:
        with open("app/core/secret.key", "wb") as key_file:
            key_file.write(key)
    except Exception as err:
        return jsonify({"msg": "no key file"}), 500


def load_key():
    """
    Loads the key named 'secret.key' from the current directory
    """
    try:
        return open("app/core/secret.key", "rb").read()
    except Exception as err:
        return jsonify({"msg": "no key file"}), 500


def encrypt_text(text):
    """
    Encrypts an input text
    """
    key = load_key()
    f = Fernet(key)

    if not isinstance(text, str):
        raise ValueError("Error : data needs to be a string !")

    encoded_text = text.encode("utf-8")
    encrypted_text = f.encrypt(encoded_text)

    return encrypted_text.decode("utf-8")


def decrypt_text(encrypted_text):
    """
    Decrypts an encrypted text
    """
    if not isinstance(encrypted_text, bytes):
        encrypted_text = encrypted_text.encode("utf-8")

    key = load_key()
    f = Fernet(key)
    decrypted_text = f.decrypt(encrypted_text)

    return decrypted_text.decode("utf-8")
