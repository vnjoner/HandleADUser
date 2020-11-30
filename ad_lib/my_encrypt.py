
import base64, random, hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto import Random


class AESCipher(object):

	def __init__(self, key):
		self.bs = 32
		self.key = hashlib.sha256(key.encode()).digest()

	def encrypt(self, raw):
		raw = self._pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw.encode()))

	def decrypt(self, enc):
		enc = base64.b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

	def _pad(self, s):
		return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

	@staticmethod
	def _unpad(s):
		return s[:-ord(s[len(s)-1:])]


class RSACipher(object):

	def __init__(self, pub_key_file, pri_key_file):
		self.pub_key = RSA.import_key(open(pub_key_file).read())
		self.pri_key = RSA.import_key(open(pri_key_file).read())

	def encrypt_data(self, data):
		cipher_rsa = PKCS1_OAEP.new(self.pub_key)
		encode_data = cipher_rsa.encrypt(data)
		return base64.b64encode(encode_data)
	
	def decrypt_data(self, encode_data):
		enc = base64.b64decode(encode_data)
		cipher_rsa = PKCS1_OAEP.new(self.pri_key)
		data = cipher_rsa.decrypt(enc).decode("utf-8")
		return data
