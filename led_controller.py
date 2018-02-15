import socket
import time


def cmd(hex_str):
	s.send(hex_str.decode('hex'))
	data = s.recv(1024)
	print 'Received', repr(data)


def hello():
	return cmd('818a8b96')


HOST = '192.168.1.147'    # The remote host
PORT = 5577              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Say hello. This same greeting seems to be used for every connection
# cmd('818a8b96')
hello()

# setting a color
cmd('31f1f1f1ff000f12')


# on
cmd('71230fa3')

# time.sleep(5)

# off
# cmd('71240fa4')

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