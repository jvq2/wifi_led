import socket
import time


HOST = '192.168.1.147'
PORT = 5577

def connect(host, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, port))
	return sock

def send(s, hex_str):
	s.send(hex_str.decode('hex'))

def calc_checksum(hex_str):
	total = 0
	for i in range(0, len(hex_str), 2):
		total += int(hex_str[i:i+2], 16)
	return hex(total)[-2:]

def cmd(s, hex_str):
	hex_str += calc_checksum(hex_str)
	send(s, hex_str)
	data = s.recv(1024)
	print 'Received', repr(data)
	return data

def hello(s):
	return cmd(s, '818a8b')

def on(s):
	return cmd(s, '71230f')
	# response is f0:71:23:84

def off(s):
	return cmd(s, '71240f')
	# response is f0:71:24:85

def rgbw(sock, r, g, b, w):
	hx = '31{r}{g}{b}{w}000f'.format(r=r, g=g, b=b, w=w)
	return cmd(sock, hx)
	# response 30

s = connect(HOST, PORT)

# Say hello. This same greeting seems to be used for every connection
# cmd('818a8b96')
hello(s)

# setting a color
# cmd('31f1f1f1ff000f12')


# on
on(s)

# time.sleep(5)

# off
# cmd('71240fa4')
# off(s)

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