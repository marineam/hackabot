"""Listen for remote commands"""

import os

from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory

from hackabot.protocol import HBLineProtocol
from hackabot import log

_listen = False

def init(config):
    global _listen

    if config.find('listen') is not None:
        _listen = "%s/sock" % config.get('root')

def listen():
    if _listen:
        try:
            os.unlink(_listen)
            log.warn("Removed an old socket: %s" % _listen)
        except OSError:
            pass

        reactor.listenUNIX(_listen, HBRemoteControl())

class HBRemoteControl(ServerFactory):
    """Remote Control connection factory"""

    protocol = HBLineProtocol
    noisy = False
