#!/usr/bin/env python3
import getpass
import select
import struct
import time

#Gets a password from command line
def passwd():
	return getpass.getpass('Password: ')

#Checks if a fd has bytes to read
def available(conn):
	try:
		readable,writeable,errored=select.select([conn],[],[],0)
		if conn in readable:
			return True
	except Exception:
		pass
	return False

#Return current time in ms
def millis():
	return int(round(time.time()*1000))

#Packs a domain name for a dns request
#  Max name is 63 chars long.
def pack_dns_name(name):
	ret=b''
	for block in name.split('.'):
		size=len(block)
		if size<0 or size>63:
			raise Exception('Bad dns block size')
		ret+=struct.pack('>B',size)+block.encode('ascii')
	ret+=b'\x00'
	return ret

#Continually asks user for a valid-ish looking dns root
def get_dns_root():
	while True:
		root=input('Root (i.e. ".attacker.ru" without quotes): ').strip()
		if len(root.strip('.'))<=0 or root.find('..')>=0 or root[-1]=='.':
			print('This is not a valid root...')
			continue
		if root.find('.')!=0:
			print('No dot at position 0...')
			continue
		return root

#Continually asks user for a dns address
def get_dns_address(default=None):
	default_str=''
	if default!=None:
		default_str=' (press enter for "%s")'%default
	while True:
		addr=input('DNS Server%s: '%default_str).strip()
		if len(addr)<=0:
			if default:
				addr=default
			else:
				print('Need a server address...')
				continue
		return addr

#Continually asks user for a dns port
def get_dns_port():
	while True:
		port=input('DNS Port (press enter for 53): ').strip()
		try:
			if len(port)==0:
				port='53'
			port=int(port)
		except Exception:
			print('Must be an integer...')
		if port<=0 or port>65535:
			print('Must be a valid port (1-65535)...')
			continue
		return port