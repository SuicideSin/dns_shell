#!/usr/bin/env python3
import b62
import crypt
from Crypto import Random
import struct

def cs_en_block_size():
	return 20

def sc_en_block_size():
	return 108

#Helper to increment a nonce with wrap-around
def inc_nonce(nonce):
	return (nonce+1)%256

class session_t:

	#Constructor
	def __init__(self,session,key):
		self.session=session
		self.key=key
		self.tx_nonce=0

	#Pack data into block size packets
	def pack(self,data,block_size,encoder=b62.encode):

		#Packets to return
		packets=[]

		#Keep encoding until all bytes are encoded
		while len(data)>0:

			#Calculate iv
			iv_byte=Random.get_random_bytes(1)
			iv_str=iv_byte*crypt.bs()

			#Calculate nonce
			nonce_byte=struct.pack('>B',self.tx_nonce)

			#Session byte
			session_byte=struct.pack('<B',self.session)

			#Encrypt block
			block=data[:block_size]
			packet=iv_byte+crypt.en(self.key,iv_str,iv_byte+session_byte+nonce_byte+block)

			#Encode
			packet=encoder(packet)

			#Add block to packets
			packets.append(packet)

			#Increment nonce (single byte with wrap around)
			self.tx_nonce=inc_nonce(self.tx_nonce)

			#On to the next block
			data=data[block_size:]

		#Return the packets
		return packets

	#Unpack packet
	def unpack(self,packet,decoder=b62.decode):

		#Decode
		#try:
		data=decoder(packet)
		#except Exception:
		#	raise Exception('Packet isn\'t encoded!')

		#Packet is always at least 1 byte for nonce
		if len(data)<1:
			raise Exception('Bad packet!')

		#Calculate nonce
		iv_byte=data[:1]
		iv_str=iv_byte*crypt.bs()

		#Session byte
		session_byte=struct.pack('<B',self.session)

		#Get decrypted data
		try:
			data=crypt.de(self.key,iv_str,data[1:])
		except Exception:
			raise Exception('Bad decrypt!')

		#Check iv
		if len(data)<1 or data[:1]!=iv_byte:
			raise Exception('Bad iv!')

		#Check session
		if len(data)<2 or data[1:2]!=session_byte:
			raise Exception('Bad session!')

		#Return rx_nonce,data
		return data[2],data[3:]
