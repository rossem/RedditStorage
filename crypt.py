from base64 import b64decode
from typing import Tuple, List, Union

import argon2.low_level
from Crypto.Cipher import AES
from argon2 import PasswordHasher, Parameters, Type


class AESCipher(object):

    hasher = PasswordHasher()
    """Mainly for internal use. So we don't have to remake this object every encryption/decryption"""

    def __init__(self, key: str):
        """
        Constructor for an AESCipher object
        :param key: The password to use as a key
        """
        # argon2 outputs a single string with all parameters delimited by a '$'
        self.argon2 = self.hasher.hash(key)
        """The argon2 parameters, salt, and hash, as output by PasswordHasher"""

        self.argon2params, self.salt, self.hash = self.extract_parameters(self.argon2)

        # argon2-cffi encodes the values in base64, so we decode it here to get our byte values
        # And we need to add padding '=' because reasons b64 needs that number of chars
        self.key: bytes = b64decode(self.hash + '=')  # Should be 32 bytes long
        """The key for encrypting, in raw byte form; 32 bytes long"""
        self.secret = key
        """The password hashed to generate the key"""

    # encrypts a file and returns a comment to be posted
    def encrypt_file(self, file_path: str) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypts a file and returns the ciphertext and associated MAC
        :param file_path: The path to the file to encrypt
        :return: A list containing [ciphertext, MAC, nonce]
        """
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext = b''
        with open(file_path, 'rb') as fo:
            while True:
                plaintext = fo.read(20000)
                if not plaintext:
                    break
                ciphertext += cipher.encrypt(plaintext)
        mac = cipher.digest()
        # comment = enc.decode('ISO-8859-1').encode('ascii')
        print('\nEncryption info:\nMAC: ', mac, '\nSalt: ', self.salt, '\nKey: ', self.hash, '\nSecret: ',
              self.secret)
        return ciphertext, mac, cipher.nonce

        # takes in a comment to be posted and decrypts it into a file

    _STR_TYPE_TO_TYPE = {"Type.ID": Type.ID, "Type.I": Type.I, "Type.D": Type.D}

    def decrypt_to_file(self, encrypt_items: Tuple[bytes, List[str]], file_path: str):
        """
        Decrypts a file encrypted in AES-GCM and outputs the result to the given filepath
        :parameter encrypt_items: A Tuple containing [ciphertext, argon2 parameters]
        :parameter file_path: The file path to output the decrypted file to
        """
        ciphertext = encrypt_items[0]
        mac = encrypt_items[1][0]
        salt = encrypt_items[1][1]
        nonce = encrypt_items[1][9]
        # ciphertext = comment.decode('ascii').encode('ISO-8859-1')
        # Format is MAC$salt$time cost$memory cost$parallelism$hash length$salt length$argon2 type$argon2 version
        dec = self._decrypt(ciphertext, b64decode(mac), b64decode(salt), b64decode(nonce),
                            Parameters(time_cost=int(encrypt_items[1][2]),
                                       memory_cost=int(encrypt_items[1][3]),
                                       parallelism=int(encrypt_items[1][4]),
                                       hash_len=int(encrypt_items[1][5]),
                                       salt_len=int(encrypt_items[1][6]),
                                       type=self._STR_TYPE_TO_TYPE[encrypt_items[1][7]],
                                       version=int(encrypt_items[1][8])
                                       )
                            )
        with open(file_path, 'wb') as fo:
            fo.write(dec)

    # decrypts ciphertexts
    def _decrypt(self, ciphertext: bytes, mac_tag: bytes, salt: bytes, nonce: bytes,
                 argon2_params: Parameters) -> bytes:
        """
        Returns the decrypted ciphertext
        :param ciphertext: The ciphertext to decrypt
        :param mac_tag: The MAC for the ciphertext
        :param salt: The salt used for the key
        :param nonce: The nonce used by the AES algorithm
        :return: The decrypted information
        """
        cipher = AES.new(
            b64decode(argon2.low_level.hash_secret(self.secret.encode('utf-8'), salt,
                                                   argon2_params.time_cost, argon2_params.memory_cost,
                                                   argon2_params.parallelism, argon2_params.hash_len,
                                                   argon2_params.type, argon2_params.version
                                                   ).decode('utf-8').split('$')[5] + '='
                      ),
            AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, mac_tag)

    _NAME_TO_TYPE = {"argon2id": Type.ID, "argon2i": Type.I, "argon2d": Type.D}
    """Dictionary quick translation of an argon2 type to appropriate enum"""

    @classmethod
    def extract_parameters(cls, argon2item: str) -> List[Union[Parameters, str]]:
        """
        Extracts argon2 parameters and returns the salt and hash
        :param argon2item: The argon2 item returned from using argon2 hashing (i.e., argon2.PassswordHasher)
        :return: A list containing [argon2 parameters, salt, hash]
        """
        parts = argon2item.split("$")

        # Backwards compatibility for Argon v1.2 hashes
        if len(parts) == 5:
            parts.insert(2, "v=18")

        argon2_type = cls._NAME_TO_TYPE[parts[1]]

        kvs = {
            k: int(v)
            for k, v in (
                s.split("=") for s in [parts[2]] + parts[3].split(",")
            )
        }

        return [Parameters(
            type=argon2_type,
            salt_len=cls._decoded_str_len(len(parts[4])),
            hash_len=cls._decoded_str_len(len(parts[5])),
            version=kvs["v"],
            time_cost=kvs["t"],
            memory_cost=kvs["m"],
            parallelism=kvs["p"],
        ), parts[4], parts[5]]

    @classmethod
    def _decoded_str_len(cls, str_len: int) -> int:
        """
        Compute how long an encoded string of length *l* becomes.
        :param str_len Length of encoded string
        :return Length of decoded string
        """
        rem = str_len % 4

        if rem == 3:
            last_group_len = 2
        elif rem == 2:
            last_group_len = 1
        else:
            last_group_len = 0

        return str_len // 4 * 3 + last_group_len
