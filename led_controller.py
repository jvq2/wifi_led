import socket
import time


def send(hex_str):
	s.send(hex_str.decode('hex'))

def cmd(hex_str):
	send(hex_str)
	data = s.recv(1024)
	print 'Received', repr(data)

def hello():
	return cmd('818a8b96')

def on():
	return cmd('71230fa3')
	# response is f0:71:23:84

def off():
	return cmd('71240fa4')
	# response is f0:71:24:85

def rgbw(r, g, b, w):
	# 31:fd:fd:fd:ff:00:0f:36
	# 31:f7:f7:f7:ff:00:0f:24
	# 31:f4:f4:f4:ff:00:0f:1b
	# 31:f3:f3:f3:ff:00:0f:18
	# 31:f2:f2:f2:ff:00:0f:15
	# 31:f1:f1:f1:ff:00:0f:12
	# 31:f0:f0:f0:ff:00:0f:0f  <--- middle
	# 31:f5:f5:f5:ff:00:0f:1e
	# 31:fa:fa:fa:ff:00:0f:2d
	# 31:fe:fe:fe:ff:00:0f:39
	# 31:ff:ff:ff:ff:00:0f:3c

	# 31:06:06:06:ff:00:0f:51
	# 31:01:01:01:ff:00:0f:42
	# 31:00:00:00:ff:00:0f:3f

	# 31:fc:fc:fc:ff:00:0f:33
	# 31:fe:fe:fe:ff:00:0f:39
	# 31:fb:fb:fb:ff:00:0f:30:31:f9:f9:f9:ff:00:0f:2a   <--- wtf
	# 31:f7:f7:f7:ff:00:0f:24
	# 31:f3:f3:f3:ff:00:0f:18
	# 31:ef:ef:ef:ff:00:0f:0c
	# 31:e8:e8:e8:ff:00:0f:f7
	# 31:e7:e7:e7:ff:00:0f:f4
	# ...

	# 31:00:00:00:ff:00:0f:3f
	# 31:00:00:00:00:00:0f:40
	return cmd('31''fdfdfd''ff''000f36')
	# response 30


HOST = '192.168.1.147'    # The remote host
PORT = 5577              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Say hello. This same greeting seems to be used for every connection
# cmd('818a8b96')
hello()

# setting a color
# cmd('31f1f1f1ff000f12')


# on
on()

# time.sleep(5)

# off
# cmd('71240fa4')
# off()

s.close()
# 81:04$a:01:10:ff:ff:ff:ff:04:00:00:1b
# \x81\x04$a\x01\x10\xff\xff\xff\xff\x04\x00\x00\x1b

# 81:04:24:61:01:10:9f:18:18:7c:04:00:00:6a - hello response when off
# 10:14:12:01:1e:13:38:1c:02:00:0f:cd - hello response when on
# 10:14:12:01:1d:15:27:25:01:00:0f:c5


# \x81\x04#a\x01\x10\x7f\x7f\x7f\xff\x04\x00\x00\x9a
# \x81\x04#a\x01\x10\x7f\x7f\x7f\xff\x04\x00\x00\x9a
#                    R   G   B   W



# 81:04:24:61:01:10:9f:18:18:7c:04:00:00:6a - hello response when off
# 10:14:12:01:1e:13:37:0f:02:00:0f:bf