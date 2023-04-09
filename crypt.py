from argon2 import PasswordHasher

from base64 import b64decode, b64encode

from Crypto.Cipher import AES
from Crypto import Random as crand
from Crypto.Util.Padding import pad, unpad
from typing import Tuple, List, Union


class AESCipher(object):

    # Mainly for internal use. So we don't have to remake this object every encryption/decryption
    hasher = PasswordHasher()

    def __init__(self, key: str):
        """
        Constructor for an AESCipher object
        :param key: The password to use as a key
        """
        # argon2 outputs a single string with all parameters delimited by a '$'
        self.argon2 = self.hasher.hash(key).split('$')

        # argon2-cffi encodes the values in base64, so we decode it here to get our byte values
        self.salt = b64decode(self.argon2[5] + '==')  # Should be 16 bytes long by default
        self.key = b64decode(self.argon2[5] + '=')  # Should be 32 bytes long

    # encrypts plaintext and generates IV (initialization vector)
    def encrypt(self, plaintext: Union[str, bytes]) -> Tuple[bytes, bytes]:
        """
        Returns the AES-GCM-encrypted ciphertext and MAC
        :param plaintext: The plaintext to encrypt
        :return: A Tuple containing [ciphertext, MAC]
        """
        cipher = AES.new(self.key, AES.MODE_GCM)
        return cipher.encrypt_and_digest(plaintext)

    # decrypts ciphertexts
    def decrypt(self, ciphertext: bytes, mac_tag: bytes) -> bytes:
        """
        Returns the decrypted ciphertext
        :param ciphertext: The ciphertext to decrypt
        :param mac_tag: The MAC for the ciphertext
        :return: The decrypted information
        """
        cipher = AES.new(self.key, AES.MODE_GCM)
        return cipher.decrypt_and_verify(ciphertext, mac_tag)

    # encrypts a file and returns a comment to be posted
    def encrypt_file(self, file_path: str) -> Tuple[bytes, bytes]:
        """
        Encrypts a file and returns the ciphertext and associated MAC
        :param file_path: The path to the file to encrypt
        :return: A list containing [ciphertext, MAC]
        """
        with open(file_path, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext)
        # comment = enc.decode('ISO-8859-1').encode('ascii')
        return b64encode(enc[0]), b64encode(enc[1])

        # takes in a comment to be posted and decrypts it into a file

    def decrypt_to_file(self, encrypt_items: Tuple[bytes, bytes], file_path: str):
        """
        Decrypts a file encrypted in AES-GCM and outputs the result to the given filepath
        :parameter encrypt_items: A Tuple containing [ciphertext, MAC]
        :parameter file_path: The file path to output the decrypted file to
        """
        ciphertext = b64decode(encrypt_items[0])
        mac = b64decode(encrypt_items[1])
        # ciphertext = comment.decode('ascii').encode('ISO-8859-1')
        dec = self.decrypt(ciphertext, mac)
        with open(file_path, 'wb') as fo:
            fo.write(dec)
