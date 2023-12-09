from collections import namedtuple

from gevent.pool import Pool
from gevent.server import StreamServer

Error = namedtuple('Error', ('message',))


class CommandError(Exception): pass


class Disconnect(Exception): pass


def custom_split2(data):
    data = data.split('\r\n')
    res_data = []
    data = data[1:-1]
    arr_len = len(data)
    i = 0
    while i < arr_len:
        str_val = data[i]
        if data[i].startswith('$') and data[i][1].isdigit():
            str_val = data[i] + data[i + 1]
            i += 1
        res_data.append(str_val)
        i += 1
    return res_data


def custom_split(data):
    data = data.split('\r\n')
    res_data = []
    arr_len = int(data[0])
    data = data[1:]
    i = 0
    while i < arr_len:
        str_val = data[i]
        if '$' in data[i]:
            str_val = data[i] + data[i + 1]
            res_data.append(str_val)
            i += 1
        res_data.append(str_val)
        i += 1
    return res_data


class ProtocolHandler:
    def __init__(self):
        self._handler = {
            '+': self.handle_string,
            '-': self.handle_error,
            ':': self.handle_integer,
            '$': self.handle_bytes,
            '*': self.handle_array,
            '%': self.handle_dict,
            '_': self.handle_null,
            '#': self.handle_boolean,
            ',': self.handle_float,
            '(': self.handle_integer
        }

    def handle_request(self, socket_file):
        pass

    def handle_response(self, socket_file, data):
        pass

    def handle_string(self, data):
        return str(data.readline().strip('\r\n'))

    def handle_null(self, data=None):
        return None

    def handle_boolean(self, data):
        return True if data.readline().strip('\r\n') == 't' else False

    def handle_float(self, data):
        return float(data.readline().strip('\r\n'))

    def handle_integer(self, data):
        return int(data.readline().strip('\r\n'))

    def handle_error(self, data):
        return Error(data.readline().strip('\r\n'))

    def handle_bytes(self, data):
        return data.readline().strip('\r\n')[1:]

    def handle_array(self, data):
        return custom_split(data)


class Server:
    def __init__(self, host='127.0.0.1', port=5835, max_clients=10):
        self._pool = Pool(max_clients)
        self._socket = StreamServer((host, port), handle=self.connection_handler, spawn=self._pool)
        self._protocol = ProtocolHandler()

    def connection_handler(self, conn, socket_file):
        socket_file = conn.makefile('rwb')
        while True:
            try:
                data = self._protocol.handle_request(socket_file)
            except Disconnect:
                break
            try:
                resp = self.get_response(data)
            except CommandError as exc:
                resp = Error(exc.args[0])
            self._protocol.handle_response(socket_file, resp)

    def get_response(self, data):
        pass

    def run(self):
        self._socket.serve_forever()
