#!/usr/bin/env python3
import alpha

#Standard base 62 alphabet
def alphabet():
	return '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

#Decoder
def decode(token_str):
	return alpha.token_str_to_bytes(token_str,alphabet(),8)

#Encoder
def encode(bs):
	return alpha.bytes_to_token_str(bs,alphabet(),8)