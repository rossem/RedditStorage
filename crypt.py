import hashlib
from key import *
from Crypto.Cipher import AES
from Crypto import Random
import base64

class AESCipher:
    
    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key).digest()
    
    def pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, plaintext):
        plaintext = self.pad(plaintext)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(plaintext))

    def decrypt(self, ciphertext):
        ciphertext = base64.b64decode(ciphertext)
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(ciphertext[AES.block_size:])).decode('utf-8')


cipher1 = AESCipher(KEYPASS)

print cipher1.key

message = "hello this is dog"

encryption = cipher1.encrypt(message)
decryption = cipher1.decrypt(encryption)

print encryption
print decryption
