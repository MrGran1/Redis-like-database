# We'll use exceptions to notify the connection-handling loop of problems.
from io import BytesIO
import logging
from utils import Disconnect, CommandError, Error
logger = logging.getLogger(__name__)
class ProtocolHandler(object):
    def __init__(self):
        self.handlers = {
            '+': self.handle_simple_string,
            '-': self.handle_error,
            ':': self.handle_integer,
            '$': self.handle_string,
            '*': self.handle_array,
            '%': self.handle_dict
            }

    def handle_request(self, socket_file):
        first_byte = socket_file.read(1).decode()
        if not first_byte:
            raise Disconnect()

        try:
            # Delegate to the appropriate handler based on the first byte.
            return self.handlers[first_byte](socket_file)
        except KeyError:
            raise CommandError('bad request')
        
    def handle_simple_string(self, socket_file):
        return socket_file.readline().decode().rstrip('\r\n')

    def handle_error(self, socket_file):
        return Error(socket_file.readline().decode().rstrip('\r\n'))

    def handle_integer(self, socket_file):
        return int(socket_file.readline().decode().rstrip('\r\n'))

    def handle_string(self, socket_file):
        # First read the length ($<length>\r\n).
        length = int((socket_file.readline().decode().rstrip('\r\n')))
        if length == -1:
            return None  # Special-case for NULLs.
        length += 2  # Include the trailing \r\n in count.
        return socket_file.read(length)[:-2]

    def handle_array(self, socket_file):
        num_elements = int((socket_file.readline().decode().rstrip('\r\n')))
        return [self.handle_request(socket_file) for _ in range(num_elements)]

    def handle_dict(self, socket_file):
        num_items = int(socket_file.readline().decode().rstrip('\r\n'))
        elements = [self.handle_request(socket_file)
                    for _ in range(num_items * 2)]
        return dict(zip(elements[::2], elements[1::2]))
        

    def write_response(self, socket_file, data):
        buf = BytesIO()
        self._write(buf, data)
        buf.seek(0)
        socket_file.write(buf.getvalue())
        socket_file.flush()

    def _write(self, buf, data):
        if isinstance(data, str):
            data = data.encode('utf-8')

        if isinstance(data, bytes):
            buf.write((f'${len(data)}\r\n').encode())
            buf.write(data)
            buf.write(b'\r\n')

        elif isinstance(data, int):
            buf.write((':%s\r\n' % data).encode())

        elif isinstance(data, Error):
            buf.write(('-%s\r\n' % data.message).encode())  ## Pas sur de ce data.message

        elif isinstance(data, (list, tuple)):
            buf.write(('*%s\r\n' % len(data)).encode())
            for item in data:
                self._write(buf, item)

        elif isinstance(data, dict):
            buf.write(('%%%s\r\n' % len(data)).encode())
            for key in data:
                self._write(buf, key)
                self._write(buf, data[key])

        elif data is None:
            buf.write('$-1\r\n')
        else:
            raise CommandError('unrecognized type: %s' % type(data))
