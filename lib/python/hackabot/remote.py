"""Listen for remote commands"""

from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory

from hackabot.protocol import HBLineProtocol
from hackabot import env, log

_listen = False

def init(config):
    global _listen

    if config.find('listen') is not None:
        _listen = True

def listen():
    if _listen:
        sock = "%s/sock" % env.HB_ROOT
        reactor.listenUNIX(sock, HBRemoteControl())

class HBRemoteControl(ServerFactory):
    """Remote Control connection factory"""

    protocol = HBLineProtocol
    noisy = False
