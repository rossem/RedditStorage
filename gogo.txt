import hashlib
from key import *
import base64

from Crypto.Cipher import AES
from Crypto import Random

class AESCipher:
    
    def __init__(self, key):
        #self.bs = 32
        self.key = hashlib.sha256(key).digest()
    
    def pad(self, s):
        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def encrypt(self, plaintext):
        plaintext = self.pad(plaintext)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(plaintext)

    def decrypt(self, ciphertext):
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")
    
    def encrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
        enc = encrypt(plaintext, key)
        with open(file_name + ".enc", 'wb') as fo:
            fo.write(enc)

    def decrypt_file(file_name, key):
        with open(file_name, 'rb') as fo:
            ciphertext = fo.read()
        dec = decrypt(ciphertext, key)
        with open(file_name[:-4], 'wb') as fo:
            fo.write(dec)


"""
cipher1 = AESCipher(KEYPASS)

print cipher1.key

message = "hello this is dog"

encryption = cipher1.encrypt(message)
decryption = cipher1.decrypt(encryption)

print encryption
print decryption
"""


