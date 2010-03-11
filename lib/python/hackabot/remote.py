"""Listen for remote commands"""

import os

from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory

from hackabot.protocol import HBLineProtocol
from hackabot import log

def init(manager):
    HBRemoteControl(manager)

class HBRemoteControl(ServerFactory):
    """Remote Control connection factory"""

    protocol = HBLineProtocol
    noisy = False

    def __init__(self, manager):
        self._manager = manager

        if manager.config.find('listen') is None:
            path = "%s/sock" % manager.config.get('root')
        else:
            return

        try:
            os.unlink(path)
            log.warn("Removed an old socket: %s" % path)
        except OSError:
            pass

        reactor.listenUNIX(path, self)
