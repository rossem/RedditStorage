from argon2 import PasswordHasher

from base64 import b64decode, b64encode

from Crypto.Cipher import AES
from Crypto import Random as crand
from Crypto.Util.Padding import pad, unpad


class AESCipher(object):
    hasher = PasswordHasher()

    def __init__(self, key: str):
        # self.bs = 32
        # self.key = hashlib.sha256(key.encode('utf-8')).digest() #turns the password into a 32char long key
        self.argon2 = self.hasher.hash(key).split('$')

        # argon2-cffi encodes the values in base64, so we decode it here to get our byte values
        self.salt = b64decode(self.argon2[5] + '==')  # Should be 16 bytes long by default
        self.key = b64decode(self.argon2[5] + '=')  # Should be 32 bytes long

    # encrypts plaintext and generates IV (initialization vector)
    def encrypt(self, plaintext):
        cipher = AES.new(self.key, AES.MODE_GCM)
        return cipher.encrypt_and_digest(plaintext)

    # decrypts ciphertexts
    def decrypt(self, ciphertext, mac_tag):
        cipher = AES.new(self.key, AES.MODE_GCM)
        return cipher.decrypt_and_verify(ciphertext, mac_tag)

    # encrypts a file and returns a comment to be posted
    def encrypt_file(self, file_path):
        with open(file_path, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext)
        # comment = enc.decode('ISO-8859-1').encode('ascii')
        return [b64encode(enc[0]), b64encode(enc[1])]

        # takes in a comment to be posted and decrypts it into a file

    def decrypt_file(self, comment, file_path):
        ciphertext = base64.b64decode(comment)
        # ciphertext = comment.decode('ascii').encode('ISO-8859-1')
        dec = self.decrypt(ciphertext)
        with open(file_path, 'wb') as fo:
            fo.write(dec)
