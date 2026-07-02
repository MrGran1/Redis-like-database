
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
        # Parse a request from the client into it's component parts.
        pass
        

    def write_response(self, socket_file, data):
        # Serialize the response data and send it to the client.
        pass
