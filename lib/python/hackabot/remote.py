"""Listen for remote commands"""

import os

from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory

from hackabot.protocol import HBLineProtocol
from hackabot import conf, log

_listen = False

def init():
    global _listen

    if conf.find('listen') is not None:
        _listen = True

def listen():
    if _listen:
        sock = "%s/sock" % conf.get('root')

        try:
            os.unlink(sock)
            log.warn("Removed an old socket: %s" % sock)
        except OSError:
            pass

        reactor.listenUNIX(sock, HBRemoteControl())

class HBRemoteControl(ServerFactory):
    """Remote Control connection factory"""

    protocol = HBLineProtocol
    noisy = False
