import json
from collections import namedtuple

with open('config.json', 'r') as f:
    config = json.load(f)


class CommandError(Exception): pass
class Disconnect(Exception): pass

Error = namedtuple('Error', ('message',))
