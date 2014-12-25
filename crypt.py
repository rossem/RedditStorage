import hashlib
import os
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
        with open(os.path.join('saved_files',file_name), 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext)
        #with open(file_name + ".enc", 'wb') as fo:
        #    fo.write(enc)
        comment = base64.b64encode(enc)
        return comment 
        

    def decrypt_file(self, comment, file_name):
        #with open(file_name, 'rb') as fo:
        #    ciphertext = fo.read()
        ciphertext = base64.b64decode(comment)
        dec = self.decrypt(ciphertext)
        with open(os.path.join('saved_files',file_name), 'wb') as fo:
            fo.write(dec)

"""
cipher1 = AESCipher(KEYPASS)

print cipher1.key

encryption = cipher1.encrypt_file("gogo.txt")

#decryption = cipher1.decrypt(encryption)

dog = base64.b64encode(encryption)
print dog
print "hello this is bad"
print base64.b64decode(dog)

"""
