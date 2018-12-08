#!/usr/bin/env python3
import termios
import tty
import util

#Nonblocking console handler
class nonblock_t:

	#Constructor
	def __init__(self):
		self.line=b''
		self.fd_r=None
		self.fd_w=None
		self.old_settings=None

	#Begin parsing on fiven fd_r and fd_w
	def begin(self,fd_r,fd_w):
		self.line=b''
		self.fd_r=fd_r
		self.fd_w=fd_w
		self.old_settings=termios.tcgetattr(self.fd_r)
		tty.setcbreak(self.fd_r.fileno())

	#Stop parsing - reset read fd to original settings
	def end(self):
		self.line=b''
		if self.fd_r and self.old_settings:
			termios.tcsetattr(self.fd_r,termios.TCSADRAIN,self.old_settings)
			self.fd_r=None
			self.fd_w=None
			self.old_settings=None

	#Parse data from console
	#  Echo is on
	#  Returns a byte string of lines
	def loop(self):
		lines=b''

		#Keep grabbing bytes
		while util.available(self.fd_r):

			#Grab the types char and byte equivalent
			c=self.fd_r.read(1)
			b=c.encode('utf-8')

			#Backspace
			if b==b'\x7f':
				self.line=self.line[:-1]
				self.fd_w.write('\b \b')
				self.fd_w.flush()

			#Anything else
			else:

				#Echo
				self.fd_w.write(c)
				self.fd_w.flush()

				#Append to line
				self.line+=b

				#Newline - add line to lines and reset
				if b==b'\n':
					lines+=self.line
					self.line=b''

		return lines

if __name__=='__main__':
	import sys
	import time

	#Open a file for logging
	f=open('log.txt','wb')

	#Make a console
	cc=nonblock_t()

	try:
		#Begin non-blocking console
		cc.begin(sys.stdin,sys.stdout)

		#Get lines from console and write them to log with quotes
		while True:
			for line in cc.loop():
				f.write(b'"'+line+b'"\n')
				f.flush()
			time.sleep(0.01)

	#End console and close log file
	finally:
		cc.end()
		f.close()
