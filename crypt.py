#!/usr/bin/env python3
from Crypto.Cipher import AES
import hashlib

#Byte size of aes128
def bs():
	return 16

#Standard padding
def pad(data):
	pad_len=bs()-(len(data)%bs())
	return data+bytes([pad_len])*pad_len

#Unpadder for above padding
def unpad(data):
	pad_len=int(data[-1])
	return data[:len(data)-pad_len]

#Key derivation (take sha256 of key and then overlap the two 16 byte halves via xor)
def calc_key(key):
	new_key=b''

	#Get sha256 hash
	k2=hashlib.sha256(key.encode()).digest()

	#Split sha256 into halves
	k1=k2[:bs()]
	k2=k2[bs():]

	#Overlap sha256 halves
	for ii in range(len(k1)):
		new_key+=bytes([k1[ii]^k2[ii]])

	#Return new key
	return new_key

#Encrypt function
#  key is a sstr
#  iv is bytes of len==bs()
#  plain is bytes to encrypt
def en(key,iv,plain):
	return AES.new(calc_key(key),AES.MODE_CBC,iv).encrypt(pad(plain))

#Decrypt function
#  key is a sstr
#  iv is bytes of len==bs()
#  cipher is bytes to decrypt
def de(key,iv,cipher):
	return unpad(AES.new(calc_key(key),AES.MODE_CBC,iv).decrypt(cipher))
