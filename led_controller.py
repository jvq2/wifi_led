import socket
import time


class LEDController():

	def __init__(self):
		self._socket = None
		self._commands = {129: self._parse_status}
		self._on = False
		self._r = 0
		self._g = 0
		self._b = 0
		self._w = 0

	@property
	def on(self):
		return self._on

	@property
	def r(self):
		return self._r

	@property
	def g(self):
		return self._g

	@property
	def b(self):
		return self._b

	@property
	def w(self):
		return self._w

	def _send(self, hex_str):
		self._socket.send(hex_str.decode('hex'))

	def _receive(self):
		data = b''

		while True:
			part = self._socket.recv(1024)
			data += part

			if len(part) < 1024:
				break

		print 'Received', repr(data)
		return data

	def _calc_str_checksum(self, hex_str):
		total = 0
		for i in range(0, len(hex_str), 2):
			total += int(hex_str[i:i+2], 16)
		return hex(total)[-2:]

	def _response_is_valid(self, data):
		checksum = int(hex(sum(data[:-1]))[-2:], 16)
		return checksum == data[-1]

	def _parse_status(self, data):
		# \x81\x04$a\x01\x08\xf1\xf1\xf1\xff\x04\x00\x00\xe9 - off
		# \x81\x04#a\x01\x08\xf1\xf1\xf1\xff\x04\x00\x00\xe8 - on
		self._on = data[2] == 35
		self._r = data[6]
		self._g = data[7]
		self._b = data[8]
		self._w = data[9]

	def _byte_str_to_list(self, data):
		return [ord(char) for char in data]

	def _parse_response(self, data):
		data = self._byte_str_to_list(data)
		if not self._response_is_valid(data):
			print 'invalid response checksum'
			return

		prefix = data[0]

		command = self._commands.get(prefix, self._do_nothing)
		command(data)

	def _do_nothing(self, data=None):
		print 'Unrecognised response: {}'.format(data)

	def connect(self, host, port):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.connect((host, port))
		self.get_status()

	def close(self):
		self._socket.close()

	def send_cmd(self, hex_str):
		hex_str += self._calc_str_checksum(hex_str)
		self._send(hex_str)
		data = self._receive()
		self._parse_response(data)
		return data

	def get_status(self):
		return self.send_cmd('818a8b')

	def power_on(self):
		return self.send_cmd('71230f')
		# response is f0:71:23:84
		# [240, 113, 35, 132]

	def power_off(self):
		return self.send_cmd('71240f')
		# response is f0:71:24:85
		# [240, 113, 36, 133]

	def rgbw(self, r, g, b, w):
		hex_str = '31{r}{g}{b}{w}000f'.format(r=r, g=g, b=b, w=w)
		return self.send_cmd(hex_str)
		# response 30


if __name__ == '__main__':
	controller = LEDController()

	controller.connect('192.168.1.147', 5577)

	controller.power_on()
	# time.sleep(5)
	# controller.power_off()

	controller.close()

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
