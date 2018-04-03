import argparse
import socket


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

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('r', type=int, default=None, nargs='?', help='Numerical red value between 0 and 255')
	parser.add_argument('g', type=int, default=None, nargs='?', help='Numerical green value between 0 and 255')
	parser.add_argument('b', type=int, default=None, nargs='?', help='Numerical blue value between 0 and 255')
	parser.add_argument('w', type=int, default=None, nargs='?', help='Numerical white value between 0 and 255')
	parser.add_argument('--on', action='store_true', help='Turns the light on')
	parser.add_argument('--off', action='store_true', help='Turns the light off')
	parser.add_argument('--toggle', action='store_true', help='Switches the light on if it\'s off and off if it\'s on')
	parser.add_argument('--get', action='store_true', help='Reads out the current light status')
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_args()
	controller = LEDController()

	controller.connect('192.168.1.147', 5577)

	if args.on:
		controller.power_on()

	if args.off:
		controller.power_off()

	if args.get:
		status = controller.on and 'on' or 'off'
		print '{}\t{}\t{}\t{}\t{}'.format(
			status, controller.r, controller.g, controller.b, controller.w)

	if args.toggle:
		if controller.on:
			controller.power_off()
		else:
			controller.power_on()

	if args.r is not None or args.g is not None or args.b is not None or args.w is not None:
		new_r = args.r or controller.r
		new_g = args.g or controller.g
		new_b = args.b or controller.b
		new_w = args.w or controller.w
		controller.rgbw(new_r, new_g, new_b, new_w)

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
