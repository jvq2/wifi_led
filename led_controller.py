from __future__ import print_function
import argparse
import socket


class LEDController():

	def __init__(self, verbose=False):
		self.verbose = verbose
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

	def _log(self, *args):
		if self.verbose:
			print(*args)

	def _str_to_int_list(self, byte_str):
		return [ord(char) for char in byte_str]

	def _int_list_to_str(self, int_list):
		return ''.join(chr(i) for i in int_list)

	def _send(self, hex_str):
		self._log('Sending:', hex_str)
		hex_str = self._int_list_to_str(hex_str)
		self._socket.send(hex_str)
		# self._socket.send(hex_str.decode('hex'))

	def _receive(self):
		data = b''

		while True:
			part = self._socket.recv(1024)
			data += part

			if len(part) < 1024:
				break

		self._log('Received', repr(data))
		return data

	def _calc_str_checksum(self, hex_str):
		total = 0
		for i in range(0, len(hex_str), 2):
			total += int(hex_str[i:i+2], 16)
		return hex(total)[-2:]

	def _calc_checksum(self, int_list):
		return int(hex(sum(int_list))[-2:], 16)

	def _response_is_valid(self, data):
		# checksum = int(hex(sum(data[:-1]))[-2:], 16)
		checksum = self._calc_checksum(data[:-1])
		return checksum == data[-1]

	def _parse_status(self, data):
		# \x81\x04$a\x01\x08\xf1\xf1\xf1\xff\x04\x00\x00\xe9 - off
		# \x81\x04#a\x01\x08\xf1\xf1\xf1\xff\x04\x00\x00\xe8 - on
		self._on = data[2] == 35
		self._r = data[6]
		self._g = data[7]
		self._b = data[8]
		self._w = data[9]

	def _parse_response(self, data):
		if data == '0':
			self._do_nothing(data)
			return

		data = self._str_to_int_list(data)
		if not self._response_is_valid(data):
			self._log('invalid response checksum')
			return

		prefix = data[0]

		command = self._commands.get(prefix, self._do_nothing)
		command(data)

	def _do_nothing(self, data=None):
		self._log('Unrecognised response: {}'.format(data))

	def connect(self, host, port):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.connect((host, port))
		self.get_status()

	def close(self):
		if not self._socket:
			self._log('No connection open to close')
			return

		self._socket.close()

	def send_cmd(self, hex_str):
		# hex_str += self._calc_str_checksum(hex_str)
		hex_str += [self._calc_checksum(hex_str)]
		self._send(hex_str)
		data = self._receive()
		self._parse_response(data)
		return data

	def get_status(self):
		# return self.send_cmd('818a8b')
		return self.send_cmd([129, 138, 139])

	def power_on(self):
		# return self.send_cmd('71230f')
		return self.send_cmd([113, 35, 15])
		# response is f0:71:23:84
		# [240, 113, 35, 132]

	def power_off(self):
		# return self.send_cmd('71240f')
		return self.send_cmd([113, 36, 15])
		# response is f0:71:24:85
		# [240, 113, 36, 133]

	def rgbw(self, r, g, b, w):
		# hex_str = '31{r}{g}{b}{w}000f'.format(r=r, g=g, b=b, w=w)
		# return self.send_cmd(hex_str)
		return self.send_cmd([49, r, g, b, w, 0, 15])
		# response 30


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--host', default='192.168.1.147', help='The host name or ip address of the light')
	parser.add_argument('--port', type=int, default=5577, help='The port number')
	parser.add_argument('--verbose', action='store_true', help='Be noisier')

	subparsers = parser.add_subparsers(dest="cmd", help='help for subcommand')

	rgbw_parser = subparsers.add_parser('rgbw', help='rgbw help')
	rgbw_parser.add_argument('r', type=int, default=None, help='Numerical red value between 0 and 255')
	rgbw_parser.add_argument('g', type=int, default=None, help='Numerical green value between 0 and 255')
	rgbw_parser.add_argument('b', type=int, default=None, help='Numerical blue value between 0 and 255')
	rgbw_parser.add_argument('w', type=int, default=None, nargs='?', help='Numerical white value between 0 and 255')
	rgbw_parser.set_defaults(func=parse_rgbw)

	state_parser = subparsers.add_parser('status', help='status help')
	state_parser.set_defaults(func=parse_status)

	on_parser = subparsers.add_parser('on', help='on help')
	on_parser.set_defaults(func=parse_on)

	off_parser = subparsers.add_parser('off', help='off help')
	off_parser.set_defaults(func=parse_off)

	toggle_parser = subparsers.add_parser('toggle', help='toggle help')
	toggle_parser.set_defaults(func=parse_toggle)

	return parser.parse_args()


def parse_rgbw(ctrl, args):
	r = args.r
	g = args.g
	b = args.b
	w = args.w

	if r is None:
		r = ctrl.r

	if g is None:
		g = ctrl.g

	if b is None:
		b = ctrl.b

	if w is None:
		w = ctrl.w

	print(r)
	print(g)
	print(b)
	print(w)
	ctrl.rgbw(r, g, b, w)


def parse_status(ctrl, args):
	status = ctrl.on and 'on' or 'off'
	print('{}\t{}\t{}\t{}\t{}'.format(status, ctrl.r, ctrl.g, ctrl.b, ctrl.w))


def parse_on(ctrl, args):
	ctrl.power_on()


def parse_off(ctrl, args):
	ctrl.power_off()


def parse_toggle(ctrl, args):
	if ctrl.on:
		ctrl.power_off()
	else:
		ctrl.power_on()


if __name__ == '__main__':
	args = parse_args()

	controller = LEDController(verbose=args.verbose)
	controller.connect(args.host, args.port)

	args.func(controller, args)

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
