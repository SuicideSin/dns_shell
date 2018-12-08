#!/usr/bin/env python3

#Encodes a base 10 integer to a string representation with the given alphabet.
#  To pad strings to a fixed size you can put the max b10 value in pad_b10_max.
#  For example, to pad a values with 256 options (aka, a byte), you would put 256 here.
#  https://stackoverflow.com/questions/1119722/base-62-conversion
def b10_to_token(b10,alphabet,pad_b10_max=0):
	token=''
	base=len(alphabet)

	#Encode
	while b10>0:
		b10,rem=divmod(b10,base)
		token=alphabet[rem]+token

	#Got a zero
	if len(token)==0:
		token=alphabet[0]

	#Add padding if specified
	if pad_b10_max>0:
		pad_width=len(b10_to_token(pad_b10_max-1,alphabet,0))
		while len(token)<pad_width:
			token=alphabet[0]+token

	return token

#Takes a token and returns a base 10 integer based on the given alphabet (works with or without padding).
#  https://stackoverflow.com/questions/1119722/base-62-conversion
def token_to_b10(token,alphabet):
	size=len(token)
	base=len(alphabet)
	b10=0
	place=0
	for ch in token:
		power=(size-place-1)
		b10+=alphabet.index(ch)*(base**power)
		place+=1
	return b10

#Takes a section of bytes, turns them into an integer, returns the base 10 value of them.
#  Warning: Be careful with the width of said bytes! No clue what a width>8 will yield!
def bytes_to_b10(bs):
	return int.from_bytes(bs,'big')

#Takes a block of bytes, turns them into a base 10 integer, and returns a padded token for a given alphabet.
#  Warning: Be careful with the width of said bytes! No clue what a width>8 will yield!
def bytes_to_token(bs,alphabet):

	#Get base 10 representation of the bytes
	b10=bytes_to_b10(bs)

	#Get the max value of the given block size (will pad the token with zeros)
	b10_max=bytes_to_b10(b'\xff'*len(bs))

	#Convert to token and return
	return b10_to_token(b10,alphabet,b10_max)

#Converts to bytes to a token string with the given alphabet.
#  Warning: Be careful with the width of said bytes! No clue what a width>8 will yield!
def bytes_to_token_str(bs,alphabet,block_width=8):
	size=len(bs)
	ptr=0
	token_str=''

	#Go through all blocks
	while ptr<size:

		#Extract the block
		block=bs[ptr:ptr+block_width]

		#Add to token string
		token_str+=bytes_to_token(block,alphabet)

		#Next block
		ptr+=block_width

	#Return the token string
	return token_str

#Converts to bytes to a token string with the given alphabet.
#  Warning: Be careful with the width of said bytes! No clue what a width>8 will yield!
def token_str_to_bytes(token_str,alphabet,block_width=8):
	size=len(token_str)
	ptr=0
	bs=b''

	#Get the max value of the given block size (will pad the token with zeros)
	b10_max=bytes_to_b10(b'\xff'*block_width)

	#Get the width of the max value of the given block size encoded in the alphabet
	enc_width=len(b10_to_token(b10_max,alphabet,b10_max))

	#Go through the tokens in the token string
	while ptr<size:

		#Grab the token
		token=token_str[ptr:ptr+enc_width]

		#Convert token to base 10
		b10=token_to_b10(token,alphabet)

		#Get the length of the token
		token_length=len(token)

		#Token length is less than a full block token length -> last block
		if token_length<enc_width:

			#Get the max value representable by the alphabet with the a token of the same length
			max_token_val=len(alphabet)**token_length

			#Find out how many blocks we have
			while block_width>0:

				#We already know we have too many, so decrement before check
				block_width-=1

				#Get the new max value
				b10_max=bytes_to_b10(b'\xff'*block_width)

				#If we crossed the boundary, we found the real number of blocks - break
				if b10_max<max_token_val:
					break

		#Decode base 10 to base 256 (aka bytes)
		bs+=b10.to_bytes(block_width,'big')

		#Next token
		ptr+=enc_width

	#Return bytes
	return bs

if __name__=='__main__':

	#Alphabet
	alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

	#Initial string
	bs=b'\x00\x00\x00\x00\x00\x00\x00\x00hello th\x00\x00\x00\x00\x00\x00\x00\x00partner\x00\x00'
	print('ini(%d)=%s'%(len(bs),bs))

	#Encode
	enc=bytes_to_token_str(bs,alphabet,8)
	print('enc=%s'%enc)

	#Decode
	dec=token_str_to_bytes(enc,alphabet,8)
	print('dec(%d)=%s'%(len(dec),dec))

	if bs!=dec:
		print('ERROR')
	else:
		print('SUCCESS')